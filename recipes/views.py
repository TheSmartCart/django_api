from rest_framework import viewsets
from .models import (Recette, Ingredient, IngredientRecette, Etape, Ustensile, UstensileRecette)
from .serializers import (RecetteSerializer, IngredientSerializer, 
                         IngredientRecetteSerializer, EtapeSerializer, UstensileSerializer, UstensileRecetteSerializer)

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

class UstensileViewSet(viewsets.ModelViewSet):
    queryset = Ustensile.objects.all()
    serializer_class = UstensileSerializer

class UstensileRecetteViewSet(viewsets.ModelViewSet):
    queryset = UstensileRecette.objects.all()
    serializer_class = UstensileRecetteSerializer