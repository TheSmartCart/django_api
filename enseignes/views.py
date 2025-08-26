from rest_framework import viewsets
from .models import Enseigne, Produit, Categorie, Magasin
from .serializers import EnseigneSerializer, ProduitSerializer, CategorieSerializer, MagasinSerializer

class EnseigneViewSet(viewsets.ModelViewSet):
    queryset = Enseigne.objects.all().prefetch_related('magasins')
    serializer_class = EnseigneSerializer

class ProduitViewSet(viewsets.ModelViewSet):
    queryset = Produit.objects.all()
    serializer_class = ProduitSerializer
    filterset_fields = ['enseigne', 'categorie']

class CategorieViewSet(viewsets.ModelViewSet):
    queryset = Categorie.objects.all()
    serializer_class = CategorieSerializer
    filterset_fields = ['enseigne']

class MagasinViewSet(viewsets.ModelViewSet):
    queryset = Magasin.objects.all()
    serializer_class = MagasinSerializer
    filterset_fields = ['enseigne', 'ville', 'code_postal', 'statut']