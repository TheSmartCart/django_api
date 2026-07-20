from rest_framework import serializers
from .models import Brand, Product, Category, Store

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'image', 'status', 'stores']

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'image', 'category', 'category_name', 'stores']

class StoreSerializer(serializers.ModelSerializer):
    brand_name = serializers.ReadOnlyField(source='brand.name')
    
    class Meta:
        model = Store
        fields = ['id', 'name', 'brand', 'brand_name', 'address', 'postal_code', 
                  'city', 'phone', 'email', 'opening_hours', 'latitude', 
                  'longitude', 'status', 'created_at', 'updated_at']

class StoreForBrandSerializer(serializers.ModelSerializer):
    postalCode = serializers.CharField(source='postal_code')
    latitude = serializers.FloatField(allow_null=True)
    longitude = serializers.FloatField(allow_null=True)
    brandId = serializers.IntegerField(source='brand_id', read_only=True)

    class Meta:
        model = Store
        fields = ['id', 'name', 'address', 'city', 'postalCode', 'latitude', 'longitude', 'brandId']

class BrandSerializer(serializers.ModelSerializer):
    stores = StoreForBrandSerializer(many=True, read_only=True)

    class Meta:
        model = Brand
        fields = ['id', 'name', 'logo_url', 'stores']
