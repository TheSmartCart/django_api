from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import CustomUser

class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    access = serializers.SerializerMethodField(required=False)
    refresh = serializers.SerializerMethodField(required=False)

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'image_profil', 'first_name', 'last_name', 'password', 'access', 'refresh']

    def get_access(self, obj):
        return getattr(obj, 'access', None)

    def get_refresh(self, obj):
        return getattr(obj, 'refresh', None)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if not data.get('access'):
            data.pop('access', None)
        if not data.get('refresh'):
            data.pop('refresh', None)
        return data

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)