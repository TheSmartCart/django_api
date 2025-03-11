from rest_framework import viewsets
from .models import (Recette, Ingredient, IngredientRecette, Etape)
from .serializers import (RecetteSerializer, IngredientSerializer, 
                         IngredientRecetteSerializer, EtapeSerializer)

class RecetteViewSet(viewsets.ModelViewSet):
    queryset = Recette.objects.all()
    serializer_class = RecetteSerializer

class EtapeViewSet(viewsets.ModelViewSet):
    queryset = Etape.objects.all()
    serializer_class = EtapeSerializer

class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer

class IngredientRecetteViewSet(viewsets.ModelViewSet):
    queryset = IngredientRecette.objects.all()
    serializer_class = IngredientRecetteSerializer