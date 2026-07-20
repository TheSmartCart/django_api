from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import transaction
from .models import (Recipe, Ingredient, RecipeIngredient, Step, Utensil, RecipeUtensil)
from .serializers import (RecipeSerializer, IngredientSerializer, 
                         RecipeIngredientSerializer, StepSerializer, UtensilSerializer, RecipeUtensilSerializer)

class RecipeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = RecipeSerializer
    
    def get_queryset(self):
        user = getattr(self.request, 'user', None)
        if user and user.is_authenticated:
            return Recipe.objects.filter(user=user)
        return Recipe.objects.none()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        payload = request.data.copy()
        utensils_payload = payload.pop('utensils', payload.pop('ustensiles', []))
        steps_payload = payload.pop('steps', payload.pop('etapes', []))
        serializer = self.get_serializer(data=payload)
        serializer.is_valid(raise_exception=True)

        if isinstance(utensils_payload, str):
            utensils_payload = [x.strip() for x in utensils_payload.split(',') if x.strip()]
        if not isinstance(utensils_payload, list):
            utensils_payload = []
        if not isinstance(steps_payload, list):
            steps_payload = []

        with transaction.atomic():
            recipe = serializer.save(user=request.user)

            for item in utensils_payload:
                utensil = None
                if isinstance(item, dict):
                    if 'id' in item:
                        try:
                            utensil = Utensil.objects.get(id=item['id'])
                        except Utensil.DoesNotExist:
                            continue
                    elif 'name' in item and item['name']:
                        utensil, _ = Utensil.objects.get_or_create(name=item['name'].strip())
                    elif 'nom' in item and item['nom']:
                        utensil, _ = Utensil.objects.get_or_create(name=item['nom'].strip())
                elif isinstance(item, str) and item.strip():
                    utensil, _ = Utensil.objects.get_or_create(name=item.strip())
                if utensil:
                    RecipeUtensil.objects.get_or_create(recipe=recipe, utensil=utensil)

            current_max = 0
            for idx, step_item in enumerate(steps_payload, start=1):
                if not isinstance(step_item, dict):
                    continue
                description = step_item.get('description')
                if not description:
                    continue
                step_number = step_item.get('step_number') or step_item.get('ordre')
                if isinstance(step_number, int) and step_number > 0:
                    use_step_number = step_number
                else:
                    current_max += 1
                    use_step_number = current_max
                status_val = step_item.get('status') or step_item.get('statut') or 'active'
                Step.objects.create(recipe=recipe, description=description, step_number=use_step_number, status=status_val)

        output = RecipeSerializer(recipe, context=self.get_serializer_context()).data
        headers = self.get_success_headers(serializer.data)
        return Response(output, status=status.HTTP_201_CREATED, headers=headers)

class StepViewSet(viewsets.ModelViewSet):
    queryset = Step.objects.all()
    serializer_class = StepSerializer

class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer

class RecipeIngredientViewSet(viewsets.ModelViewSet):
    queryset = RecipeIngredient.objects.all()
    serializer_class = RecipeIngredientSerializer

class UtensilViewSet(viewsets.ModelViewSet):
    queryset = Utensil.objects.all()
    serializer_class = UtensilSerializer

class RecipeUtensilViewSet(viewsets.ModelViewSet):
    queryset = RecipeUtensil.objects.all()
    serializer_class = RecipeUtensilSerializer