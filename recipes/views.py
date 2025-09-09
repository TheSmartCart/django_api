from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import transaction
from .models import (Recette, Ingredient, IngredientRecette, Etape, Ustensile, UstensileRecette)
from .serializers import (RecetteSerializer, IngredientSerializer, 
                         IngredientRecetteSerializer, EtapeSerializer, UstensileSerializer, UstensileRecetteSerializer)

class RecetteViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = RecetteSerializer
    
    def get_queryset(self):
        """Retourne uniquement les recettes appartenant à l'utilisateur authentifié."""
        user = getattr(self.request, 'user', None)
        if user and user.is_authenticated:
            return Recette.objects.filter(utilisateur=user)
        return Recette.objects.none()

    def perform_create(self, serializer):
        """Assigne automatiquement l'utilisateur authentifié à la recette lors de la création."""
        serializer.save(utilisateur=self.request.user)

    def create(self, request, *args, **kwargs):
        """
        Crée une recette et, si fournis, ses ustensiles (par nom) et ses étapes.
        - ustensiles: liste de strings (noms) ou d'objets {"nom": "..."} ou {"id": 1}
        - etapes: liste d'objets {"description": str, "ordre"?: int, "statut"?: str}
        """
        payload = request.data.copy()
        ustensiles_payload = payload.pop('ustensiles', [])
        etapes_payload = payload.pop('etapes', [])
        serializer = self.get_serializer(data=payload)
        serializer.is_valid(raise_exception=True)

        # Normalisation des ustensiles
        if isinstance(ustensiles_payload, str):
            ustensiles_payload = [x.strip() for x in ustensiles_payload.split(',') if x.strip()]
        if not isinstance(ustensiles_payload, list):
            ustensiles_payload = []
        if not isinstance(etapes_payload, list):
            etapes_payload = []

        with transaction.atomic():
            recette = serializer.save(utilisateur=request.user)

            # Ustensiles: get or create par nom ou récupérer par id
            for item in ustensiles_payload:
                ust = None
                if isinstance(item, dict):
                    if 'id' in item:
                        try:
                            ust = Ustensile.objects.get(id=item['id'])
                        except Ustensile.DoesNotExist:
                            continue
                    elif 'nom' in item and item['nom']:
                        ust, _ = Ustensile.objects.get_or_create(nom=item['nom'].strip())
                elif isinstance(item, str) and item.strip():
                    ust, _ = Ustensile.objects.get_or_create(nom=item.strip())
                if ust:
                    UstensileRecette.objects.get_or_create(recette=recette, ustensile=ust)

            # Étapes: créer avec ordre si fourni, sinon incrémental
            current_max = 0
            for idx, step in enumerate(etapes_payload, start=1):
                if not isinstance(step, dict):
                    continue
                description = step.get('description')
                if not description:
                    continue
                ordre = step.get('ordre')
                if isinstance(ordre, int) and ordre > 0:
                    use_ordre = ordre
                else:
                    current_max += 1
                    use_ordre = current_max
                statut = step.get('statut') or 'actif'
                Etape.objects.create(recette=recette, description=description, ordre=use_ordre, statut=statut)

        # Re-serialize pour retourner les données enrichies (ustensiles, etapes)
        output = RecetteSerializer(recette, context=self.get_serializer_context()).data
        headers = self.get_success_headers(serializer.data)
        return Response(output, status=status.HTTP_201_CREATED, headers=headers)

class EtapeViewSet(viewsets.ModelViewSet):
    queryset = Etape.objects.all()
    serializer_class = EtapeSerializer

class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer

class IngredientRecetteViewSet(viewsets.ModelViewSet):
    queryset = IngredientRecette.objects.all()
    serializer_class = IngredientRecetteSerializer

class UstensileViewSet(viewsets.ModelViewSet):
    queryset = Ustensile.objects.all()
    serializer_class = UstensileSerializer

class UstensileRecetteViewSet(viewsets.ModelViewSet):
    queryset = UstensileRecette.objects.all()
    serializer_class = UstensileRecetteSerializer