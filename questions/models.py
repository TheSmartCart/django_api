from django.db import models
from recipes.models import Recette
from django.contrib.auth import get_user_model

User = get_user_model()

class Question(models.Model):
    title = models.CharField(max_length=255)
    type = models.CharField(max_length=100, choices=[
        ('TypeQuestion1', 'Type 1'),
        ('TypeQuestion2', 'Type 2'),
        # Ajoutez d'autres types selon vos besoins
    ])
    dateCreation = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('Actif', 'Actif'),
        ('Brouillon', 'Brouillon'),
        ('Inactif', 'Inactif')
    ])
    recette = models.ForeignKey(Recette, on_delete=models.CASCADE, related_name='questions', null=True, blank=True)
    
    def __str__(self):
        return self.title

class TypeQuestion(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.nom

class Proposition(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='propositions')
    texte = models.CharField(max_length=255)
    estCorrecte = models.BooleanField(default=False)
    statut = models.CharField(max_length=20, default='Actif')
    
    def __str__(self):
        return self.texte