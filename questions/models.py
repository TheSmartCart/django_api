from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class QuestionType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.name

class Question(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    type = models.ForeignKey(QuestionType, on_delete=models.CASCADE, related_name='questions')
    created_at = models.DateTimeField(auto_now_add=True)
    min_value = models.FloatField(null=True, blank=True, help_text="Minimum value for slider questions")
    max_value = models.FloatField(null=True, blank=True, help_text="Maximum value for slider questions")
    status = models.CharField(max_length=20, choices=[
        ('active', 'Active'),
        ('draft', 'Draft'),
        ('inactive', 'Inactive')
    ], default='active')
    
    def __str__(self):
        return self.title

class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=255)
    status = models.CharField(max_length=20, default='active')
    image = models.ImageField(upload_to='options/', blank=True, null=True)
    
    def __str__(self):
        return self.text

class UserAnswer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='user_answers')
    created_at = models.DateTimeField(auto_now_add=True)
    numeric_value = models.FloatField(null=True, blank=True)
    
    def clean(self):
        from django.core.exceptions import ValidationError
        
        if self.pk is None:
            return
            
        if self.numeric_value is None and not self.selected_options.exists():
            raise ValidationError("You must provide either a numeric value or at least one selected option.")
        
        if self.numeric_value is not None and self.selected_options.exists():
            raise ValidationError("You cannot provide both a numeric value and selected options.")
    
    def save(self, *args, **kwargs):
        self.clean()
        super(UserAnswer, self).save(*args, **kwargs)
    
    def __str__(self):
        return f"Answer from {self.user.username} to question '{self.question.title}'"

class SelectedOption(models.Model):
    user_answer = models.ForeignKey(UserAnswer, on_delete=models.CASCADE, related_name='selected_options')
    option = models.ForeignKey(Option, on_delete=models.CASCADE, related_name='selections')
    
    class Meta:
        unique_together = ('user_answer', 'option')
    
    def __str__(self):
        return f"{self.option.text}"