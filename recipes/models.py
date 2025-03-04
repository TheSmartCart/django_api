from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Recette(models.Model):
    nom = models.CharField(max_length=255)
    temps_preparation = models.CharField(max_length=50)
    difficulte = models.CharField(max_length=50, choices=[('Debutant', 'Debutant'), ('Intermediaire', 'Intermediaire'), ('Expert', 'Expert'), ('Chef etoile', 'Chef etoile')])
    date_creation = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[('Actif', 'Actif'), ('Brouillon', 'Brouillon'), ('Inactif', 'Inactif')])
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE, related_name="recettes")

    def __str__(self):
        return self.nom