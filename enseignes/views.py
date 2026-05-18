from rest_framework import viewsets
from .models import Enseigne, Produit, Categorie, Magasin
from .serializers import EnseigneSerializer, ProduitSerializer, CategorieSerializer, MagasinSerializer

class EnseigneViewSet(viewsets.ModelViewSet):
    queryset = Enseigne.objects.all().prefetch_related('magasins')
    serializer_class = EnseigneSerializer

class ProduitViewSet(viewsets.ModelViewSet):
    queryset = Produit.objects.all()
    serializer_class = ProduitSerializer
    
    def get_queryset(self):
        queryset = Produit.objects.all()
        enseigne = self.request.query_params.get('enseigne')
        if enseigne:
            queryset = queryset.filter(enseigne_id=enseigne)
        categorie = self.request.query_params.get('categorie')
        if categorie:
            queryset = queryset.filter(categorie_id=categorie)
        return queryset

class CategorieViewSet(viewsets.ModelViewSet):
    queryset = Categorie.objects.all()
    serializer_class = CategorieSerializer
    
    def get_queryset(self):
        queryset = Categorie.objects.all()
        enseigne = self.request.query_params.get('enseigne')
        if enseigne:
            queryset = queryset.filter(enseigne_id=enseigne)
        return queryset

class MagasinViewSet(viewsets.ModelViewSet):
    queryset = Magasin.objects.all()
    serializer_class = MagasinSerializer
    
    def get_queryset(self):
        queryset = Magasin.objects.all()
        enseigne = self.request.query_params.get('enseigne')
        if enseigne:
            queryset = queryset.filter(enseigne_id=enseigne)
        ville = self.request.query_params.get('ville')
        if ville:
            queryset = queryset.filter(ville=ville)
        code_postal = self.request.query_params.get('code_postal')
        if code_postal:
            queryset = queryset.filter(code_postal=code_postal)
        statut = self.request.query_params.get('statut')
        if statut:
            queryset = queryset.filter(statut=statut)
        return queryset