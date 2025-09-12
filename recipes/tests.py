from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Recette
from .models import Ustensile, UstensileRecette
from .models import Ingredient, IngredientRecette

User = get_user_model()


class RecetteAuthTests(APITestCase):
	def setUp(self):
		# Crée deux utilisateurs
		self.user1 = User.objects.create_user(username="u1", password="p1")
		self.user2 = User.objects.create_user(username="u2", password="p2")

		# Recettes pour chacun
		Recette.objects.create(nom="R1", temps_preparation="10m", difficulte="Debutant", status="Actif", utilisateur=self.user1)
		Recette.objects.create(nom="R2", temps_preparation="20m", difficulte="Intermediaire", status="Actif", utilisateur=self.user2)

		# Obtenir token JWT pour user1
		url_token = reverse('token_obtain_pair')
		resp = self.client.post(url_token, {"username": "u1", "password": "p1"}, format='json')
		self.assertEqual(resp.status_code, status.HTTP_200_OK)
		self.access_token = resp.data["access"]

	def test_list_recettes_requires_auth(self):
		url = reverse('recette-list')
		resp = self.client.get(url)
		self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

	def test_list_only_user_recettes(self):
		url = reverse('recette-list')
		self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
		resp = self.client.get(url)
		self.assertEqual(resp.status_code, status.HTTP_200_OK)
		# Ne doit retourner que la recette de user1
		names = [r["nom"] for r in resp.data]
		self.assertIn("R1", names)
		self.assertNotIn("R2", names)

	def test_create_sets_user(self):
		url = reverse('recette-list')
		self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
		payload = {
			"nom": "R3",
			"temps_preparation": "15m",
			"difficulte": "Debutant"
		}
		resp = self.client.post(url, payload, format='json')
		self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
		r = Recette.objects.get(nom="R3")
		self.assertEqual(r.utilisateur, self.user1)
		self.assertEqual(r.status, "Actif")

	def test_ustensiles_is_list_of_objects(self):
		r = Recette.objects.create(nom="Avec U", temps_preparation="5m", difficulte="Debutant", status="Actif", utilisateur=self.user1)
		u1 = Ustensile.objects.create(nom="Couteau")
		u2 = Ustensile.objects.create(nom="Planche")
		UstensileRecette.objects.create(recette=r, ustensile=u1)
		UstensileRecette.objects.create(recette=r, ustensile=u2)

		url = reverse('recette-list')
		self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
		resp = self.client.get(url)
		self.assertEqual(resp.status_code, status.HTTP_200_OK)
		recette = next((x for x in resp.data if x["nom"] == "Avec U"), None)
		self.assertIsNotNone(recette)
		self.assertIn("ustensiles", recette)
		self.assertIsInstance(recette["ustensiles"], list)
		# Chaque entrée doit être un objet avec au moins id et nom
		self.assertTrue(all(isinstance(u, dict) and {"id", "nom"}.issubset(u.keys()) for u in recette["ustensiles"]))

	def test_ingredients_is_list_of_objects(self):
		r = Recette.objects.create(nom="Avec I", temps_preparation="7m", difficulte="Debutant", utilisateur=self.user1)
		i1 = Ingredient.objects.create(nom="Sel")
		i2 = Ingredient.objects.create(nom="Poivre")
		IngredientRecette.objects.create(recette=r, ingredient=i1, quantite=1, unite="pincée")
		IngredientRecette.objects.create(recette=r, ingredient=i2, quantite=1, unite="tour de moulin")

		url = reverse('recette-list')
		self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
		resp = self.client.get(url)
		self.assertEqual(resp.status_code, status.HTTP_200_OK)
		recette = next((x for x in resp.data if x["nom"] == "Avec I"), None)
		self.assertIsNotNone(recette)
		self.assertIn("ingredients", recette)
		self.assertIsInstance(recette["ingredients"], list)
		self.assertTrue(all(isinstance(i, dict) and {"id", "nom"}.issubset(i.keys()) for i in recette["ingredients"]))

	def test_recette_has_description_and_image_fields(self):
		r = Recette.objects.create(
			nom="Avec champs",
			temps_preparation="30m",
			difficulte="Debutant",
			status="Actif",
			utilisateur=self.user1,
			description="Une super recette",
		)
		url = reverse('recette-list')
		self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
		resp = self.client.get(url)
		self.assertEqual(resp.status_code, status.HTTP_200_OK)
		recette = next((x for x in resp.data if x["nom"] == "Avec champs"), None)
		self.assertIsNotNone(recette)
		# Les champs doivent exister (image peut être null)
		self.assertIn("description", recette)
		self.assertIn("image", recette)
		self.assertEqual(recette["description"], "Une super recette")

	def test_create_recipe_with_nested_ustensiles_and_etapes(self):
		existing = Ustensile.objects.create(nom="Casserole")
		url = reverse('recette-list')
		self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
		payload = {
			"nom": "Pâtes",
			"temps_preparation": "12m",
			"difficulte": "Debutant",
			"ustensiles": [
				{"id": existing.id},
				{"nom": "Passoire"},
				"Cuillère en bois"
			],
			"etapes": [
				{"description": "Faire bouillir l'eau", "ordre": 1},
				{"description": "Cuire les pâtes"},
				{"description": "Égoutter", "statut": "actif"}
			]
		}
		resp = self.client.post(url, payload, format='json')
		self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
		data = resp.data
		self.assertEqual(data["nom"], "Pâtes")
		u_names = sorted([u["nom"] for u in data["ustensiles"]])
		self.assertEqual(u_names, sorted(["Casserole", "Cuillère en bois", "Passoire"]))
		self.assertEqual(len(data["etapes"]), 3)
		self.assertEqual(Ustensile.objects.filter(nom="Casserole").count(), 1)

	def test_nested_ustensiles_default_status_actif(self):
		url = reverse('recette-list')
		self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
		payload = {
			"nom": "Test défaut",
			"temps_preparation": "5m",
			"difficulte": "Debutant",
			"ustensiles": ["Fouet"]
		}
		resp = self.client.post(url, payload, format='json')
		self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
		u = Ustensile.objects.get(nom="Fouet")
		self.assertEqual(u.status, "Actif")

	def test_ustensiles_endpoint_default_status(self):
		url = reverse('ustensile-list')
		resp = self.client.post(url, {"nom": "Spatule"}, format='json')
		if resp.status_code == status.HTTP_401_UNAUTHORIZED:
			token_url = reverse('token_obtain_pair')
			resp_token = self.client.post(token_url, {"username": "u1", "password": "p1"}, format='json')
			self.assertEqual(resp_token.status_code, status.HTTP_200_OK)
			access = resp_token.data['access']
			self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
			resp = self.client.post(url, {"nom": "Spatule"}, format='json')
		self.assertIn(resp.status_code, (status.HTTP_201_CREATED, status.HTTP_200_OK))
		self.assertEqual(Ustensile.objects.get(nom="Spatule").status, "Actif")
