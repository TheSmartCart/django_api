from rest_framework import serializers
from .models import (Recette, Ingredient, IngredientRecette, Etape)

class EtapeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Etape
        fields = ["id", "ordre", "description"]

class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ["id", "nom"]

class IngredientRecetteDetailSerializer(serializers.ModelSerializer):
    ingredient = IngredientSerializer(read_only=True)
    
    class Meta:
        model = IngredientRecette
        fields = ["id", "ingredient", "quantite", "unite"]

class RecetteSerializer(serializers.ModelSerializer):
    ingredients = serializers.SerializerMethodField()
    etapes = EtapeSerializer(many=True, read_only=True)
    
    class Meta:
        model = Recette
        fields = '__all__'
    
    def get_ingredients(self, obj):
        ingredients_recette = IngredientRecette.objects.filter(recette=obj, status='Actif')
        return IngredientRecetteDetailSerializer(ingredients_recette, many=True).data


class IngredientRecetteSerializer(serializers.ModelSerializer):
    ingredient_nom = serializers.ReadOnlyField(source="ingredient.nom")
    recette_nom = serializers.ReadOnlyField(source="recette.nom")

    class Meta:
        model = IngredientRecette
        fields = ["id", "recette", "recette_nom", "ingredient", "ingredient_nom", "quantite", "unite"]