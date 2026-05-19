from rest_framework import serializers
from .models import Enseigne, Produit, Categorie, Magasin

class CategorieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categorie
        fields = ['id', 'nom', 'description', 'image', 'statut', 'magasins']

class ProduitSerializer(serializers.ModelSerializer):
    categorie_nom = serializers.ReadOnlyField(source='categorie.nom')
    
    class Meta:
        model = Produit
        fields = ['id', 'nom', 'description', 'prix', 'image', 'categorie', 'categorie_nom', 'magasins']

class MagasinSerializer(serializers.ModelSerializer):
    enseigne_nom = serializers.ReadOnlyField(source='enseigne.nom')
    
    class Meta:
        model = Magasin
        fields = ['id', 'nom', 'enseigne', 'enseigne_nom', 'adresse', 'code_postal', 
                  'ville', 'telephone', 'email', 'horaires', 'latitude', 
                  'longitude', 'statut', 'date_creation', 'date_modification']

class MagasinForEnseigneSerializer(serializers.ModelSerializer):
    codePostal = serializers.CharField(source='code_postal')
    latitude = serializers.FloatField(allow_null=True)
    longitude = serializers.FloatField(allow_null=True)
    enseigneId = serializers.IntegerField(source='enseigne_id', read_only=True)

    class Meta:
        model = Magasin
        fields = ['id', 'nom', 'adresse', 'ville', 'codePostal', 'latitude', 'longitude', 'enseigneId']

class EnseigneSerializer(serializers.ModelSerializer):
    magasins = MagasinForEnseigneSerializer(many=True, read_only=True)

    class Meta:
        model = Enseigne
        fields = ['id', 'nom', 'logoUrl', 'magasins']