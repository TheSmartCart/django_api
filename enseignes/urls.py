from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EnseigneViewSet, ProduitViewSet, CategorieViewSet, MagasinViewSet

router = DefaultRouter()
router.register(r'enseignes', EnseigneViewSet)
router.register(r'produits', ProduitViewSet)
router.register(r'categories', CategorieViewSet)
router.register(r'magasins', MagasinViewSet)

urlpatterns = [
    path('', include(router.urls)),
]