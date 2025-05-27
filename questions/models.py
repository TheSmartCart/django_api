from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class TypeQuestion(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.nom

class Question(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    type = models.ForeignKey(TypeQuestion, on_delete=models.CASCADE, related_name='questions')
    dateCreation = models.DateTimeField(auto_now_add=True)
    min_value = models.FloatField(null=True, blank=True, help_text="Valeur minimale pour les questions de type slider")
    max_value = models.FloatField(null=True, blank=True, help_text="Valeur maximale pour les questions de type slider")
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
    image = models.ImageField(upload_to='propositions/', blank=True, null=True)
    
    def __str__(self):
        return self.texte

class ReponseUtilisateur(models.Model):
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reponses')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='reponses_utilisateurs')
    date_creation = models.DateTimeField(auto_now_add=True)
    valeur_numerique = models.FloatField(null=True, blank=True)
    
    def clean(self):
        from django.core.exceptions import ValidationError
        
        # Si l'objet n'a pas encore été sauvegardé (pas d'ID), on ne peut pas vérifier
        # les propositions_selectionnees car elles n'existent pas encore
        if self.pk is None:
            return
            
        # Vérifier qu'au moins un des champs valeur_numerique ou propositions_selectionnees existe
        if self.valeur_numerique is None and not self.propositions_selectionnees.exists():
            raise ValidationError("Vous devez fournir soit une valeur numérique, soit au moins une proposition sélectionnée.")
        
        # Vérifier qu'on n'a pas à la fois une valeur numérique et des propositions sélectionnées
        if self.valeur_numerique is not None and self.propositions_selectionnees.exists():
            raise ValidationError("Vous ne pouvez pas fournir à la fois une valeur numérique et des propositions sélectionnées.")
    
    def save(self, *args, **kwargs):
        self.clean()
        super(ReponseUtilisateur, self).save(*args, **kwargs)
    
    def __str__(self):
        return f"Réponse de {self.utilisateur.username} à la question '{self.question.title}'"

class PropositionSelectionnee(models.Model):
    reponse = models.ForeignKey(ReponseUtilisateur, on_delete=models.CASCADE, related_name='propositions_selectionnees')
    proposition = models.ForeignKey(Proposition, on_delete=models.CASCADE, related_name='selections')
    
    class Meta:
        unique_together = ('reponse', 'proposition')
    
    def __str__(self):
        return f"{self.proposition.texte}"