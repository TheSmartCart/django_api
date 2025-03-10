from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import IngredientViewSet, IngredientRecetteViewSet

router = DefaultRouter()
router.register(r'ingredients', IngredientViewSet, basename='ingredient')
router.register(r'ingredients_recette', IngredientRecetteViewSet, basename='ingredientrecette')

urlpatterns = [
    path('', include(router.urls)),
]