from rest_framework import serializers
from .models import Question, Option, QuestionType, SelectedOption, UserAnswer

class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ['id', 'text', 'status', 'image']

class QuestionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionType
        fields = '__all__'

class QuestionSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True, required=False)
    type_name = serializers.ReadOnlyField(source='type.name', read_only=True)
    
    class Meta:
        model = Question
        fields = ['id', 'title', 'description', 'type', 'type_name', 'created_at', 'status', 'min_value', 'max_value', 'options']
    
    def create(self, validated_data):
        options_data = validated_data.pop('options', [])
        question = Question.objects.create(**validated_data)
        
        for option_data in options_data:
            Option.objects.create(question=question, **option_data)
        
        return question
    
    def update(self, instance, validated_data):
        options_data = validated_data.pop('options', [])
        
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.type = validated_data.get('type', instance.type)
        instance.status = validated_data.get('status', instance.status)
        instance.min_value = validated_data.get('min_value', instance.min_value)
        instance.max_value = validated_data.get('max_value', instance.max_value)
        instance.save()
        
        if options_data:
            instance.options.all().delete()
        
        return instance

class SelectedOptionSerializer(serializers.ModelSerializer):
    option_text = serializers.ReadOnlyField(source='option.text')
    
    class Meta:
        model = SelectedOption
        fields = ['id', 'option', 'option_text']

class UserAnswerSerializer(serializers.ModelSerializer):
    selected_options = SelectedOptionSerializer(many=True, required=False, write_only=True)
    user_name = serializers.ReadOnlyField(source='user.username')
    question_title = serializers.ReadOnlyField(source='question.title')
    
    class Meta:
        model = UserAnswer
        fields = ['id', 'user', 'user_name', 'question', 'question_title', 
                  'created_at', 'numeric_value', 'selected_options']
        read_only_fields = ['user']

    def validate(self, data):
        if isinstance(self.initial_data, list):
            return data
            
        if self.instance:
            question = data['question'] if 'question' in data else self.instance.question
            numeric_value = data['numeric_value'] if 'numeric_value' in data else self.instance.numeric_value
            
            if 'selected_options' in self.initial_data:
                options_data = self.initial_data.get('selected_options', [])
                has_options = len(options_data) > 0
            else:
                options_data = []
                has_options = self.instance.selected_options.exists()
        else:
            question = data.get('question')
            numeric_value = data.get('numeric_value')
            options_data = self.initial_data.get('selected_options', [])
            has_options = len(options_data) > 0

        type_name = getattr(question.type, 'name', None) if question else None
        is_slider = type_name and type_name.lower() == 'slider'

        if is_slider:
            if numeric_value is None:
                raise serializers.ValidationError("This question expects a numeric value.")
            if has_options:
                raise serializers.ValidationError("You cannot select options for a slider question.")
        else:
            if not has_options:
                raise serializers.ValidationError("This question expects one or more selected options.")
            if numeric_value is not None:
                raise serializers.ValidationError("You cannot provide a numeric value for this question.")

        if is_slider and question and numeric_value is not None:
            if question.min_value is not None and numeric_value < question.min_value:
                raise serializers.ValidationError(f"Numeric value must be greater than or equal to {question.min_value}.")
            if question.max_value is not None and numeric_value > question.max_value:
                raise serializers.ValidationError(f"Numeric value must be less than or equal to {question.max_value}.")

        if not is_slider and question and options_data:
            question_options_ids = set(question.options.values_list('id', flat=True))
            for opt in options_data:
                opt_id = opt.get('option')
                if opt_id not in question_options_ids:
                    raise serializers.ValidationError(f"Option {opt_id} does not belong to question {question.id}.")

        return data

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        
        options_data = validated_data.pop('selected_options', [])
        
        user_answer = UserAnswer.objects.create(
            user=validated_data['user'],
            question=validated_data['question'],
            numeric_value=validated_data.get('numeric_value')
        )
        
        for option_data in options_data:
            option_id = option_data.get('option')
            if isinstance(option_id, Option):
                option_id = option_id.id
            if option_id:
                SelectedOption.objects.create(
                    user_answer=user_answer,
                    option_id=option_id
                )
        
        return user_answer
        
    def update(self, instance, validated_data):
        request = self.context.get('request')
        if request and request.user != instance.user:
            raise serializers.ValidationError("You cannot modify an answer that does not belong to you.")
            
        instance.numeric_value = validated_data.get('numeric_value', instance.numeric_value)
        instance.save()
        
        options_data = self.initial_data.get('selected_options', [])
        if 'selected_options' in self.initial_data:
            instance.selected_options.all().delete()
            
            for option_data in options_data:
                option_id = option_data.get('option')
                if option_id:
                    SelectedOption.objects.create(
                        user_answer=instance,
                        option_id=option_id
                    )
        
        return instance

class UserAnswerReadSerializer(serializers.ModelSerializer):
    questionText = serializers.ReadOnlyField(source='question.title')
    selectedOptions = serializers.SerializerMethodField()
    sliderValue = serializers.ReadOnlyField(source='numeric_value')
    
    class Meta:
        model = UserAnswer
        fields = ['questionText', 'selectedOptions', 'sliderValue']
    
    def get_selectedOptions(self, obj):
        return [selected_opt.option.text for selected_opt in obj.selected_options.all()]