from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from .models import (Recipe, Ingredient, RecipeIngredient, Step, Utensil, RecipeUtensil)

class StepSerializer(serializers.ModelSerializer):
    class Meta:
        model = Step
        fields = ["id", "step_number", "description", "recipe"]
        extra_kwargs = {
            'recipe': {'required': True}
        }

class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ["id", "name"]

class RecipeIngredientDetailSerializer(serializers.ModelSerializer):
    ingredient = IngredientSerializer(read_only=True)
    
    class Meta:
        model = RecipeIngredient
        fields = ["id", "ingredient", "quantity", "unit"]

class UtensilSerializer(serializers.ModelSerializer):
    class Meta:
        model = Utensil
        fields = '__all__'
        extra_kwargs = {
            'status': {'required': False, 'default': 'active'}
        }

class RecipeUtensilDetailSerializer(serializers.ModelSerializer):
    utensil = UtensilSerializer(read_only=True)
    
    class Meta:
        model = RecipeUtensil
        fields = '__all__'

class RecipeSerializer(serializers.ModelSerializer):
    ingredients = serializers.SerializerMethodField()
    steps = StepSerializer(many=True, read_only=True)
    utensils = serializers.SerializerMethodField()
    
    class Meta:
        model = Recipe
        fields = '__all__'
        extra_kwargs = {
            'user': {'read_only': True},
            'created_at': {'read_only': True},
            'status': {'read_only': True},
        }
    
    @extend_schema_field(IngredientSerializer(many=True))
    def get_ingredients(self, obj):
        ingredients_qs = Ingredient.objects.filter(used_in_recipes__recipe=obj,
                                                  used_in_recipes__status='active').distinct()
        return IngredientSerializer(ingredients_qs, many=True).data
    
    @extend_schema_field(UtensilSerializer(many=True))
    def get_utensils(self, obj):
        utensils_qs = Utensil.objects.filter(used_in_recipes__recipe=obj,
                                             used_in_recipes__status='active')
        return UtensilSerializer(utensils_qs, many=True).data


class RecipeIngredientSerializer(serializers.ModelSerializer):
    ingredient_name = serializers.ReadOnlyField(source="ingredient.name")
    recipe_title = serializers.ReadOnlyField(source="recipe.title")

    class Meta:
        model = RecipeIngredient
        fields = ["id", "recipe", "recipe_title", "ingredient", "ingredient_name", "quantity", "unit"]

class RecipeUtensilSerializer(serializers.ModelSerializer):
    utensil_name = serializers.ReadOnlyField(source="utensil.name")
    recipe_title = serializers.ReadOnlyField(source="recipe.title")

    class Meta:
        model = RecipeUtensil
        fields = ["id", "recipe", "recipe_title", "utensil", "utensil_name"]