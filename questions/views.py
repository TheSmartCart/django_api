from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Question, Proposition, TypeQuestion, PropositionSelectionnee, ReponseUtilisateur
from .serializers import QuestionSerializer, PropositionSerializer, TypeQuestionSerializer, PropositionSelectionneeSerializer, ReponseUtilisateurSerializer

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
    
    def get_queryset(self):
        queryset = ReponseUtilisateur.objects.all()
        utilisateur_id = self.request.query_params.get('utilisateur_id', None)
        question_id = self.request.query_params.get('question_id', None)
        
        if utilisateur_id is not None:
            queryset = queryset.filter(utilisateur_id=utilisateur_id)
        if question_id is not None:
            queryset = queryset.filter(question_id=question_id)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def mes_reponses(self, request):
        """Endpoint pour obtenir toutes les réponses de l'utilisateur connecté."""
        if request.user.is_authenticated:
            reponses = ReponseUtilisateur.objects.filter(utilisateur=request.user)
            serializer = self.get_serializer(reponses, many=True)
            return Response(serializer.data)
        return Response({"error": "Utilisateur non connecté"}, status=status.HTTP_401_UNAUTHORIZED)

class PropositionSelectionneeViewSet(viewsets.ModelViewSet):
    queryset = PropositionSelectionnee.objects.all()
    serializer_class = PropositionSelectionneeSerializer