from django.db import models

class Brand(models.Model):
    name = models.CharField(max_length=100)
    logo_url = models.ImageField(upload_to='brands/logos/', blank=True, null=True)
    status = models.CharField(max_length=50, choices=[
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ], default='active')
    
    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='categories/images/', blank=True, null=True)
    stores = models.ManyToManyField('Store', related_name='categories', blank=True)
    status = models.CharField(max_length=50, default='active')
    
    def __str__(self):
        return self.name

class Store(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=10)
    city = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    
    brand = models.ForeignKey('Brand', on_delete=models.CASCADE, related_name='stores')
    
    opening_hours = models.TextField(blank=True, null=True, help_text="JSON format recommended for opening hours")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    
    status = models.CharField(max_length=50, choices=[
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ], default='active')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.city} ({self.brand.name})"
    
    class Meta:
        verbose_name = "Store"
        verbose_name_plural = "Stores"
        ordering = ['brand', 'city', 'name']

class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/images/', blank=True, null=True)
    stores = models.ManyToManyField('Store', related_name='products', blank=True)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, related_name='products')
    
    def __str__(self):
        return self.name
