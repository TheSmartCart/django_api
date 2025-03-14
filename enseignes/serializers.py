from rest_framework import serializers
from .models import Enseigne, Produit, Categorie, Magasin

class CategorieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categorie
        fields = ['id', 'nom', 'description', 'statut']

class ProduitSerializer(serializers.ModelSerializer):
    categorie_nom = serializers.ReadOnlyField(source='categorie.nom')
    
    class Meta:
        model = Produit
        fields = ['id', 'nom', 'description', 'prix', 'image', 'categorie', 'categorie_nom']

class MagasinSerializer(serializers.ModelSerializer):
    enseigne_nom = serializers.ReadOnlyField(source='enseigne.nom')
    
    class Meta:
        model = Magasin
        fields = ['id', 'nom', 'enseigne', 'enseigne_nom', 'adresse', 'code_postal', 
                  'ville', 'telephone', 'email', 'horaires', 'latitude', 
                  'longitude', 'statut', 'date_creation', 'date_modification']

class EnseigneSerializer(serializers.ModelSerializer):
    produits = ProduitSerializer(many=True, read_only=True)
    categories = CategorieSerializer(many=True, read_only=True)
    magasins = MagasinSerializer(many=True, read_only=True)
    
    class Meta:
        model = Enseigne
        fields = ['id', 'nom', 'logo', 'description', 'adresse', 'horaires_ouverture', 
                  'statut', 'produits', 'categories', 'magasins']