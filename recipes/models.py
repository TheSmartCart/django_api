from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Recipe(models.Model):
    title = models.CharField(max_length=255)
    prep_time = models.CharField(max_length=50)
    difficulty = models.CharField(max_length=50, choices=[
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('expert', 'Expert'),
        ('starred_chef', 'Starred Chef')
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('active', 'Active'),
        ('draft', 'Draft'),
        ('inactive', 'Inactive')
    ], default='active')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="recipes")
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='recipes/', null=True, blank=True)

    def __str__(self):
        return self.title

class Ingredient(models.Model):
    name = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=20, choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active')

    def __str__(self):
        return self.name

class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="recipe_ingredients")
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name="used_in_recipes")
    quantity = models.FloatField()
    unit = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active')

    def __str__(self):
        return f"{self.quantity} {self.unit} of {self.ingredient.name} for {self.recipe.title}"

class Utensil(models.Model):
    name = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=20, choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active')

    def __str__(self):
        return self.name

class RecipeUtensil(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="recipe_utensils")
    utensil = models.ForeignKey(Utensil, on_delete=models.CASCADE, related_name="used_in_recipes")
    status = models.CharField(max_length=20, choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active')

    def __str__(self):
        return f"You will need {self.utensil.name} for {self.recipe.title}"

class Step(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="steps")
    description = models.TextField()
    step_number = models.PositiveIntegerField()
    status = models.CharField(max_length=50, default="active")

    class Meta:
        ordering = ["step_number"]

    def __str__(self):
        return f"Step {self.step_number} - {self.recipe.title}"