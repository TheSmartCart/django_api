from rest_framework import viewsets
from .models import Question, Proposition, TypeQuestion
from .serializers import QuestionSerializer, PropositionSerializer, TypeQuestionSerializer, QuestionDetailSerializer

class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return QuestionDetailSerializer
        return QuestionSerializer

class PropositionViewSet(viewsets.ModelViewSet):
    queryset = Proposition.objects.all()
    serializer_class = PropositionSerializer

class TypeQuestionViewSet(viewsets.ModelViewSet):
    queryset = TypeQuestion.objects.all()
    serializer_class = TypeQuestionSerializer