from django.contrib import admin
from .models import Enseigne, Produit, Categorie, Magasin

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

@admin.register(Magasin)
class MagasinAdmin(admin.ModelAdmin):
    list_display = ('nom', 'enseigne', 'ville', 'code_postal', 'statut')
    list_filter = ('enseigne', 'statut', 'ville')
    search_fields = ('nom', 'adresse', 'ville', 'code_postal')
    fieldsets = (
        (None, {
            'fields': ('nom', 'enseigne')
        }),
        ('Localisation', {
            'fields': ('adresse', 'code_postal', 'ville', 'latitude', 'longitude')
        }),
        ('Contact', {
            'fields': ('telephone', 'email')
        }),
        ('Informations', {
            'fields': ('horaires', 'statut')
        }),
    )