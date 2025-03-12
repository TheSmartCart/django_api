from rest_framework import serializers
from .models import (Recette, Ingredient, IngredientRecette, Etape)

class RecetteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recette
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ["id", "nom"]

class EtapeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Etape
        fields = ["id", "ordre", "description"]

class IngredientRecetteSerializer(serializers.ModelSerializer):
    ingredient_nom = serializers.ReadOnlyField(source="ingredient.nom")
    recette_nom = serializers.ReadOnlyField(source="recette.nom")

    class Meta:
        model = IngredientRecette
        fields = ["id", "recette", "recette_nom", "ingredient", "ingredient_nom", "quantite", "unite"]
