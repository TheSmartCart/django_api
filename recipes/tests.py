from django.test import TestCase
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
		self.user1 = User.objects.create_user(username="u1", password="p1")
		self.user2 = User.objects.create_user(username="u2", password="p2")

		Recette.objects.create(nom="R1", temps_preparation="10m", difficulte="Debutant", status="Actif", utilisateur=self.user1)
		Recette.objects.create(nom="R2", temps_preparation="20m", difficulte="Intermediaire", status="Actif", utilisateur=self.user2)

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

	def test_create_recipe_with_ustensiles_as_string(self):
		url = reverse('recette-list')
		self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
		payload = {
			"nom": "Recette String Ust",
			"temps_preparation": "10m",
			"difficulte": "Debutant",
			"ustensiles": "Spatule, Bol",
		}
		resp = self.client.post(url, payload, format='json')
		self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
		self.assertIn("Spatule", [u["nom"] for u in resp.data["ustensiles"]])

	def test_create_recipe_with_invalid_ustensile_id(self):
		url = reverse('recette-list')
		self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
		payload = {
			"nom": "Recette Bad ID",
			"temps_preparation": "5m",
			"difficulte": "Debutant",
			"ustensiles": [{"id": 99999}],
		}
		resp = self.client.post(url, payload, format='json')
		self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
		self.assertEqual(len(resp.data["ustensiles"]), 0)

	def test_create_recipe_with_non_dict_step(self):
		url = reverse('recette-list')
		self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
		payload = {
			"nom": "Recette Non-Dict Step",
			"temps_preparation": "5m",
			"difficulte": "Debutant",
			"etapes": ["not a dict", {"description": "Étape valide"}],
		}
		resp = self.client.post(url, payload, format='json')
		self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
		self.assertEqual(len(resp.data["etapes"]), 1)

	def test_create_recipe_with_step_without_description(self):
		url = reverse('recette-list')
		self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
		payload = {
			"nom": "Recette No Desc Step",
			"temps_preparation": "5m",
			"difficulte": "Debutant",
			"etapes": [{"ordre": 1}, {"description": "Bonne étape"}],
		}
		resp = self.client.post(url, payload, format='json')
		self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
		self.assertEqual(len(resp.data["etapes"]), 1)


class RecettesModelStrTestCase(TestCase):

	def setUp(self):
		from django.contrib.auth import get_user_model
		User = get_user_model()
		self.user = User.objects.create_user(username='rstruser', password='pass')
		self.recette = Recette.objects.create(
			nom="Ma Recette",
			temps_preparation="20m",
			difficulte="Debutant",
			utilisateur=self.user
		)
		self.ingredient = Ingredient.objects.create(nom="Farine")
		self.ingredientrecette = IngredientRecette.objects.create(
			recette=self.recette,
			ingredient=self.ingredient,
			quantite=200,
			unite="g"
		)
		self.ustensile = Ustensile.objects.create(nom="Rouleau")
		self.ustensilerecette = UstensileRecette.objects.create(
			recette=self.recette,
			ustensile=self.ustensile
		)
		from recipes.models import Etape
		self.etape = Etape.objects.create(
			recette=self.recette,
			description="Mélanger",
			ordre=1
		)

	def test_recette_str(self):
		self.assertEqual(str(self.recette), "Ma Recette")

	def test_ingredient_str(self):
		self.assertEqual(str(self.ingredient), "Farine")

	def test_ingredientrecette_str(self):
		s = str(self.ingredientrecette)
		self.assertIn("Farine", s)
		self.assertIn("Ma Recette", s)

	def test_ustensile_str(self):
		self.assertEqual(str(self.ustensile), "Rouleau")

	def test_ustensilerecette_str(self):
		s = str(self.ustensilerecette)
		self.assertIn("Rouleau", s)
		self.assertIn("Ma Recette", s)

	def test_etape_str(self):
		s = str(self.etape)
		self.assertIn("Ma Recette", s)
		self.assertIn("1", s)


class RecetteGetQuerysetUnauthTestCase(TestCase):

	def test_get_queryset_unauthenticated(self):
		from recipes.views import RecetteViewSet
		from unittest.mock import MagicMock
		viewset = RecetteViewSet()
		mock_request = MagicMock()
		mock_request.user = None
		viewset.request = mock_request
		qs = viewset.get_queryset()
		self.assertEqual(qs.count(), 0)


class RecettePerformCreateTestCase(APITestCase):

	def setUp(self):
		from django.contrib.auth import get_user_model
		User = get_user_model()
		self.user = User.objects.create_user(username='pcruser', password='pass')

	def test_perform_create_assigns_user(self):
		from recipes.views import RecetteViewSet
		from unittest.mock import MagicMock
		viewset = RecetteViewSet()
		mock_request = MagicMock()
		mock_request.user = self.user
		viewset.request = mock_request
		mock_serializer = MagicMock()
		viewset.perform_create(mock_serializer)
		mock_serializer.save.assert_called_once_with(utilisateur=self.user)

	def test_create_recipe_with_invalid_type_payloads(self):
		url = reverse('recette-list')
		token_url = reverse('token_obtain_pair')
		resp_token = self.client.post(token_url, {"username": "pcruser", "password": "pass"}, format='json')
		access = resp_token.data['access']
		self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
		
		payload = {
			"nom": "Recette Invalid Types",
			"temps_preparation": "10m",
			"difficulte": "Debutant",
			"ustensiles": 123,
			"etapes": 456
		}
		resp = self.client.post(url, payload, format='json')
		self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
		self.assertEqual(len(resp.data["ustensiles"]), 0)
		self.assertEqual(len(resp.data["etapes"]), 0)

