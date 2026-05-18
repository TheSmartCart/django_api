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
        self.categorie = Categorie.objects.create(nom='Épicerie', enseigne=self.enseigne, statut='active')
        self.produit = Produit.objects.create(nom='Pâtes', prix=1.50, enseigne=self.enseigne, categorie=self.categorie)
        self.magasin = Magasin.objects.create(
            nom='Carrefour Market',
            adresse='123 Rue de Paris',
            code_postal='75001',
            ville='Paris',
            enseigne=self.enseigne,
            statut='actif'
        )

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

    def test_filter_categories_by_enseigne(self):
        other_enseigne = Enseigne.objects.create(nom='Leclerc', statut='actif')
        other_cat = Categorie.objects.create(nom='Boulangerie', enseigne=other_enseigne)
        
        url = reverse('categorie-list')
        response = self.client.get(f"{url}?enseigne={self.enseigne.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['nom'], 'Épicerie')

    def test_create_categorie(self):
        url = reverse('categorie-list')
        data = {
            'nom': 'Fruits & Légumes',
            'enseigne': self.enseigne.id,
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
        response = self.client.get(f"{url}?enseigne={self.enseigne.id}&categorie={self.categorie.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_produit(self):
        url = reverse('produit-list')
        data = {
            'nom': 'Riz',
            'prix': 2.30,
            'enseigne': self.enseigne.id,
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
