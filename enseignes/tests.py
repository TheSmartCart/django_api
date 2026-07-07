from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from enseignes.models import Enseigne, Categorie, Produit, Magasin

User = get_user_model()

class EnseignesAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.force_authenticate(user=self.user)

        self.enseigne = Enseigne.objects.create(nom='Carrefour', statut='actif')
        self.magasin = Magasin.objects.create(
            nom='Carrefour Market',
            adresse='123 Rue de Paris',
            code_postal='75001',
            ville='Paris',
            enseigne=self.enseigne,
            statut='actif'
        )
        self.categorie = Categorie.objects.create(nom='Épicerie', statut='active')
        self.categorie.magasins.set([self.magasin])

        self.produit = Produit.objects.create(nom='Pâtes', prix=1.50, categorie=self.categorie)
        self.produit.magasins.set([self.magasin])

    def test_list_enseignes(self):
        url = reverse('enseigne-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['nom'], 'Carrefour')
        self.assertEqual(len(response.data[0]['magasins']), 1)
        self.assertEqual(response.data[0]['magasins'][0]['nom'], 'Carrefour Market')

    def test_create_enseigne(self):
        url = reverse('enseigne-list')
        data = {'nom': 'Auchan', 'statut': 'actif'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Enseigne.objects.filter(nom='Auchan').count(), 1)

    def test_list_categories(self):
        url = reverse('categorie-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_filter_categories_by_magasin(self):
        other_enseigne = Enseigne.objects.create(nom='Leclerc', statut='actif')
        other_magasin = Magasin.objects.create(
            nom='Leclerc Centre',
            adresse='99 Rue Victor Hugo',
            code_postal='33000',
            ville='Bordeaux',
            enseigne=other_enseigne,
            statut='actif'
        )
        other_cat = Categorie.objects.create(nom='Boulangerie')
        other_cat.magasins.set([other_magasin])

        url = reverse('categorie-list')
        response = self.client.get(f"{url}?magasin={self.magasin.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['nom'], 'Épicerie')

    def test_create_categorie(self):
        url = reverse('categorie-list')
        data = {
            'nom': 'Fruits & Légumes',
            'statut': 'active'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Categorie.objects.filter(nom='Fruits & Légumes').exists())

    def test_list_produits(self):
        url = reverse('produit-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_filter_produits(self):
        url = reverse('produit-list')
        response = self.client.get(f"{url}?magasin={self.magasin.id}&categorie={self.categorie.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_produit(self):
        url = reverse('produit-list')
        data = {
            'nom': 'Riz',
            'prix': 2.30,
            'categorie': self.categorie.id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Produit.objects.filter(nom='Riz').exists())

    def test_list_magasins(self):
        url = reverse('magasin-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_filter_magasins(self):
        url = reverse('magasin-list')
        response = self.client.get(f"{url}?enseigne={self.enseigne.id}&ville=Paris&statut=actif")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_magasin(self):
        url = reverse('magasin-list')
        data = {
            'nom': 'Carrefour Express',
            'adresse': '456 Rue de Lyon',
            'code_postal': '69002',
            'ville': 'Lyon',
            'enseigne': self.enseigne.id,
            'statut': 'actif'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Magasin.objects.filter(nom='Carrefour Express').exists())

    def test_filter_magasins_by_code_postal(self):
        url = reverse('magasin-list')
        response = self.client.get(f"{url}?code_postal=75001")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['nom'], 'Carrefour Market')


class EnseignesModelStrTestCase(TestCase):

    def setUp(self):
        self.enseigne = Enseigne.objects.create(nom='Leclerc', statut='actif')
        self.magasin = Magasin.objects.create(
            nom='Leclerc Lyon',
            adresse='1 Rue Victor Hugo',
            code_postal='69001',
            ville='Lyon',
            enseigne=self.enseigne,
            statut='actif'
        )
        self.categorie = Categorie.objects.create(nom='Crèmerie', statut='active')
        self.produit = Produit.objects.create(nom='Beurre', prix=1.80)

    def test_enseigne_str(self):
        self.assertEqual(str(self.enseigne), 'Leclerc')

    def test_produit_str(self):
        self.assertEqual(str(self.produit), 'Beurre')

    def test_categorie_str(self):
        self.assertEqual(str(self.categorie), 'Crèmerie')

    def test_magasin_str(self):
        self.assertEqual(str(self.magasin), 'Leclerc Lyon - Lyon (Leclerc)')
