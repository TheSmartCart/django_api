from rest_framework import viewsets
from .models import Enseigne, Produit, Categorie
from .serializers import EnseigneSerializer, ProduitSerializer, CategorieSerializer

class EnseigneViewSet(viewsets.ModelViewSet):
    queryset = Enseigne.objects.all()
    serializer_class = EnseigneSerializer

class ProduitViewSet(viewsets.ModelViewSet):
    queryset = Produit.objects.all()
    serializer_class = ProduitSerializer
    filterset_fields = ['enseigne', 'categorie']

class CategorieViewSet(viewsets.ModelViewSet):
    queryset = Categorie.objects.all()
    serializer_class = CategorieSerializer
    filterset_fields = ['enseigne']