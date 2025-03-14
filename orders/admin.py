from django.contrib import admin
from .models import Commande, ArticleCommande

class ArticleCommandeInline(admin.TabularInline):
    model = ArticleCommande
    extra = 0
    readonly_fields = ['prix_total']

@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    list_display = ('id', 'utilisateur', 'magasin', 'statut', 'date_creation', 'prix_total')
    list_filter = ('statut', 'magasin')
    search_fields = ('utilisateur__username', 'magasin__nom')
    inlines = [ArticleCommandeInline]
    readonly_fields = ['prix_total']
    fieldsets = (
        (None, {
            'fields': ('utilisateur', 'magasin', 'statut')
        }),
        ('Informations', {
            'fields': ('date_creation', 'date_modification', 'prix_total')
        }),
    )

@admin.register(ArticleCommande)
class ArticleCommandeAdmin(admin.ModelAdmin):
    list_display = ('id', 'commande', 'produit', 'quantite', 'prix_unitaire', 'prix_total')
    list_filter = ('commande__statut',)
    search_fields = ('commande__id', 'produit__nom')