from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class TypeQuestion(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.nom

class Question(models.Model):
    title = models.CharField(max_length=255)
    type = models.ForeignKey(TypeQuestion, on_delete=models.CASCADE, related_name='questions')
    dateCreation = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('Actif', 'Actif'),
        ('Brouillon', 'Brouillon'),
        ('Inactif', 'Inactif')
    ])
    
    def __str__(self):
        return self.title

class Proposition(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='propositions')
    texte = models.CharField(max_length=255)
    statut = models.CharField(max_length=20, default='Actif')
    
    def __str__(self):
        return self.texte