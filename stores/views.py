from rest_framework import viewsets
from .models import Brand, Product, Category, Store
from .serializers import BrandSerializer, ProductSerializer, CategorySerializer, StoreSerializer

class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all().prefetch_related('stores')
    serializer_class = BrandSerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    
    def get_queryset(self):
        queryset = Product.objects.all()
        store = self.request.query_params.get('store')
        if store:
            queryset = queryset.filter(stores__id=store)
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category_id=category)
        return queryset.distinct()

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    
    def get_queryset(self):
        queryset = Category.objects.all()
        store = self.request.query_params.get('store')
        if store:
            queryset = queryset.filter(stores__id=store)
        return queryset.distinct()

class StoreViewSet(viewsets.ModelViewSet):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    
    def get_queryset(self):
        queryset = Store.objects.all()
        brand = self.request.query_params.get('brand')
        if brand:
            queryset = queryset.filter(brand_id=brand)
        city = self.request.query_params.get('city')
        if city:
            queryset = queryset.filter(city=city)
        postal_code = self.request.query_params.get('postal_code')
        if postal_code:
            queryset = queryset.filter(postal_code=postal_code)
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)
        return queryset
