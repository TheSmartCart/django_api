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

    class Meta:
        model = IngredientRecette
        fields = ["id", "ingredient_nom", "quantite", "unite"]
