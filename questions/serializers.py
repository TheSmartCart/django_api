from rest_framework import serializers
from .models import Question, Proposition, TypeQuestion, PropositionSelectionnee, ReponseUtilisateur

class PropositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proposition
        fields = ['id', 'texte', 'statut', 'image']

class TypeQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TypeQuestion
        fields = '__all__'

class QuestionSerializer(serializers.ModelSerializer):
    propositions = PropositionSerializer(many=True, required=False)
    type_nom = serializers.ReadOnlyField(source='type.nom', read_only=True)
    
    class Meta:
        model = Question
        fields = ['id', 'title', 'description', 'type', 'type_nom', 'dateCreation', 'status', 'min_value', 'max_value', 'propositions']
    
    def create(self, validated_data):
        propositions_data = validated_data.pop('propositions', [])
        question = Question.objects.create(**validated_data)
        
        for proposition_data in propositions_data:
            Proposition.objects.create(question=question, **proposition_data)
        
        return question
    
    def update(self, instance, validated_data):
        propositions_data = validated_data.pop('propositions', [])
        
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.type = validated_data.get('type', instance.type)
        instance.status = validated_data.get('status', instance.status)
        instance.min_value = validated_data.get('min_value', instance.min_value)
        instance.max_value = validated_data.get('max_value', instance.max_value)
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
    propositions_selectionnees = PropositionSelectionneeSerializer(many=True, required=False, write_only=True)
    nom_utilisateur = serializers.ReadOnlyField(source='utilisateur.username')
    titre_question = serializers.ReadOnlyField(source='question.title')
    
    class Meta:
        model = ReponseUtilisateur
        fields = ['id', 'utilisateur', 'nom_utilisateur', 'question', 'titre_question', 
                 'date_creation', 'valeur_numerique', 'propositions_selectionnees']
        read_only_fields = ['utilisateur']

    def validate(self, data):
        if isinstance(self.initial_data, list):
            return data
            
        # Support partial updates (PATCH) by merging with self.instance values
        if self.instance:
            question = data['question'] if 'question' in data else self.instance.question
            valeur_numerique = data['valeur_numerique'] if 'valeur_numerique' in data else self.instance.valeur_numerique
            
            if 'propositions_selectionnees' in self.initial_data:
                propositions_data = self.initial_data.get('propositions_selectionnees', [])
                has_propositions = len(propositions_data) > 0
            else:
                propositions_data = []
                has_propositions = self.instance.propositions_selectionnees.exists()
        else:
            question = data.get('question')
            valeur_numerique = data.get('valeur_numerique')
            propositions_data = self.initial_data.get('propositions_selectionnees', [])
            has_propositions = len(propositions_data) > 0

        # Vérification du type de question
        type_nom = getattr(question.type, 'nom', None) if question else None
        is_slider = type_nom and type_nom.lower() == 'slider'

        if is_slider:
            # Pour les sliders, il faut une valeur numérique et aucune proposition
            if valeur_numerique is None:
                raise serializers.ValidationError("Cette question attend une valeur numérique.")
            if has_propositions:
                raise serializers.ValidationError("Vous ne pouvez pas sélectionner de proposition pour une question de type slider.")
        else:
            # Pour les autres types, il faut des propositions et pas de valeur numérique
            if not has_propositions:
                raise serializers.ValidationError("Cette question attend une ou plusieurs propositions sélectionnées.")
            if valeur_numerique is not None:
                raise serializers.ValidationError("Vous ne pouvez pas fournir une valeur numérique pour cette question.")

        # Vérification min/max pour les sliders
        if is_slider and question and valeur_numerique is not None:
            if question.min_value is not None and valeur_numerique < question.min_value:
                raise serializers.ValidationError(f"La valeur numérique doit être supérieure ou égale à {question.min_value}.")
            if question.max_value is not None and valeur_numerique > question.max_value:
                raise serializers.ValidationError(f"La valeur numérique doit être inférieure ou égale à {question.max_value}.")

        # Vérification que chaque proposition appartient bien à la question
        if not is_slider and question and propositions_data:
            question_propositions_ids = set(question.propositions.values_list('id', flat=True))
            for prop in propositions_data:
                prop_id = prop.get('proposition')
                if prop_id not in question_propositions_ids:
                    raise serializers.ValidationError(f"La proposition {prop_id} n'appartient pas à la question {question.id}.")

        return data

    def create(self, validated_data):
        # Récupérer l'utilisateur à partir du contexte (injecté par la vue)
        utilisateur = self.context['request'].user
        validated_data['utilisateur'] = utilisateur
        
        # Extraire les propositions_data avant de créer la réponse
        propositions_data = validated_data.pop('propositions_selectionnees', [])
        
        # Créer l'objet ReponseUtilisateur
        reponse = ReponseUtilisateur.objects.create(
            utilisateur=validated_data['utilisateur'],
            question=validated_data['question'],
            valeur_numerique=validated_data.get('valeur_numerique')
        )
        
        # Maintenant ajouter les propositions
        for proposition_data in propositions_data:
            proposition_id = proposition_data.get('proposition')
            if isinstance(proposition_id, Proposition):
                proposition_id = proposition_id.id
            if proposition_id:
                PropositionSelectionnee.objects.create(
                    reponse=reponse,
                    proposition_id=proposition_id
                )
        
        return reponse
        
    def update(self, instance, validated_data):
        # Vérifier que l'utilisateur actuel est bien le créateur de la réponse
        request = self.context.get('request')
        if request and request.user != instance.utilisateur:
            raise serializers.ValidationError("Vous ne pouvez pas modifier une réponse qui ne vous appartient pas.")
            
        # Gérer la mise à jour des champs simples
        instance.valeur_numerique = validated_data.get('valeur_numerique', instance.valeur_numerique)
        instance.save()
        
        # Gérer la mise à jour des propositions sélectionnées
        propositions_data = self.initial_data.get('propositions_selectionnees', [])
        if 'propositions_selectionnees' in self.initial_data:
            # Supprimer les anciennes propositions
            instance.propositions_selectionnees.all().delete()
            
            # Ajouter les nouvelles propositions
            for proposition_data in propositions_data:
                proposition_id = proposition_data.get('proposition')
                if proposition_id:
                    PropositionSelectionnee.objects.create(
                        reponse=instance,
                        proposition_id=proposition_id
                    )
        
        return instance

class ReponseUtilisateurReadSerializer(serializers.ModelSerializer):
    questionText = serializers.ReadOnlyField(source='question.title')
    selectedOptions = serializers.SerializerMethodField()
    sliderValue = serializers.ReadOnlyField(source='valeur_numerique')
    
    class Meta:
        model = ReponseUtilisateur
        fields = ['questionText', 'selectedOptions', 'sliderValue']
    
    def get_selectedOptions(self, obj):
        """Retourne la liste des textes des propositions sélectionnées."""
        return [prop_sel.proposition.texte for prop_sel in obj.propositions_selectionnees.all()]