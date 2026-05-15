from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404

from .models import Commande, ArticleCommande
from .serializers import (
    CommandeListSerializer,
    CommandeDetailSerializer,
    CommandeCreateSerializer,
    CommandePatchSerializer,
    StatutUpdateSerializer,
    ArticleCommandeSerializer,
)
from enseignes.models import Produit, Magasin

TRANSITIONS_AUTORISEES = {
    'en_attente':     ['en_preparation', 'prete', 'annulee'],
    'en_preparation': ['prete', 'annulee'],
    'prete':          ['recuperee', 'annulee'],
    'recuperee':      [],
    'annulee':        ['en_attente'],
}


class CommandeViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        return Commande.objects.filter(utilisateur=self.request.user)

    def get_serializer_class(self):
        if self.action in ('retrieve', 'update', 'partial_update'):
            return CommandeDetailSerializer
        if self.action == 'create':
            return CommandeCreateSerializer
        return CommandeListSerializer

    def update(self, request, *args, **kwargs):
        return Response(
            {"error": "Méthode PUT non supportée. Utilisez PATCH."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def partial_update(self, request, *args, **kwargs):
        commande = self.get_object()

        if commande.statut != 'en_attente':
            return Response(
                {"error": f"Seules les commandes 'en_attente' peuvent être modifiées. Statut actuel : '{commande.statut}'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = CommandePatchSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        if 'statut' in data:
            nouveau_statut = data['statut']
            transitions_possibles = TRANSITIONS_AUTORISEES.get(commande.statut, [])
            if nouveau_statut not in transitions_possibles:
                return Response(
                    {
                        "error": (
                            f"Transition de '{commande.statut}' vers '{nouveau_statut}' non autorisée. "
                            f"Transitions possibles : {transitions_possibles or 'aucune'}."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            commande.statut = nouveau_statut

        if 'articles' in data:
            commande.articles.all().delete()
            self._create_articles(commande, data['articles'])

        commande.save()

        out = CommandeDetailSerializer(commande, context={'request': request})
        return Response(out.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = CommandeCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        magasin = get_object_or_404(Magasin, pk=data['magasin'])

        nouveau_statut = data.get('statut', 'en_attente')

        commande_existante = Commande.objects.filter(
            utilisateur=request.user,
            magasin=magasin,
            statut='en_attente',
        ).first()

        if commande_existante:
            commande_existante.statut = nouveau_statut
            commande_existante.save()
            commande_existante.articles.all().delete()
            self._create_articles(commande_existante, data['articles'])

            out = CommandeDetailSerializer(commande_existante, context={'request': request})
            return Response(out.data, status=status.HTTP_200_OK)
        else:
            if nouveau_statut != 'en_attente':
                return Response(
                    {"error": "Aucune commande en attente à modifier. Une commande ne peut pas être créée directement avec ce statut."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            derniere_commande = Commande.objects.filter(
                utilisateur=request.user,
                magasin=magasin
            ).order_by('-date_creation').first()

            if derniere_commande and derniere_commande.statut in ['en_preparation', 'prete']:
                if len(data['articles']) == derniere_commande.articles.count():
                    out = CommandeDetailSerializer(derniere_commande, context={'request': request})
                    return Response(out.data, status=status.HTTP_200_OK)

            commande = Commande.objects.create(
                utilisateur=request.user,
                magasin=magasin,
                statut='en_attente',
            )
            self._create_articles(commande, data['articles'])

            out = CommandeDetailSerializer(commande, context={'request': request})
            return Response(out.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['patch'], url_path='modifier_statut')
    def modifier_statut(self, request, pk=None):
        commande = self.get_object()
        serializer = StatutUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        nouveau_statut = serializer.validated_data['statut']
        statut_actuel = commande.statut

        transitions_possibles = TRANSITIONS_AUTORISEES.get(statut_actuel, [])
        if nouveau_statut not in transitions_possibles:
            return Response(
                {
                    "error": (
                        f"Transition de '{statut_actuel}' vers '{nouveau_statut}' non autorisée. "
                        f"Transitions possibles depuis '{statut_actuel}' : {transitions_possibles or 'aucune'}."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        commande.statut = nouveau_statut
        commande.save()

        out = CommandeDetailSerializer(commande, context={'request': request})
        return Response(out.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path=r'en_attente_magasin/(?P<magasin_id>\d+)')
    def en_attente_par_magasin(self, request, magasin_id=None):
        commande = Commande.objects.filter(
            utilisateur=request.user,
            magasin_id=magasin_id,
            statut='en_attente'
        ).first()

        if not commande:
            return Response({"error": "Aucune commande en attente pour ce magasin."}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(commande)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        commande = self.get_object()

        if commande.statut == 'recuperee':
            return Response(
                {"error": "Une commande récupérée ne peut pas être annulée."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if commande.statut == 'annulee':
            return Response(
                {"error": "Cette commande est déjà annulée."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        commande.statut = 'annulee'
        commande.save()

        return Response(
            {"message": "Commande annulée avec succès."},
            status=status.HTTP_200_OK,
        )

    @staticmethod
    def _create_articles(commande, articles_data):
        enseigne = commande.magasin.enseigne
        for article_data in articles_data:
            identifiant = str(article_data['produit'])
            
            produit = None
            if identifiant.isdigit():
                produit = Produit.objects.filter(id=int(identifiant), enseigne=enseigne).first()
                
            if not produit:
                from django.shortcuts import get_object_or_404
                produit = get_object_or_404(Produit, nom=identifiant, enseigne=enseigne)
                
            ArticleCommande.objects.create(
                commande=commande,
                produit=produit,
                quantite=article_data['quantite'],
                prix_unitaire=produit.prix,
            )


class ArticleCommandeViewSet(viewsets.ModelViewSet):
    queryset = ArticleCommande.objects.all()
    serializer_class = ArticleCommandeSerializer
    
    def perform_create(self, serializer):
        produit = serializer.validated_data['produit']
        serializer.save(prix_unitaire=produit.prix)