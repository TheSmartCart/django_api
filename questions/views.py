from rest_framework import viewsets, status, permissions
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Question, Option, QuestionType, SelectedOption, UserAnswer
from .serializers import (
    QuestionSerializer,
    OptionSerializer,
    QuestionTypeSerializer,
    SelectedOptionSerializer,
    UserAnswerSerializer,
    UserAnswerReadSerializer
)

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
    def with_options(self, request, pk=None):
        """Endpoint to get a question with all its options."""
        question = self.get_object()
        serializer = self.get_serializer(question)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Endpoint to filter questions by type."""
        type_id = request.query_params.get('type_id', None)
        if type_id is not None:
            questions = Question.objects.filter(type_id=type_id)
            serializer = self.get_serializer(questions, many=True)
            return Response(serializer.data)
        return Response({"error": "type_id parameter is required"}, status=status.HTTP_400_BAD_REQUEST)

class OptionViewSet(viewsets.ModelViewSet):
    queryset = Option.objects.all()
    serializer_class = OptionSerializer
    
    @action(detail=False, methods=['get'])
    def by_question(self, request):
        """Endpoint to filter options by question."""
        question_id = request.query_params.get('question_id', None)
        if question_id is not None:
            options = Option.objects.filter(question_id=question_id)
            serializer = self.get_serializer(options, many=True)
            return Response(serializer.data)
        return Response({"error": "question_id parameter is required"}, status=status.HTTP_400_BAD_REQUEST)

class QuestionTypeViewSet(viewsets.ModelViewSet):
    queryset = QuestionType.objects.all()
    serializer_class = QuestionTypeSerializer

class UserAnswerViewSet(viewsets.ModelViewSet):
    queryset = UserAnswer.objects.all()
    serializer_class = UserAnswerSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return UserAnswer.objects.filter(user=user)
    
    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return UserAnswerReadSerializer
        return UserAnswerSerializer
        
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

class SelectedOptionViewSet(viewsets.ModelViewSet):
    queryset = SelectedOption.objects.all()
    serializer_class = SelectedOptionSerializer