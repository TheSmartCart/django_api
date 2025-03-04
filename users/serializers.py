from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import CustomUser

class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'image_profil', 'first_name', 'last_name', 'password']

    def create(self, validated_data):
        """Créer un utilisateur avec un mot de passe hashé"""
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)