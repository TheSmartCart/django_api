from rest_framework import serializers
from .models import Commande, ArticleCommande
from enseignes.serializers import ProduitSerializer, MagasinSerializer

class ArticleCommandeSerializer(serializers.ModelSerializer):
    produit_nom = serializers.ReadOnlyField(source='produit.nom')
    prix_total = serializers.ReadOnlyField()
    
    class Meta:
        model = ArticleCommande
        fields = ['id', 'commande', 'produit', 'produit_nom', 'quantite', 'prix_unitaire', 'prix_total']

class CommandeListSerializer(serializers.ModelSerializer):
    utilisateur_nom = serializers.ReadOnlyField(source='utilisateur.username')
    magasin_nom = serializers.ReadOnlyField(source='magasin.nom')
    prix_total = serializers.ReadOnlyField()
    
    class Meta:
        model = Commande
        fields = ['id', 'utilisateur', 'utilisateur_nom', 'date_creation', 'statut', 
                  'magasin', 'magasin_nom', 'prix_total']

class CommandeDetailSerializer(serializers.ModelSerializer):
    utilisateur_nom = serializers.ReadOnlyField(source='utilisateur.username')
    magasin_nom = serializers.ReadOnlyField(source='magasin.nom')
    articles = ArticleCommandeSerializer(many=True, read_only=True)
    prix_total = serializers.ReadOnlyField()
    
    class Meta:
        model = Commande
        fields = ['id', 'utilisateur', 'utilisateur_nom', 'date_creation', 'date_modification',
                  'statut', 'magasin', 'magasin_nom', 'articles', 'prix_total']