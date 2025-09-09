from django.contrib import admin
from .models import Recette, Ingredient, IngredientRecette, Etape, Ustensile, UstensileRecette

@admin.register(Recette)
class RecetteAdmin(admin.ModelAdmin):
	list_display = ("id", "nom", "utilisateur", "status", "date_creation")
	search_fields = ("nom", "utilisateur__username")
	list_filter = ("status", )

admin.site.register(Ingredient)
admin.site.register(IngredientRecette)
admin.site.register(Etape)
admin.site.register(Ustensile)
admin.site.register(UstensileRecette)
