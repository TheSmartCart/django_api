from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import IngredientViewSet, IngredientRecetteViewSet

router = DefaultRouter()
router.register(r'recettes', IngredientViewSet, basename='recette')
router.register(r'ingredients', IngredientViewSet, basename='ingredient')
router.register(r'ingredients_recette', IngredientRecetteViewSet, basename='ingredientrecette')
router.register(r'etapes', IngredientViewSet, basename='etape')

urlpatterns = [
    path('', include(router.urls)),
]