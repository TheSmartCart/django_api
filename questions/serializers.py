from rest_framework import serializers
from .models import Question, Proposition, TypeQuestion

class PropositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proposition
        fields = '__all__'

class TypeQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TypeQuestion
        fields = '__all__'

class QuestionSerializer(serializers.ModelSerializer):
    propositions = PropositionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Question
        fields = '__all__'

class QuestionDetailSerializer(serializers.ModelSerializer):
    propositions = PropositionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Question
        fields = '__all__'