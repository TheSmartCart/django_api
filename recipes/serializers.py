from rest_framework import serializers
from .models import (Recette, Ingredient, IngredientRecette, Etape, Ustensile, UstensileRecette)

class EtapeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Etape
        fields = ["id", "ordre", "description", "recette"]
        extra_kwargs = {
            'recette': {'required': True}
        }

class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ["id", "nom"]

class IngredientRecetteDetailSerializer(serializers.ModelSerializer):
    ingredient = IngredientSerializer(read_only=True)
    
    class Meta:
        model = IngredientRecette
        fields = ["id", "ingredient", "quantite", "unite"]

class UstensileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ustensile
        fields = '__all__'

class UstensileRecetteDetailSerializer(serializers.ModelSerializer):
    ustensile = UstensileSerializer(read_only=True)
    
    class Meta:
        model = UstensileRecette
        fields = '__all__'

class RecetteSerializer(serializers.ModelSerializer):
    ingredients = serializers.SerializerMethodField()
    etapes = EtapeSerializer(many=True, read_only=True)
    ustensiles = serializers.SerializerMethodField()
    
    class Meta:
        model = Recette
        fields = '__all__'
    
    def get_ingredients(self, obj):
        ingredients_recette = IngredientRecette.objects.filter(recette=obj, status='Actif')
        return IngredientRecetteDetailSerializer(ingredients_recette, many=True).data
    
    def get_ustensiles(self, obj):
        ustensiles_recette = UstensileRecette.objects.filter(recette=obj, status='Actif')
        return UstensileRecetteDetailSerializer(ustensiles_recette, many=True).data


class IngredientRecetteSerializer(serializers.ModelSerializer):
    ingredient_nom = serializers.ReadOnlyField(source="ingredient.nom")
    recette_nom = serializers.ReadOnlyField(source="recette.nom")

    class Meta:
        model = IngredientRecette
        fields = ["id", "recette", "recette_nom", "ingredient", "ingredient_nom", "quantite", "unite"]

class UstensileRecetteSerializer(serializers.ModelSerializer):
    ustensile_nom = serializers.ReadOnlyField(source="ustensile.nom")
    recette_nom = serializers.ReadOnlyField(source="recette.nom")

    class Meta:
        model = UstensileRecette
        fields = ["id", "recette", "recette_nom", "ustensile", "ustensile_nom"]