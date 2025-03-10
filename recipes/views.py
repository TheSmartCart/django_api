from rest_framework import viewsets
from .models import Ingredient, IngredientRecette
from .serializers import IngredientSerializer, IngredientRecetteSerializer

class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer

class IngredientRecetteViewSet(viewsets.ModelViewSet):
    queryset = IngredientRecette.objects.all()
    serializer_class = IngredientRecetteSerializer