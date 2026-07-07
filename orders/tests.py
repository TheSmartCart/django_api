from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from enseignes.models import Enseigne, Produit, Magasin
from orders.models import Commande, ArticleCommande

User = get_user_model()

class CommandeAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='buyer1', password='password123')
        self.other_user = User.objects.create_user(username='buyer2', password='password123')

        self.client.force_authenticate(user=self.user)

        self.enseigne = Enseigne.objects.create(nom='Monoprix', statut='actif')
        self.magasin = Magasin.objects.create(
            nom='Monoprix Paris',
            adresse='10 Rue des Halles',
            code_postal='75001',
            ville='Paris',
            enseigne=self.enseigne,
            statut='actif'
        )
        self.produit_pasta = Produit.objects.create(
            nom='Pâtes Coquillettes',
            prix=1.20,
        )
        self.produit_pasta.magasins.set([self.magasin])

        self.produit_sauce = Produit.objects.create(
            nom='Sauce Tomate',
            prix=2.50,
        )
        self.produit_sauce.magasins.set([self.magasin])

    def test_list_commandes_only_returns_own_orders(self):
        cmd_user = Commande.objects.create(utilisateur=self.user, magasin=self.magasin, statut='en_attente')
        cmd_other = Commande.objects.create(utilisateur=self.other_user, magasin=self.magasin, statut='en_attente')

        url = reverse('commandes-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], cmd_user.id)

    def test_create_new_order_en_attente_success(self):
        url = reverse('commandes-list')
        data = {
            'magasin': self.magasin.id,
            'statut': 'en_attente',
            'articles': [
                {'produit': self.produit_pasta.id, 'quantite': 3},
                {'produit': self.produit_sauce.id, 'quantite': 1}
            ]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['statut'], 'en_attente')
        self.assertEqual(len(response.data['articles']), 2)

        commande = Commande.objects.get(id=response.data['id'])
        self.assertEqual(commande.utilisateur, self.user)
        self.assertEqual(commande.magasin, self.magasin)
        self.assertEqual(commande.articles.count(), 2)

        self.assertEqual(float(response.data['prix_total']), 6.10)

    def test_create_order_modifies_existing_en_attente(self):
        existing_cmd = Commande.objects.create(utilisateur=self.user, magasin=self.magasin, statut='en_attente')
        ArticleCommande.objects.create(commande=existing_cmd, produit=self.produit_pasta, quantite=10, prix_unitaire=1.20)

        url = reverse('commandes-list')
        data = {
            'magasin': self.magasin.id,
            'statut': 'en_attente',
            'articles': [
                {'produit': self.produit_sauce.id, 'quantite': 2}
            ]
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], existing_cmd.id)

        existing_cmd.refresh_from_db()
        self.assertEqual(existing_cmd.articles.count(), 1)
        self.assertEqual(existing_cmd.articles.first().produit, self.produit_sauce)
        self.assertEqual(existing_cmd.articles.first().quantite, 2)

    def test_create_order_non_en_attente_no_existing_fails(self):
        url = reverse('commandes-list')
        data = {
            'magasin': self.magasin.id,
            'statut': 'en_preparation',
            'articles': [
                {'produit': self.produit_pasta.id, 'quantite': 1}
            ]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_create_order_returns_existing_when_preparation_or_prete_with_same_articles(self):
        existing_cmd = Commande.objects.create(utilisateur=self.user, magasin=self.magasin, statut='en_preparation')
        ArticleCommande.objects.create(commande=existing_cmd, produit=self.produit_pasta, quantite=2, prix_unitaire=1.20)

        url = reverse('commandes-list')
        data = {
            'magasin': self.magasin.id,
            'statut': 'en_attente',
            'articles': [
                {'produit': self.produit_pasta.id, 'quantite': 2}
            ]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], existing_cmd.id)
        self.assertEqual(response.data['statut'], 'en_preparation')

    def test_put_method_not_allowed(self):
        cmd = Commande.objects.create(utilisateur=self.user, magasin=self.magasin, statut='en_attente')
        url = reverse('commandes-detail', kwargs={'pk': cmd.id})
        response = self.client.put(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_patch_order_only_allowed_for_en_attente(self):
        cmd = Commande.objects.create(utilisateur=self.user, magasin=self.magasin, statut='prete')
        url = reverse('commandes-detail', kwargs={'pk': cmd.id})
        data = {'statut': 'recuperee'}

        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Seules les commandes', response.data['error'])

    def test_patch_order_invalid_transition_fails(self):
        cmd = Commande.objects.create(utilisateur=self.user, magasin=self.magasin, statut='en_attente')
        url = reverse('commandes-detail', kwargs={'pk': cmd.id})
        data = {'statut': 'recuperee'}

        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Transition de', response.data['error'])

    def test_patch_order_valid_transition_and_articles_recreated(self):
        cmd = Commande.objects.create(utilisateur=self.user, magasin=self.magasin, statut='en_attente')
        ArticleCommande.objects.create(commande=cmd, produit=self.produit_pasta, quantite=1, prix_unitaire=1.20)

        url = reverse('commandes-detail', kwargs={'pk': cmd.id})
        data = {
            'statut': 'en_preparation',
            'articles': [
                {'produit': self.produit_sauce.id, 'quantite': 5}
            ]
        }

        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['statut'], 'en_preparation')
        self.assertEqual(len(response.data['articles']), 1)
        self.assertEqual(response.data['articles'][0]['produit']['id'], self.produit_sauce.id)

        cmd.refresh_from_db()
        self.assertEqual(cmd.statut, 'en_preparation')
        self.assertEqual(cmd.articles.count(), 1)
        self.assertEqual(cmd.articles.first().produit, self.produit_sauce)

    def test_modifier_statut_success(self):
        cmd = Commande.objects.create(utilisateur=self.user, magasin=self.magasin, statut='en_attente')
        url = reverse('commandes-modifier-statut', kwargs={'pk': cmd.id})

        response = self.client.patch(url, {'statut': 'en_preparation'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['statut'], 'en_preparation')

        cmd.refresh_from_db()
        self.assertEqual(cmd.statut, 'en_preparation')

    def test_modifier_statut_invalid_transition_fails(self):
        cmd = Commande.objects.create(utilisateur=self.user, magasin=self.magasin, statut='prete')
        url = reverse('commandes-modifier-statut', kwargs={'pk': cmd.id})

        response = self.client.patch(url, {'statut': 'en_preparation'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Transition de', response.data['error'])

    def test_en_attente_par_magasin_success(self):
        cmd = Commande.objects.create(utilisateur=self.user, magasin=self.magasin, statut='en_attente')
        url = reverse('commandes-en-attente-par-magasin', kwargs={'magasin_id': self.magasin.id})

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], cmd.id)

    def test_en_attente_par_magasin_not_found(self):
        url = reverse('commandes-en-attente-par-magasin', kwargs={'magasin_id': self.magasin.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_cancel_order_via_delete_success(self):
        cmd = Commande.objects.create(utilisateur=self.user, magasin=self.magasin, statut='en_attente')
        url = reverse('commandes-detail', kwargs={'pk': cmd.id})

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Commande annulée avec succès.')

        cmd.refresh_from_db()
        self.assertEqual(cmd.statut, 'annulee')

    def test_cancel_already_cancelled_fails(self):
        cmd = Commande.objects.create(utilisateur=self.user, magasin=self.magasin, statut='annulee')
        url = reverse('commandes-detail', kwargs={'pk': cmd.id})

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('déjà annulée', response.data['error'])

    def test_cancel_recuperee_fails(self):
        cmd = Commande.objects.create(utilisateur=self.user, magasin=self.magasin, statut='recuperee')
        url = reverse('commandes-detail', kwargs={'pk': cmd.id})

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('récupérée ne peut pas être annulée', response.data['error'])

    def test_retrieve_commande_uses_detail_serializer(self):
        cmd = Commande.objects.create(utilisateur=self.user, magasin=self.magasin, statut='en_attente')
        url = reverse('commandes-detail', kwargs={'pk': cmd.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('date_modification', response.data)

    def test_create_article_by_name_not_found_returns_404(self):
        url = reverse('commandes-list')
        data = {
            'magasin': self.magasin.id,
            'statut': 'en_attente',
            'articles': [
                {'produit': 'Produit Inexistant', 'quantite': 1}
            ]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_article_commande_viewset_perform_create(self):
        from orders.views import ArticleCommandeViewSet
        from unittest.mock import MagicMock

        cmd = Commande.objects.create(utilisateur=self.user, magasin=self.magasin, statut='en_attente')

        viewset = ArticleCommandeViewSet()
        mock_serializer = MagicMock()
        mock_serializer.validated_data = {
            'produit': self.produit_pasta,
            'quantite': 2,
            'commande': cmd,
        }
        viewset.perform_create(mock_serializer)
        mock_serializer.save.assert_called_once_with(prix_unitaire=self.produit_pasta.prix)


    def test_get_serializer_class_for_create(self):
        from orders.views import CommandeViewSet
        from orders.serializers import CommandeCreateSerializer
        viewset = CommandeViewSet()
        viewset.action = 'create'
        self.assertEqual(viewset.get_serializer_class(), CommandeCreateSerializer)


class OrdersModelStrTestCase(TestCase):

    def setUp(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        self.user = User.objects.create_user(username='struser', password='pass123')
        from enseignes.models import Enseigne, Magasin, Produit
        self.enseigne = Enseigne.objects.create(nom='TestEnseigne', statut='actif')
        self.magasin = Magasin.objects.create(
            nom='TestMagasin',
            adresse='1 Rue Test',
            code_postal='00000',
            ville='TestVille',
            enseigne=self.enseigne,
            statut='actif'
        )
        self.produit = Produit.objects.create(nom='TestProduit', prix=9.99)
        self.produit.magasins.set([self.magasin])

    def test_commande_str(self):
        cmd = Commande.objects.create(utilisateur=self.user, magasin=self.magasin, statut='en_attente')
        self.assertIn('struser', str(cmd))

    def test_article_commande_str(self):
        cmd = Commande.objects.create(utilisateur=self.user, magasin=self.magasin, statut='en_attente')
        article = ArticleCommande.objects.create(commande=cmd, produit=self.produit, quantite=3, prix_unitaire=9.99)
        self.assertIn('TestProduit', str(article))
        self.assertIn('3', str(article))
