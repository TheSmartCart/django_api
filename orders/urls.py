from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CommandeViewSet, ArticleCommandeViewSet

router = DefaultRouter()
router.register(r'commandes', CommandeViewSet)
router.register(r'articles-commande', ArticleCommandeViewSet)

urlpatterns = [
    path('', include(router.urls)),
]