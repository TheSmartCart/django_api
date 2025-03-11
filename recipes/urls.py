from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import IngredientViewSet, IngredientRecetteViewSet, RecetteViewSet, EtapeViewSet

router = DefaultRouter()
router.register(r'recettes', RecetteViewSet, basename='recette')
router.register(r'ingredients', IngredientViewSet, basename='ingredient')
router.register(r'ingredients_recette', IngredientRecetteViewSet, basename='ingredientrecette')
router.register(r'etapes', EtapeViewSet, basename='etape')

urlpatterns = [
    path('', include(router.urls)),
]