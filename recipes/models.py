from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Recette(models.Model):
    nom = models.CharField(max_length=255)
    temps_preparation = models.CharField(max_length=50)
    difficulte = models.CharField(max_length=50, choices=[('Debutant', 'Debutant'), ('Intermediaire', 'Intermediaire'), ('Expert', 'Expert'), ('Chef etoile', 'Chef etoile')])
    date_creation = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[('Actif', 'Actif'), ('Brouillon', 'Brouillon'), ('Inactif', 'Inactif')], default='Actif')
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE, related_name="recettes")
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='recettes/', null=True, blank=True)

    def __str__(self):
        return self.nom

class Ingredient(models.Model):
    nom = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=20, choices=[('Actif', 'Actif'), ('Inactif', 'Inactif')], default='Actif')

    def __str__(self):
        return self.nom

class IngredientRecette(models.Model):
    recette = models.ForeignKey(Recette, on_delete=models.CASCADE, related_name="ingredients_recette")
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name="recettes_utilisant")
    quantite = models.FloatField()
    unite = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=[('Actif', 'Actif'), ('Inactif', 'Inactif')], default='Actif')

    def __str__(self):
        return f"{self.quantite} {self.unite} de {self.ingredient.nom} pour {self.recette.nom}"

class Ustensile(models.Model):
    nom = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=20, choices=[('Actif', 'Actif'), ('Inactif', 'Inactif')], default='Actif')

    def __str__(self):
        return self.nom

class UstensileRecette(models.Model):
    recette = models.ForeignKey(Recette, on_delete=models.CASCADE, related_name="ustensile_recette")
    ustensile = models.ForeignKey(Ustensile, on_delete=models.CASCADE, related_name="recettes_utilisant")
    status = models.CharField(max_length=20, choices=[('Actif', 'Actif'), ('Inactif', 'Inactif')], default='Actif')

    def __str__(self):
        return f"Vous aurez besoin de {self.ustensile.nom} pour {self.recette.nom}"

class Etape(models.Model):
    recette = models.ForeignKey(Recette, on_delete=models.CASCADE, related_name="etapes")
    description = models.TextField()
    ordre = models.PositiveIntegerField()
    statut = models.CharField(max_length=50, default="actif")

    class Meta:
        ordering = ["ordre"]

    def __str__(self):
        return f"Étape {self.ordre} - {self.recette.nom}"