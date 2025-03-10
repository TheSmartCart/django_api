from rest_framework import serializers
from .models import Ingredient, IngredientRecette

class IngredientRecetteSerializer(serializers.ModelSerializer):
    ingredient_nom = serializers.CharField(source='ingredient.nom', read_only=True) 
    class Meta:
        model = IngredientRecette
        fields = ['id', 'recette', 'ingredient', 'quantite', 'unite', 'status', 'ingredient_nom']

class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'
