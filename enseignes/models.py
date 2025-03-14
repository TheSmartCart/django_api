from django.db import models

class Enseigne(models.Model):
    nom = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='enseignes/logos/', blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    adresse = models.CharField(max_length=255, blank=True, null=True)
    horaires_ouverture = models.CharField(max_length=255, blank=True, null=True)  # Could be JSON or specific format
    statut = models.CharField(max_length=50, choices=[
        ('ouvert', 'Ouvert'),
        ('fermé', 'Fermé'),
        ('en_pause', 'En Pause')
    ], default='fermé')
    
    def __str__(self):
        return self.nom

class Produit(models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='produits/images/', blank=True, null=True)
    enseigne = models.ForeignKey(Enseigne, on_delete=models.CASCADE, related_name='produits')
    categorie = models.ForeignKey('Categorie', on_delete=models.SET_NULL, null=True, related_name='produits')
    
    def __str__(self):
        return f"{self.nom} - {self.enseigne.nom}"

class Categorie(models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    enseigne = models.ForeignKey(Enseigne, on_delete=models.CASCADE, related_name='categories')
    statut = models.CharField(max_length=50, default='active')
    
    def __str__(self):
        return f"{self.nom} - {self.enseigne.nom}"