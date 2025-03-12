from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import IngredientViewSet, IngredientRecetteViewSet, RecetteViewSet, EtapeViewSet, UstensileViewSet, UstensileRecetteViewSet

router = DefaultRouter()
router.register(r'recettes', RecetteViewSet, basename='recette')
router.register(r'ingredients', IngredientViewSet, basename='ingredient')
router.register(r'ingredients_recette', IngredientRecetteViewSet, basename='ingredientrecette')
router.register(r'ustensiles', UstensileViewSet, basename='ustensile')
router.register(r'ustensiles_recette', UstensileRecetteViewSet, basename='ustensilerecette')
router.register(r'etapes', EtapeViewSet, basename='etape')

urlpatterns = [
    path('', include(router.urls)),
]