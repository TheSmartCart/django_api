from rest_framework import serializers
from .models import Enseigne, Produit, Categorie

class CategorieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categorie
        fields = ['id', 'nom', 'description', 'statut']

class ProduitSerializer(serializers.ModelSerializer):
    categorie_nom = serializers.ReadOnlyField(source='categorie.nom')
    
    class Meta:
        model = Produit
        fields = ['id', 'nom', 'description', 'prix', 'image', 'categorie', 'categorie_nom']

class EnseigneSerializer(serializers.ModelSerializer):
    produits = ProduitSerializer(many=True, read_only=True)
    categories = CategorieSerializer(many=True, read_only=True)
    
    class Meta:
        model = Enseigne
        fields = ['id', 'nom', 'logo', 'description', 'adresse', 'horaires_ouverture', 
                  'statut', 'produits', 'categories']