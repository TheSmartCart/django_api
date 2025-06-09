from rest_framework import viewsets, status, permissions
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Question, Proposition, TypeQuestion, PropositionSelectionnee, ReponseUtilisateur
from .serializers import QuestionSerializer, PropositionSerializer, TypeQuestionSerializer, PropositionSelectionneeSerializer, ReponseUtilisateurSerializer, ReponseUtilisateurReadSerializer

class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def with_propositions(self, request, pk=None):
        """Endpoint pour obtenir une question avec toutes ses propositions."""
        question = self.get_object()
        serializer = self.get_serializer(question)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Endpoint pour filtrer les questions par type."""
        type_id = request.query_params.get('type_id', None)
        if type_id is not None:
            questions = Question.objects.filter(type_id=type_id)
            serializer = self.get_serializer(questions, many=True)
            return Response(serializer.data)
        return Response({"error": "Paramètre type_id requis"}, status=status.HTTP_400_BAD_REQUEST)

class PropositionViewSet(viewsets.ModelViewSet):
    queryset = Proposition.objects.all()
    serializer_class = PropositionSerializer
    
    @action(detail=False, methods=['get'])
    def by_question(self, request):
        """Endpoint pour filtrer les propositions par question."""
        question_id = request.query_params.get('question_id', None)
        if question_id is not None:
            propositions = Proposition.objects.filter(question_id=question_id)
            serializer = self.get_serializer(propositions, many=True)
            return Response(serializer.data)
        return Response({"error": "Paramètre question_id requis"}, status=status.HTTP_400_BAD_REQUEST)

class TypeQuestionViewSet(viewsets.ModelViewSet):
    queryset = TypeQuestion.objects.all()
    serializer_class = TypeQuestionSerializer

class ReponseUtilisateurViewSet(viewsets.ModelViewSet):
    queryset = ReponseUtilisateur.objects.all()
    serializer_class = ReponseUtilisateurSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return ReponseUtilisateur.objects.filter(utilisateur=user)
    
    def get_serializer_class(self):
        """Utilise le serializer de lecture pour les actions GET, et le serializer d'écriture pour les autres."""
        if self.action in ['list', 'retrieve']:
            return ReponseUtilisateurReadSerializer
        return ReponseUtilisateurSerializer
        
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def create(self, request, *args, **kwargs):
        is_many = isinstance(request.data, list)
        serializer = self.get_serializer(data=request.data, many=is_many, context=self.get_serializer_context())
        if not is_many:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        # Bulk : gestion partielle
        results = []
        errors = []
        for idx, item in enumerate(request.data):
            item_serializer = self.get_serializer(data=item, context=self.get_serializer_context())
            if item_serializer.is_valid():
                instance = item_serializer.save()
                results.append(self.get_serializer(instance).data)
            else:
                errors.append({"index": idx, "errors": item_serializer.errors})
        return Response({"created": results, "errors": errors}, status=status.HTTP_207_MULTI_STATUS)

class PropositionSelectionneeViewSet(viewsets.ModelViewSet):
    queryset = PropositionSelectionnee.objects.all()
    serializer_class = PropositionSelectionneeSerializer