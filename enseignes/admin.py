from django.contrib import admin
from .models import Enseigne, Produit, Categorie, Magasin

@admin.register(Enseigne)
class EnseigneAdmin(admin.ModelAdmin):
    list_display = ('nom', 'statut')
    search_fields = ('nom',)

@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display = ('nom', 'prix', 'magasin', 'categorie')
    list_filter = ('magasin', 'categorie')
    search_fields = ('nom', 'description')

@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ('nom', 'magasin', 'statut')
    list_filter = ('magasin', 'statut')
    search_fields = ('nom',)
    readonly_fields = ()

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