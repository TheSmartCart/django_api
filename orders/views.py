from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Commande, ArticleCommande
from .serializers import CommandeListSerializer, CommandeDetailSerializer, ArticleCommandeSerializer
from enseignes.models import Produit

class CommandeViewSet(viewsets.ModelViewSet):
    queryset = Commande.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CommandeDetailSerializer
        return CommandeListSerializer
    
    def perform_create(self, serializer):
        serializer.save(utilisateur=self.request.user)
    
    @action(detail=True, methods=['post'])
    def add_article(self, request, pk=None):
        commande = self.get_object()
        produit_id = request.data.get('produit')
        quantite = int(request.data.get('quantite', 1))
        
        try:
            produit = Produit.objects.get(pk=produit_id)
            
            # Verify if product already exists in the order
            article_existant = ArticleCommande.objects.filter(commande=commande, produit=produit).first()
            
            if article_existant:
                article_existant.quantite += quantite
                article_existant.save()
                serializer = ArticleCommandeSerializer(article_existant)
            else:
                article = ArticleCommande.objects.create(
                    commande=commande,
                    produit=produit,
                    quantite=quantite,
                    prix_unitaire=produit.prix
                )
                serializer = ArticleCommandeSerializer(article)
                
            return Response(serializer.data)
        except Produit.DoesNotExist:
            return Response({"error": "Produit non trouvé"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'])
    def update_statut(self, request, pk=None):
        commande = self.get_object()
        nouveau_statut = request.data.get('statut')
        
        if nouveau_statut in [status[0] for status in Commande._meta.get_field('statut').choices]:
            commande.statut = nouveau_statut
            commande.save()
            return Response({"status": "Statut mis à jour"})
        else:
            return Response({"error": "Statut invalide"}, status=status.HTTP_400_BAD_REQUEST)

class ArticleCommandeViewSet(viewsets.ModelViewSet):
    queryset = ArticleCommande.objects.all()
    serializer_class = ArticleCommandeSerializer
    
    def perform_create(self, serializer):
        produit = serializer.validated_data['produit']
        serializer.save(prix_unitaire=produit.prix)