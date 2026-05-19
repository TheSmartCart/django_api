from django.db import models

class Enseigne(models.Model):
    nom = models.CharField(max_length=100)
    logoUrl = models.ImageField(upload_to='enseignes/logos/', blank=True, null=True)
    statut = models.CharField(max_length=50, choices=[
        ('actif', 'Actif'),
        ('inactif', 'Inactif'),
    ], default='Actif')
    
    def __str__(self):
        return self.nom

class Produit(models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='produits/images/', blank=True, null=True)
    magasins = models.ManyToManyField('Magasin', related_name='produits', blank=True)
    categorie = models.ForeignKey('Categorie', on_delete=models.SET_NULL, null=True, related_name='produits')
    
    def __str__(self):
        return self.nom

class Categorie(models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='categories/images/', blank=True, null=True)
    magasins = models.ManyToManyField('Magasin', related_name='categories', blank=True)
    statut = models.CharField(max_length=50, default='active')
    
    def __str__(self):
        return self.nom

class Magasin(models.Model):
    nom = models.CharField(max_length=100)
    adresse = models.CharField(max_length=255)
    code_postal = models.CharField(max_length=10)
    ville = models.CharField(max_length=100)
    telephone = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    
    enseigne = models.ForeignKey('Enseigne', on_delete=models.CASCADE, related_name='magasins')
    
    horaires = models.TextField(blank=True, null=True, help_text="Format JSON recommandé pour les horaires")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    
    statut = models.CharField(max_length=50, choices=[
        ('actif', 'Actif'),
        ('inactif', 'Inactif'),
    ], default='Actif')
    
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.nom} - {self.ville} ({self.enseigne.nom})"
    
    class Meta:
        verbose_name = "Magasin"
        verbose_name_plural = "Magasins"
        ordering = ['enseigne', 'ville', 'nom']