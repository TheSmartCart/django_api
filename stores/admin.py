from django.contrib import admin
from .models import Brand, Product, Category, Store

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'status')
    search_fields = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'category')
    list_filter = ('stores', 'category')
    search_fields = ('name', 'description')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'status')
    list_filter = ('stores', 'status')
    search_fields = ('name',)

@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'city', 'postal_code', 'status')
    list_filter = ('brand', 'status', 'city')
    search_fields = ('name', 'address', 'city', 'postal_code')
    fieldsets = (
        (None, {
            'fields': ('name', 'brand')
        }),
        ('Location', {
            'fields': ('address', 'postal_code', 'city', 'latitude', 'longitude')
        }),
        ('Contact', {
            'fields': ('phone', 'email')
        }),
        ('Information', {
            'fields': ('opening_hours', 'status')
        }),
    )
