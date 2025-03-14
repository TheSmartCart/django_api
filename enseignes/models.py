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

class Magasin(models.Model):
    nom = models.CharField(max_length=100)
    adresse = models.CharField(max_length=255)
    code_postal = models.CharField(max_length=10)
    ville = models.CharField(max_length=100)
    telephone = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    
    # Relation avec Enseigne (un magasin appartient à une enseigne)
    enseigne = models.ForeignKey('Enseigne', on_delete=models.CASCADE, related_name='magasins')
    
    # Informations supplémentaires
    horaires = models.TextField(blank=True, null=True, help_text="Format JSON recommandé pour les horaires")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    
    # Statut du magasin
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