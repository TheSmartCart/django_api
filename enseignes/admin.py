from django.contrib import admin
from .models import Enseigne, Produit, Categorie

@admin.register(Enseigne)
class EnseigneAdmin(admin.ModelAdmin):
    list_display = ('nom', 'statut')
    search_fields = ('nom', 'description')

@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display = ('nom', 'prix', 'enseigne', 'categorie')
    list_filter = ('enseigne', 'categorie')
    search_fields = ('nom', 'description')

@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ('nom', 'enseigne', 'statut')
    list_filter = ('enseigne', 'statut')
    search_fields = ('nom',)