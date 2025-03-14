from rest_framework import serializers
from .models import Question, Proposition, TypeQuestion, PropositionSelectionnee, ReponseUtilisateur

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

class PropositionSelectionneeSerializer(serializers.ModelSerializer):
    texte_proposition = serializers.ReadOnlyField(source='proposition.texte')
    
    class Meta:
        model = PropositionSelectionnee
        fields = ['id', 'proposition', 'texte_proposition']

class ReponseUtilisateurSerializer(serializers.ModelSerializer):
    propositions_selectionnees = PropositionSelectionneeSerializer(many=True, required=False)
    nom_utilisateur = serializers.ReadOnlyField(source='utilisateur.username')
    titre_question = serializers.ReadOnlyField(source='question.title')
    
    class Meta:
        model = ReponseUtilisateur
        fields = ['id', 'utilisateur', 'nom_utilisateur', 'question', 'titre_question', 
                 'date_creation', 'valeur_numerique', 'propositions_selectionnees']
    
    def validate(self, data):
        # Vérifier qu'au moins un des champs valeur_numerique ou propositions_selectionnees existe
        propositions_data = self.initial_data.get('propositions_selectionnees', [])
        if data.get('valeur_numerique') is None and not propositions_data:
            raise serializers.ValidationError("Vous devez fournir soit une valeur numérique, soit au moins une proposition sélectionnée.")
        
        # Vérifier qu'on n'a pas à la fois une valeur numérique et des propositions sélectionnées
        if data.get('valeur_numerique') is not None and propositions_data:
            raise serializers.ValidationError("Vous ne pouvez pas fournir à la fois une valeur numérique et des propositions sélectionnées.")
        
        return data
    
    def create(self, validated_data):
        # Traitement pour créer la réponse de l'utilisateur
        propositions_selectionnees = validated_data.pop('propositions_selectionnees')
        reponse = ReponseUtilisateur.objects.create(**validated_data)

        # Ajouter les propositions sélectionnées à la réponse
        reponse.propositions_selectionnees.set(propositions_selectionnees)
        reponse.save()
        return reponse