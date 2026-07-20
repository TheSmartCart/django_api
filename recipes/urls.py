from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import IngredientViewSet, RecipeIngredientViewSet, RecipeViewSet, StepViewSet, UtensilViewSet, RecipeUtensilViewSet

router = DefaultRouter()
router.register(r'recipes', RecipeViewSet, basename='recipe')
router.register(r'ingredients', IngredientViewSet, basename='ingredient')
router.register(r'recipe-ingredients', RecipeIngredientViewSet, basename='recipeingredient')
router.register(r'utensils', UtensilViewSet, basename='utensil')
router.register(r'recipe-utensils', RecipeUtensilViewSet, basename='recipeutensil')
router.register(r'steps', StepViewSet, basename='step')

urlpatterns = [
    path('', include(router.urls)),
]