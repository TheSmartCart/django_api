from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from questions.models import Question, Option, QuestionType, UserAnswer, SelectedOption

User = get_user_model()

class UserAnswerTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpassword')
        self.other_user = User.objects.create_user(username='otheruser', email='other@example.com', password='testpassword')
        
        self.type_slider = QuestionType.objects.create(name='Slider')
        self.type_choice = QuestionType.objects.create(name='Choice')

        self.question_slider = Question.objects.create(
            title='Slider Question',
            description='Test slider',
            type=self.type_slider,
            min_value=0.0,
            max_value=10.0,
            status='active'
        )
        
        self.question_choice = Question.objects.create(
            title='Choice Question',
            description='Test choice',
            type=self.type_choice,
            status='active'
        )
        
        self.prop1 = Option.objects.create(question=self.question_choice, text='Option 1')
        self.prop2 = Option.objects.create(question=self.question_choice, text='Option 2')
        
        self.other_question = Question.objects.create(
            title='Other Question',
            type=self.type_choice,
            status='active'
        )
        self.other_prop = Option.objects.create(question=self.other_question, text='Other Option')
        
        self.client.force_authenticate(user=self.user)

    def test_create_slider_response_success(self):
        url = reverse('answer-list')
        data = {
            'question': self.question_slider.id,
            'numeric_value': 5.0
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['numeric_value'], 5.0)
        self.assertEqual(response.data['question'], self.question_slider.id)
        
        reponse_obj = UserAnswer.objects.get(id=response.data['id'])
        self.assertEqual(reponse_obj.user, self.user)
        self.assertEqual(reponse_obj.numeric_value, 5.0)

    def test_create_slider_response_out_of_bounds(self):
        url = reverse('answer-list')
        data = {
            'question': self.question_slider.id,
            'numeric_value': 15.0
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        data = {
            'question': self.question_slider.id,
            'numeric_value': -1.0
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_slider_response_with_options_fails(self):
        url = reverse('answer-list')
        data = {
            'question': self.question_slider.id,
            'numeric_value': 5.0,
            'selected_options': [{'option': self.prop1.id}]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_choice_response_success(self):
        url = reverse('answer-list')
        data = {
            'question': self.question_choice.id,
            'selected_options': [
                {'option': self.prop1.id},
                {'option': self.prop2.id}
            ]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        reponse_obj = UserAnswer.objects.get(id=response.data['id'])
        self.assertEqual(reponse_obj.selected_options.count(), 2)
        selections = reponse_obj.selected_options.all()
        self.assertEqual(set(s.option for s in selections), {self.prop1, self.prop2})

    def test_create_choice_response_with_numeric_value_fails(self):
        url = reverse('answer-list')
        data = {
            'question': self.question_choice.id,
            'numeric_value': 5.0,
            'selected_options': [{'option': self.prop1.id}]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_choice_response_with_invalid_option_fails(self):
        url = reverse('answer-list')
        data = {
            'question': self.question_choice.id,
            'selected_options': [{'option': self.other_prop.id}]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_responses_uses_read_serializer(self):
        reponse = UserAnswer.objects.create(
            user=self.user,
            question=self.question_slider,
            numeric_value=7.5
        )
        
        url = reverse('answer-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        item = response.data[0]
        self.assertIn('questionText', item)
        self.assertIn('selectedOptions', item)
        self.assertIn('sliderValue', item)
        self.assertEqual(item['questionText'], 'Slider Question')
        self.assertEqual(item['sliderValue'], 7.5)
        self.assertEqual(item['selectedOptions'], [])

    def test_update_response_success(self):
        reponse = UserAnswer.objects.create(
            user=self.user,
            question=self.question_slider,
            numeric_value=3.0
        )
        
        url = reverse('answer-detail', kwargs={'pk': reponse.id})
        data = {
            'numeric_value': 8.0
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        reponse.refresh_from_db()
        self.assertEqual(reponse.numeric_value, 8.0)

    def test_update_response_from_other_user_fails(self):
        reponse = UserAnswer.objects.create(
            user=self.other_user,
            question=self.question_slider,
            numeric_value=3.0
        )
        
        url = reverse('answer-detail', kwargs={'pk': reponse.id})
        data = {
            'numeric_value': 8.0
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_bulk_create_responses_success(self):
        url = reverse('answer-list')
        data = [
            {
                'question': self.question_slider.id,
                'numeric_value': 4.5
            },
            {
                'question': self.question_choice.id,
                'selected_options': [{'option': self.prop1.id}]
            }
        ]
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_207_MULTI_STATUS)
        self.assertEqual(len(response.data['created']), 2)
        self.assertEqual(len(response.data['errors']), 0)
        
        self.assertEqual(UserAnswer.objects.filter(user=self.user).count(), 2)

    def test_bulk_create_responses_partial_errors(self):
        url = reverse('answer-list')
        data = [
            {
                'question': self.question_slider.id,
                'numeric_value': 14.5  # Invalid, out of bounds
            },
            {
                'question': self.question_choice.id,
                'selected_options': [{'option': self.prop1.id}]  # Valid
            }
        ]
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_207_MULTI_STATUS)
        self.assertEqual(len(response.data['created']), 1)
        self.assertEqual(len(response.data['errors']), 1)
        self.assertEqual(response.data['errors'][0]['index'], 0)


class QuestionEndpointsTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpassword')
        self.client.force_authenticate(user=self.user)
        
        self.type_q = QuestionType.objects.create(name='Multiple')
        self.question = Question.objects.create(
            title='Sample Question',
            type=self.type_q,
            status='active'
        )
        self.prop = Option.objects.create(question=self.question, text='Sample Option')

    def test_question_with_options(self):
        url = reverse('question-with-options', kwargs={'pk': self.question.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Sample Question')
        self.assertEqual(len(response.data['options']), 1)
        self.assertEqual(response.data['options'][0]['text'], 'Sample Option')

    def test_question_by_type_success(self):
        url = reverse('question-by-type')
        response = self.client.get(f"{url}?type_id={self.type_q.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Sample Question')

    def test_question_by_type_missing_param(self):
        url = reverse('question-by-type')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_options_by_question_success(self):
        url = reverse('option-by-question')
        response = self.client.get(f"{url}?question_id={self.question.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['text'], 'Sample Option')

    def test_options_by_question_missing_param(self):
        url = reverse('option-by-question')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_create_question_with_options(self):
        url = reverse('question-list')
        data = {
            'title': 'Q with options',
            'type': self.type_q.id,
            'status': 'active',
            'options': [
                {'text': 'Option A', 'status': 'active'},
                {'text': 'Option B', 'status': 'active'},
            ]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        q = Question.objects.get(title='Q with options')
        self.assertEqual(q.options.count(), 2)

    def test_create_question_without_options(self):
        url = reverse('question-list')
        data = {
            'title': 'Q without options',
            'type': self.type_q.id,
            'status': 'draft',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_question_with_options(self):
        url = reverse('question-detail', kwargs={'pk': self.question.id})
        data = {
            'title': 'Updated Question',
            'type': self.type_q.id,
            'status': 'inactive',
            'options': [
                {'text': 'New Option', 'status': 'active'},
            ]
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Question')

    def test_update_question_without_options(self):
        url = reverse('question-detail', kwargs={'pk': self.question.id})
        data = {
            'title': 'Partially Updated',
            'type': self.type_q.id,
            'status': 'active',
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class QuestionsModelStrTestCase(TestCase):

    def setUp(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        self.user = User.objects.create_user(username='qstruser', password='pass')
        self.type_q = QuestionType.objects.create(name='MyType')
        self.question = Question.objects.create(
            title='My Question',
            type=self.type_q,
            status='active'
        )
        self.prop = Option.objects.create(question=self.question, text='My Option')

    def test_type_question_str(self):
        self.assertEqual(str(self.type_q), 'MyType')

    def test_question_str(self):
        self.assertEqual(str(self.question), 'My Question')

    def test_option_str(self):
        self.assertEqual(str(self.prop), 'My Option')

    def test_user_answer_str(self):
        reponse = UserAnswer.objects.create(
            user=self.user,
            question=self.question,
            numeric_value=5.0
        )
        s = str(reponse)
        self.assertIn('qstruser', s)
        self.assertIn('My Question', s)

    def test_selected_option_str(self):
        reponse = UserAnswer.objects.create(
            user=self.user,
            question=self.question,
            numeric_value=None
        )
        ps = SelectedOption.objects.create(user_answer=reponse, option=self.prop)
        self.assertEqual(str(ps), 'My Option')

    def test_user_answer_clean_new_object(self):
        reponse = UserAnswer(
            user=self.user,
            question=self.question,
            numeric_value=5.0
        )
        reponse.clean()

    def test_user_answer_clean_validates_numeric_and_no_options(self):
        from django.core.exceptions import ValidationError
        reponse = UserAnswer.objects.create(
            user=self.user,
            question=self.question,
            numeric_value=None
        )
        with self.assertRaises(ValidationError):
            reponse.clean()

    def test_user_answer_clean_validates_both_fields_raises(self):
        from django.core.exceptions import ValidationError
        reponse = UserAnswer.objects.create(
            user=self.user,
            question=self.question,
            numeric_value=5.0
        )
        SelectedOption.objects.create(user_answer=reponse, option=self.prop)
        with self.assertRaises(ValidationError):
            reponse.clean()


class AnswerUpdateCoverageTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='upd_user', email='upd@test.com', password='pass')
        self.client.force_authenticate(user=self.user)
        self.type_choice = QuestionType.objects.create(name='ChoiceUpd')
        self.question = Question.objects.create(
            title='Upd Question',
            type=self.type_choice,
            status='active'
        )
        self.prop1 = Option.objects.create(question=self.question, text='Upd Opt 1')
        self.prop2 = Option.objects.create(question=self.question, text='Upd Opt 2')

    def test_update_response_replaces_options(self):
        reponse = UserAnswer.objects.create(
            user=self.user,
            question=self.question,
            numeric_value=None
        )
        SelectedOption.objects.create(user_answer=reponse, option=self.prop1)

        url = reverse('answer-detail', kwargs={'pk': reponse.id})
        data = {
            'selected_options': [{'option': self.prop2.id}]
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        reponse.refresh_from_db()
        self.assertEqual(reponse.selected_options.count(), 1)
        self.assertEqual(reponse.selected_options.first().option, self.prop2)

    def test_validate_with_instance_and_existing_options(self):
        reponse = UserAnswer.objects.create(
            user=self.user,
            question=self.question,
            numeric_value=None
        )
        SelectedOption.objects.create(user_answer=reponse, option=self.prop1)

        url = reverse('answer-detail', kwargs={'pk': reponse.id})
        data = {}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_response_by_other_user_fails(self):
        other_user = User.objects.create_user(username='other_upd', email='other@upd.com', password='pass')
        reponse = UserAnswer.objects.create(
            user=other_user,
            question=self.question,
            numeric_value=None
        )
        SelectedOption.objects.create(user_answer=reponse, option=self.prop1)

        url = reverse('answer-detail', kwargs={'pk': reponse.id})
        self.client.force_authenticate(user=self.user)
        data = {}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_slider_response_clears_value(self):
        type_slider = QuestionType.objects.create(name='SliderUpd')
        question_slider = Question.objects.create(
            title='Slider Upd Q',
            type=type_slider,
            min_value=0.0,
            max_value=10.0,
            status='active'
        )
        reponse = UserAnswer.objects.create(
            user=self.user,
            question=question_slider,
            numeric_value=5.0
        )
        url = reverse('answer-detail', kwargs={'pk': reponse.id})
        data = {'numeric_value': None}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_choice_response_without_options_fails(self):
        reponse = UserAnswer.objects.create(
            user=self.user,
            question=self.question,
            numeric_value=None
        )
        SelectedOption.objects.create(user_answer=reponse, option=self.prop1)

        url = reverse('answer-detail', kwargs={'pk': reponse.id})
        data = {'selected_options': []}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class SerializerDirectCoverageTestCase(TestCase):

    def setUp(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        self.user = User.objects.create_user(username='ser_user', password='pwd')
        self.type_slider = QuestionType.objects.create(name='Slider')
        self.type_choice = QuestionType.objects.create(name='Choice')
        
        self.q_slider = Question.objects.create(title='Slider', type=self.type_slider)
        self.q_choice = Question.objects.create(title='Choice', type=self.type_choice)
        
        self.reponse_slider = UserAnswer.objects.create(
            user=self.user,
            question=self.q_slider,
            numeric_value=5.0
        )
        self.reponse_choice = UserAnswer.objects.create(
            user=self.user,
            question=self.q_choice,
            numeric_value=None
        )

    def test_serializer_validate_initial_data_list(self):
        from questions.serializers import UserAnswerSerializer
        serializer = UserAnswerSerializer(data=[{'dummy': 'data'}])
        self.assertEqual(serializer.validate({'dummy': 'data'}), {'dummy': 'data'})

    def test_serializer_validate_slider_missing_value(self):
        from questions.serializers import UserAnswerSerializer
        from rest_framework.exceptions import ValidationError
        serializer = UserAnswerSerializer(instance=self.reponse_slider, data={'numeric_value': None}, partial=True)
        serializer.initial_data = {} 
        with self.assertRaises(ValidationError) as ctx:
            serializer.validate({'numeric_value': None})
        self.assertIn("This question expects a numeric value", str(ctx.exception))

    def test_serializer_validate_choice_missing_options(self):
        from questions.serializers import UserAnswerSerializer
        from rest_framework.exceptions import ValidationError
        serializer = UserAnswerSerializer(instance=self.reponse_choice, data={}, partial=True)
        serializer.initial_data = {'selected_options': []}
        with self.assertRaises(ValidationError) as ctx:
            serializer.validate({})
        self.assertIn("This question expects one or more selected options", str(ctx.exception))

    def test_serializer_update_wrong_user(self):
        from questions.serializers import UserAnswerSerializer
        from rest_framework.exceptions import ValidationError
        from unittest.mock import MagicMock
        
        other_user = User.objects.create_user(username='other_u', password='pwd')
        mock_request = MagicMock()
        mock_request.user = other_user
        
        serializer = UserAnswerSerializer(instance=self.reponse_slider, context={'request': mock_request})
        with self.assertRaises(ValidationError) as ctx:
            serializer.update(self.reponse_slider, {})
        self.assertIn("You cannot modify an answer that does not belong to you", str(ctx.exception))
