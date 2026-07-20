from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Recipe, Utensil, RecipeUtensil, Ingredient, RecipeIngredient, Step

User = get_user_model()


class RecipeAuthTests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="u1", password="p1")
        self.user2 = User.objects.create_user(username="u2", password="p2")

        Recipe.objects.create(title="R1", prep_time="10m", difficulty="beginner", status="active", user=self.user1)
        Recipe.objects.create(title="R2", prep_time="20m", difficulty="intermediate", status="active", user=self.user2)

        url_token = reverse('token_obtain_pair')
        resp = self.client.post(url_token, {"username": "u1", "password": "p1"}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.access_token = resp.data["access"]

    def test_list_recipes_requires_auth(self):
        url = reverse('recipe-list')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_only_user_recipes(self):
        url = reverse('recipe-list')
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        titles = [r["title"] for r in resp.data]
        self.assertIn("R1", titles)
        self.assertNotIn("R2", titles)

    def test_create_sets_user(self):
        url = reverse('recipe-list')
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        payload = {
            "title": "R3",
            "prep_time": "15m",
            "difficulty": "beginner"
        }
        resp = self.client.post(url, payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        r = Recipe.objects.get(title="R3")
        self.assertEqual(r.user, self.user1)
        self.assertEqual(r.status, "active")

    def test_utensils_is_list_of_objects(self):
        r = Recipe.objects.create(title="With U", prep_time="5m", difficulty="beginner", status="active", user=self.user1)
        u1 = Utensil.objects.create(name="Knife")
        u2 = Utensil.objects.create(name="Board")
        RecipeUtensil.objects.create(recipe=r, utensil=u1)
        RecipeUtensil.objects.create(recipe=r, utensil=u2)

        url = reverse('recipe-list')
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        recipe = next((x for x in resp.data if x["title"] == "With U"), None)
        self.assertIsNotNone(recipe)
        self.assertIn("utensils", recipe)
        self.assertIsInstance(recipe["utensils"], list)
        self.assertTrue(all(isinstance(u, dict) and {"id", "name"}.issubset(u.keys()) for u in recipe["utensils"]))

    def test_ingredients_is_list_of_objects(self):
        r = Recipe.objects.create(title="With I", prep_time="7m", difficulty="beginner", user=self.user1)
        i1 = Ingredient.objects.create(name="Salt")
        i2 = Ingredient.objects.create(name="Pepper")
        RecipeIngredient.objects.create(recipe=r, ingredient=i1, quantity=1, unit="pinch")
        RecipeIngredient.objects.create(recipe=r, ingredient=i2, quantity=1, unit="turn")

        url = reverse('recipe-list')
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        recipe = next((x for x in resp.data if x["title"] == "With I"), None)
        self.assertIsNotNone(recipe)
        self.assertIn("ingredients", recipe)
        self.assertIsInstance(recipe["ingredients"], list)
        self.assertTrue(all(isinstance(i, dict) and {"id", "name"}.issubset(i.keys()) for i in recipe["ingredients"]))

    def test_recipe_has_description_and_image_fields(self):
        r = Recipe.objects.create(
            title="With fields",
            prep_time="30m",
            difficulty="beginner",
            status="active",
            user=self.user1,
            description="A great recipe",
        )
        url = reverse('recipe-list')
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        recipe = next((x for x in resp.data if x["title"] == "With fields"), None)
        self.assertIsNotNone(recipe)
        self.assertIn("description", recipe)
        self.assertIn("image", recipe)
        self.assertEqual(recipe["description"], "A great recipe")

    def test_create_recipe_with_nested_utensils_and_steps(self):
        existing = Utensil.objects.create(name="Pan")
        url = reverse('recipe-list')
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        payload = {
            "title": "Pasta",
            "prep_time": "12m",
            "difficulty": "beginner",
            "utensils": [
                {"id": existing.id},
                {"name": "Colander"},
                "Wooden Spoon"
            ],
            "steps": [
                {"description": "Boil water", "step_number": 1},
                {"description": "Cook pasta"},
                {"description": "Drain", "status": "active"}
            ]
        }
        resp = self.client.post(url, payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        data = resp.data
        self.assertEqual(data["title"], "Pasta")
        u_names = sorted([u["name"] for u in data["utensils"]])
        self.assertEqual(u_names, sorted(["Colander", "Pan", "Wooden Spoon"]))
        self.assertEqual(len(data["steps"]), 3)
        self.assertEqual(Utensil.objects.filter(name="Pan").count(), 1)

    def test_nested_utensils_default_status_active(self):
        url = reverse('recipe-list')
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        payload = {
            "title": "Default test",
            "prep_time": "5m",
            "difficulty": "beginner",
            "utensils": ["Whisk"]
        }
        resp = self.client.post(url, payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        u = Utensil.objects.get(name="Whisk")
        self.assertEqual(u.status, "active")

    def test_utensils_endpoint_default_status(self):
        url = reverse('utensil-list')
        resp = self.client.post(url, {"name": "Spatula"}, format='json')
        if resp.status_code == status.HTTP_401_UNAUTHORIZED:
            token_url = reverse('token_obtain_pair')
            resp_token = self.client.post(token_url, {"username": "u1", "password": "p1"}, format='json')
            self.assertEqual(resp_token.status_code, status.HTTP_200_OK)
            access = resp_token.data['access']
            self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
            resp = self.client.post(url, {"name": "Spatula"}, format='json')
        self.assertIn(resp.status_code, (status.HTTP_201_CREATED, status.HTTP_200_OK))
        self.assertEqual(Utensil.objects.get(name="Spatula").status, "active")

    def test_create_recipe_with_utensils_as_string(self):
        url = reverse('recipe-list')
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        payload = {
            "title": "Recipe String Utensil",
            "prep_time": "10m",
            "difficulty": "beginner",
            "utensils": "Spatula, Bowl",
        }
        resp = self.client.post(url, payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertIn("Spatula", [u["name"] for u in resp.data["utensils"]])

    def test_create_recipe_with_invalid_utensil_id(self):
        url = reverse('recipe-list')
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        payload = {
            "title": "Recipe Bad ID",
            "prep_time": "5m",
            "difficulty": "beginner",
            "utensils": [{"id": 99999}],
        }
        resp = self.client.post(url, payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(resp.data["utensils"]), 0)

    def test_create_recipe_with_non_dict_step(self):
        url = reverse('recipe-list')
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        payload = {
            "title": "Recipe Non-Dict Step",
            "prep_time": "5m",
            "difficulty": "beginner",
            "steps": ["not a dict", {"description": "Valid step"}],
        }
        resp = self.client.post(url, payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(resp.data["steps"]), 1)

    def test_create_recipe_with_step_without_description(self):
        url = reverse('recipe-list')
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        payload = {
            "title": "Recipe No Desc Step",
            "prep_time": "5m",
            "difficulty": "beginner",
            "steps": [{"step_number": 1}, {"description": "Good step"}],
        }
        resp = self.client.post(url, payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(resp.data["steps"]), 1)


class RecipesModelStrTestCase(TestCase):

    def setUp(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        self.user = User.objects.create_user(username='rstruser', password='pass')
        self.recipe = Recipe.objects.create(
            title="My Recipe",
            prep_time="20m",
            difficulty="beginner",
            user=self.user
        )
        self.ingredient = Ingredient.objects.create(name="Flour")
        self.recipe_ingredient = RecipeIngredient.objects.create(
            recipe=self.recipe,
            ingredient=self.ingredient,
            quantity=200,
            unit="g"
        )
        self.utensil = Utensil.objects.create(name="Roller")
        self.recipe_utensil = RecipeUtensil.objects.create(
            recipe=self.recipe,
            utensil=self.utensil
        )
        self.step = Step.objects.create(
            recipe=self.recipe,
            description="Mix well",
            step_number=1
        )

    def test_recipe_str(self):
        self.assertEqual(str(self.recipe), "My Recipe")

    def test_ingredient_str(self):
        self.assertEqual(str(self.ingredient), "Flour")

    def test_recipe_ingredient_str(self):
        s = str(self.recipe_ingredient)
        self.assertIn("Flour", s)
        self.assertIn("My Recipe", s)

    def test_utensil_str(self):
        self.assertEqual(str(self.utensil), "Roller")

    def test_recipe_utensil_str(self):
        s = str(self.recipe_utensil)
        self.assertIn("Roller", s)
        self.assertIn("My Recipe", s)

    def test_step_str(self):
        s = str(self.step)
        self.assertIn("My Recipe", s)
        self.assertIn("1", s)


class RecipeGetQuerysetUnauthTestCase(TestCase):

    def test_get_queryset_unauthenticated(self):
        from recipes.views import RecipeViewSet
        from unittest.mock import MagicMock
        viewset = RecipeViewSet()
        mock_request = MagicMock()
        mock_request.user = None
        viewset.request = mock_request
        qs = viewset.get_queryset()
        self.assertEqual(qs.count(), 0)


class RecipePerformCreateTestCase(APITestCase):

    def setUp(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        self.user = User.objects.create_user(username='pcruser', password='pass')

    def test_perform_create_assigns_user(self):
        from recipes.views import RecipeViewSet
        from unittest.mock import MagicMock
        viewset = RecipeViewSet()
        mock_request = MagicMock()
        mock_request.user = self.user
        viewset.request = mock_request
        mock_serializer = MagicMock()
        viewset.perform_create(mock_serializer)
        mock_serializer.save.assert_called_once_with(user=self.user)

    def test_create_recipe_with_invalid_type_payloads(self):
        url = reverse('recipe-list')
        token_url = reverse('token_obtain_pair')
        resp_token = self.client.post(token_url, {"username": "pcruser", "password": "pass"}, format='json')
        access = resp_token.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        
        payload = {
            "title": "Recipe Invalid Types",
            "prep_time": "10m",
            "difficulty": "beginner",
            "utensils": 123,
            "steps": 456
        }
        resp = self.client.post(url, payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(resp.data["utensils"]), 0)
        self.assertEqual(len(resp.data["steps"]), 0)
