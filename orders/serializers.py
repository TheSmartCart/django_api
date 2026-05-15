from rest_framework import serializers
from .models import Commande, ArticleCommande
from enseignes.models import Magasin, Produit


class ProduitOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Produit
        fields = ['id', 'nom', 'description', 'prix', 'image']


class MagasinOrderSerializer(serializers.ModelSerializer):
    enseigne_nom = serializers.ReadOnlyField(source='enseigne.nom')

    class Meta:
        model = Magasin
        fields = ['id', 'nom', 'enseigne_nom', 'adresse', 'code_postal', 'ville']


class ArticleCommandeInputSerializer(serializers.Serializer):
    produit = serializers.CharField()
    quantite = serializers.IntegerField(min_value=1, default=1)


class ArticleCommandeSerializer(serializers.ModelSerializer):
    produit = ProduitOrderSerializer(read_only=True)

    class Meta:
        model = ArticleCommande
        fields = ['id', 'produit', 'quantite', 'prix_unitaire']


class CommandeListSerializer(serializers.ModelSerializer):
    magasin = MagasinOrderSerializer(read_only=True)
    articles = ArticleCommandeSerializer(many=True, read_only=True)
    prix_total = serializers.FloatField(read_only=True)
    
    class Meta:
        model = Commande
        fields = ['id', 'date_creation', 'statut', 'magasin', 'articles', 'prix_total']

class CommandeDetailSerializer(serializers.ModelSerializer):
    magasin = MagasinOrderSerializer(read_only=True)
    articles = ArticleCommandeSerializer(many=True, read_only=True)
    prix_total = serializers.FloatField(read_only=True)
    
    class Meta:
        model = Commande
        fields = ['id', 'date_creation', 'date_modification', 'statut', 'magasin', 'articles', 'prix_total']


class CommandeCreateSerializer(serializers.Serializer):
    magasin = serializers.IntegerField()
    articles = ArticleCommandeInputSerializer(many=True)
    statut = serializers.ChoiceField(
        choices=['en_attente', 'en_preparation', 'prete', 'recuperee', 'annulee'],
        default='en_attente'
    )


class StatutUpdateSerializer(serializers.Serializer):
    statut = serializers.ChoiceField(
        choices=['en_attente', 'en_preparation', 'prete', 'recuperee', 'annulee']
    )


class CommandePatchSerializer(serializers.Serializer):
    articles = ArticleCommandeInputSerializer(many=True, required=False)
    statut = serializers.ChoiceField(
        choices=['en_attente', 'en_preparation', 'prete', 'recuperee', 'annulee'],
        required=False,
    )