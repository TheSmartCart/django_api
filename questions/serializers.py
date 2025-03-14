from rest_framework import serializers
from .models import Question, Proposition, TypeQuestion

class PropositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proposition
        fields = ['id', 'texte', 'statut']

class TypeQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TypeQuestion
        fields = '__all__'

class QuestionSerializer(serializers.ModelSerializer):
    propositions = PropositionSerializer(many=True, required=False)
    type_nom = serializers.ReadOnlyField(source='type.nom', read_only=True)
    
    class Meta:
        model = Question
        fields = ['id', 'title', 'type', 'type_nom', 'dateCreation', 'status', 'propositions']
    
    def create(self, validated_data):
        propositions_data = validated_data.pop('propositions', [])
        question = Question.objects.create(**validated_data)
        
        for proposition_data in propositions_data:
            Proposition.objects.create(question=question, **proposition_data)
        
        return question
    
    def update(self, instance, validated_data):
        propositions_data = validated_data.pop('propositions', [])
        
        instance.title = validated_data.get('title', instance.title)
        instance.type = validated_data.get('type', instance.type)
        instance.status = validated_data.get('status', instance.status)
        instance.save()
        
        if propositions_data:
            instance.propositions.all().delete()
        
        return instance