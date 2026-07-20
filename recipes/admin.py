from django.contrib import admin
from .models import Recipe, Ingredient, RecipeIngredient, Step, Utensil, RecipeUtensil

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "user", "status", "created_at")
    search_fields = ("title", "user__username")
    list_filter = ("status", )

admin.site.register(Ingredient)
admin.site.register(RecipeIngredient)
admin.site.register(Step)
admin.site.register(Utensil)
admin.site.register(RecipeUtensil)
