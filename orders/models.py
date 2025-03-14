from django.db import models
from users.models import CustomUser
from enseignes.models import Produit, Magasin

class Commande(models.Model):
    utilisateur = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='commandes')
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    statut = models.CharField(max_length=50, choices=[
        ('en_preparation', 'En préparation'),
        ('prete', 'Prête'),
        ('recuperee', 'Récupérée'),
        ('annulee', 'Annulée')
    ], default='en_preparation')
    magasin = models.ForeignKey(Magasin, on_delete=models.CASCADE, related_name='commandes')
    
    def __str__(self):
        return f"Commande #{self.id} - {self.utilisateur.username}"
    
    @property
    def prix_total(self):
        return sum(item.prix_total for item in self.articles.all())
    
    class Meta:
        verbose_name = "Commande"
        verbose_name_plural = "Commandes"
        ordering = ['-date_creation']

class ArticleCommande(models.Model):
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE, related_name='articles')
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField(default=1)
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.quantite} x {self.produit.nom} - Commande #{self.commande.id}"
    
    @property
    def prix_total(self):
        return self.prix_unitaire * self.quantite
    
    class Meta:
        verbose_name = "Article de commande"
        verbose_name_plural = "Articles de commande"