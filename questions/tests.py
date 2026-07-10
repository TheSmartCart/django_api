from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from questions.models import Question, Proposition, TypeQuestion, ReponseUtilisateur, PropositionSelectionnee

User = get_user_model()

class ReponseUtilisateurTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpassword')
        self.other_user = User.objects.create_user(username='otheruser', email='other@example.com', password='testpassword')
        
        self.type_slider = TypeQuestion.objects.create(nom='Slider')
        self.type_choix = TypeQuestion.objects.create(nom='Choix')

        self.question_slider = Question.objects.create(
            title='Slider Question',
            description='Test slider',
            type=self.type_slider,
            min_value=0.0,
            max_value=10.0,
            status='Actif'
        )
        
        self.question_choix = Question.objects.create(
            title='Choix Question',
            description='Test choice',
            type=self.type_choix,
            status='Actif'
        )
        
        self.prop1 = Proposition.objects.create(question=self.question_choix, texte='Option 1')
        self.prop2 = Proposition.objects.create(question=self.question_choix, texte='Option 2')
        
        self.other_question = Question.objects.create(
            title='Other Question',
            type=self.type_choix,
            status='Actif'
        )
        self.other_prop = Proposition.objects.create(question=self.other_question, texte='Other Option')
        
        self.client.force_authenticate(user=self.user)

    def test_create_slider_response_success(self):
        url = reverse('reponse-list')
        data = {
            'question': self.question_slider.id,
            'valeur_numerique': 5.0
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['valeur_numerique'], 5.0)
        self.assertEqual(response.data['question'], self.question_slider.id)
        
        reponse_obj = ReponseUtilisateur.objects.get(id=response.data['id'])
        self.assertEqual(reponse_obj.utilisateur, self.user)
        self.assertEqual(reponse_obj.valeur_numerique, 5.0)

    def test_create_slider_response_out_of_bounds(self):
        url = reverse('reponse-list')
        data = {
            'question': self.question_slider.id,
            'valeur_numerique': 15.0
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        data = {
            'question': self.question_slider.id,
            'valeur_numerique': -1.0
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_slider_response_with_propositions_fails(self):
        url = reverse('reponse-list')
        data = {
            'question': self.question_slider.id,
            'valeur_numerique': 5.0,
            'propositions_selectionnees': [{'proposition': self.prop1.id}]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_choix_response_success(self):
        url = reverse('reponse-list')
        data = {
            'question': self.question_choix.id,
            'propositions_selectionnees': [
                {'proposition': self.prop1.id},
                {'proposition': self.prop2.id}
            ]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        reponse_obj = ReponseUtilisateur.objects.get(id=response.data['id'])
        self.assertEqual(reponse_obj.propositions_selectionnees.count(), 2)
        selections = reponse_obj.propositions_selectionnees.all()
        self.assertEqual(set(s.proposition for s in selections), {self.prop1, self.prop2})

    def test_create_choix_response_with_valeur_numerique_fails(self):
        url = reverse('reponse-list')
        data = {
            'question': self.question_choix.id,
            'valeur_numerique': 5.0,
            'propositions_selectionnees': [{'proposition': self.prop1.id}]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_choix_response_with_invalid_proposition_fails(self):
        url = reverse('reponse-list')
        data = {
            'question': self.question_choix.id,
            'propositions_selectionnees': [{'proposition': self.other_prop.id}]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_responses_uses_read_serializer(self):
        reponse = ReponseUtilisateur.objects.create(
            utilisateur=self.user,
            question=self.question_slider,
            valeur_numerique=7.5
        )
        
        url = reverse('reponse-list')
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
        reponse = ReponseUtilisateur.objects.create(
            utilisateur=self.user,
            question=self.question_slider,
            valeur_numerique=3.0
        )
        
        url = reverse('reponse-detail', kwargs={'pk': reponse.id})
        data = {
            'valeur_numerique': 8.0
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        reponse.refresh_from_db()
        self.assertEqual(reponse.valeur_numerique, 8.0)

    def test_update_response_from_other_user_fails(self):
        reponse = ReponseUtilisateur.objects.create(
            utilisateur=self.other_user,
            question=self.question_slider,
            valeur_numerique=3.0
        )
        
        url = reverse('reponse-detail', kwargs={'pk': reponse.id})
        data = {
            'valeur_numerique': 8.0
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_bulk_create_responses_success(self):
        url = reverse('reponse-list')
        data = [
            {
                'question': self.question_slider.id,
                'valeur_numerique': 4.5
            },
            {
                'question': self.question_choix.id,
                'propositions_selectionnees': [{'proposition': self.prop1.id}]
            }
        ]
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_207_MULTI_STATUS)
        self.assertEqual(len(response.data['created']), 2)
        self.assertEqual(len(response.data['errors']), 0)
        
        self.assertEqual(ReponseUtilisateur.objects.filter(utilisateur=self.user).count(), 2)

    def test_bulk_create_responses_partial_errors(self):
        url = reverse('reponse-list')
        data = [
            {
                'question': self.question_slider.id,
                'valeur_numerique': 14.5  # Invalid, out of bounds
            },
            {
                'question': self.question_choix.id,
                'propositions_selectionnees': [{'proposition': self.prop1.id}]  # Valid
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
        
        self.type_q = TypeQuestion.objects.create(nom='Multiple')
        self.question = Question.objects.create(
            title='Sample Question',
            type=self.type_q,
            status='Actif'
        )
        self.prop = Proposition.objects.create(question=self.question, texte='Sample Option')

    def test_question_with_propositions(self):
        url = reverse('question-with-propositions', kwargs={'pk': self.question.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Sample Question')
        self.assertEqual(len(response.data['propositions']), 1)
        self.assertEqual(response.data['propositions'][0]['texte'], 'Sample Option')

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

    def test_propositions_by_question_success(self):
        url = reverse('proposition-by-question')
        response = self.client.get(f"{url}?question_id={self.question.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['texte'], 'Sample Option')

    def test_propositions_by_question_missing_param(self):
        url = reverse('proposition-by-question')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_create_question_with_propositions(self):
        url = reverse('question-list')
        data = {
            'title': 'Q avec props',
            'type': self.type_q.id,
            'status': 'Actif',
            'propositions': [
                {'texte': 'Prop A', 'statut': 'Actif'},
                {'texte': 'Prop B', 'statut': 'Actif'},
            ]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        q = Question.objects.get(title='Q avec props')
        self.assertEqual(q.propositions.count(), 2)

    def test_create_question_without_propositions(self):
        url = reverse('question-list')
        data = {
            'title': 'Q sans props',
            'type': self.type_q.id,
            'status': 'Brouillon',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_question_with_propositions(self):
        url = reverse('question-detail', kwargs={'pk': self.question.id})
        data = {
            'title': 'Updated Question',
            'type': self.type_q.id,
            'status': 'Inactif',
            'propositions': [
                {'texte': 'New Prop', 'statut': 'Actif'},
            ]
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Question')

    def test_update_question_without_propositions(self):
        url = reverse('question-detail', kwargs={'pk': self.question.id})
        data = {
            'title': 'Partially Updated',
            'type': self.type_q.id,
            'status': 'Actif',
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class QuestionsModelStrTestCase(TestCase):

    def setUp(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        self.user = User.objects.create_user(username='qstruser', password='pass')
        self.type_q = TypeQuestion.objects.create(nom='MonType')
        self.question = Question.objects.create(
            title='Ma Question',
            type=self.type_q,
            status='Actif'
        )
        self.prop = Proposition.objects.create(question=self.question, texte='Ma Prop')

    def test_type_question_str(self):
        self.assertEqual(str(self.type_q), 'MonType')

    def test_question_str(self):
        self.assertEqual(str(self.question), 'Ma Question')

    def test_proposition_str(self):
        self.assertEqual(str(self.prop), 'Ma Prop')

    def test_reponse_utilisateur_str(self):
        reponse = ReponseUtilisateur.objects.create(
            utilisateur=self.user,
            question=self.question,
            valeur_numerique=5.0
        )
        s = str(reponse)
        self.assertIn('qstruser', s)
        self.assertIn('Ma Question', s)

    def test_proposition_selectionnee_str(self):
        reponse = ReponseUtilisateur.objects.create(
            utilisateur=self.user,
            question=self.question,
            valeur_numerique=None
        )
        ps = PropositionSelectionnee.objects.create(reponse=reponse, proposition=self.prop)
        self.assertEqual(str(ps), 'Ma Prop')

    def test_reponse_clean_new_object(self):
        reponse = ReponseUtilisateur(
            utilisateur=self.user,
            question=self.question,
            valeur_numerique=5.0
        )
        # Should not raise
        reponse.clean()

    def test_reponse_clean_validates_numeric_and_no_propositions(self):
        from django.core.exceptions import ValidationError
        reponse = ReponseUtilisateur.objects.create(
            utilisateur=self.user,
            question=self.question,
            valeur_numerique=None
        )
        with self.assertRaises(ValidationError):
            reponse.clean()

    def test_reponse_clean_validates_both_fields_raises(self):
        from django.core.exceptions import ValidationError
        reponse = ReponseUtilisateur.objects.create(
            utilisateur=self.user,
            question=self.question,
            valeur_numerique=5.0
        )
        PropositionSelectionnee.objects.create(reponse=reponse, proposition=self.prop)
        with self.assertRaises(ValidationError):
            reponse.clean()


class ReponseUpdateCoverageTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='upd_user', email='upd@test.com', password='pass')
        self.client.force_authenticate(user=self.user)
        self.type_choix = TypeQuestion.objects.create(nom='ChoixUpd')
        self.question = Question.objects.create(
            title='Upd Question',
            type=self.type_choix,
            status='Actif'
        )
        self.prop1 = Proposition.objects.create(question=self.question, texte='Upd Opt 1')
        self.prop2 = Proposition.objects.create(question=self.question, texte='Upd Opt 2')

    def test_update_response_replaces_propositions(self):
        reponse = ReponseUtilisateur.objects.create(
            utilisateur=self.user,
            question=self.question,
            valeur_numerique=None
        )
        PropositionSelectionnee.objects.create(reponse=reponse, proposition=self.prop1)

        url = reverse('reponse-detail', kwargs={'pk': reponse.id})
        data = {
            'propositions_selectionnees': [{'proposition': self.prop2.id}]
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        reponse.refresh_from_db()
        self.assertEqual(reponse.propositions_selectionnees.count(), 1)
        self.assertEqual(reponse.propositions_selectionnees.first().proposition, self.prop2)

    def test_validate_with_instance_and_existing_propositions(self):
        reponse = ReponseUtilisateur.objects.create(
            utilisateur=self.user,
            question=self.question,
            valeur_numerique=None
        )
        PropositionSelectionnee.objects.create(reponse=reponse, proposition=self.prop1)

        url = reverse('reponse-detail', kwargs={'pk': reponse.id})
        # PATCH without propositions_selectionnees key — it uses existing propositions
        data = {}
        response = self.client.patch(url, data, format='json')
        # Should be 200 (existing props keep response valid)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_response_by_other_user_fails(self):
        other_user = User.objects.create_user(username='other_upd', email='other@upd.com', password='pass')
        reponse = ReponseUtilisateur.objects.create(
            utilisateur=other_user,
            question=self.question,
            valeur_numerique=None
        )
        PropositionSelectionnee.objects.create(reponse=reponse, proposition=self.prop1)

        url = reverse('reponse-detail', kwargs={'pk': reponse.id})
        self.client.force_authenticate(user=self.user)
        data = {}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_slider_response_clears_value(self):
        type_slider = TypeQuestion.objects.create(nom='SliderUpd')
        question_slider = Question.objects.create(
            title='Slider Upd Q',
            type=type_slider,
            min_value=0.0,
            max_value=10.0,
            status='Actif'
        )
        reponse = ReponseUtilisateur.objects.create(
            utilisateur=self.user,
            question=question_slider,
            valeur_numerique=5.0
        )
        url = reverse('reponse-detail', kwargs={'pk': reponse.id})
        data = {'valeur_numerique': None}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_choix_response_without_propositions_fails(self):
        reponse = ReponseUtilisateur.objects.create(
            utilisateur=self.user,
            question=self.question,
            valeur_numerique=None
        )
        PropositionSelectionnee.objects.create(reponse=reponse, proposition=self.prop1)

        url = reverse('reponse-detail', kwargs={'pk': reponse.id})
        data = {'propositions_selectionnees': []}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class SerializerDirectCoverageTestCase(TestCase):

    def setUp(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        self.user = User.objects.create_user(username='ser_user', password='pwd')
        self.type_slider = TypeQuestion.objects.create(nom='Slider')
        self.type_choix = TypeQuestion.objects.create(nom='Choix')
        
        self.q_slider = Question.objects.create(title='Slider', type=self.type_slider)
        self.q_choix = Question.objects.create(title='Choix', type=self.type_choix)
        
        self.reponse_slider = ReponseUtilisateur.objects.create(
            utilisateur=self.user,
            question=self.q_slider,
            valeur_numerique=5.0
        )
        self.reponse_choix = ReponseUtilisateur.objects.create(
            utilisateur=self.user,
            question=self.q_choix,
            valeur_numerique=None
        )

    def test_serializer_validate_initial_data_list(self):
        from questions.serializers import ReponseUtilisateurSerializer
        serializer = ReponseUtilisateurSerializer(data=[{'dummy': 'data'}])
        self.assertEqual(serializer.validate({'dummy': 'data'}), {'dummy': 'data'})

    def test_serializer_validate_slider_missing_value(self):
        from questions.serializers import ReponseUtilisateurSerializer
        from rest_framework.exceptions import ValidationError
        serializer = ReponseUtilisateurSerializer(instance=self.reponse_slider, data={'valeur_numerique': None}, partial=True)
        serializer.initial_data = {} 
        with self.assertRaises(ValidationError) as ctx:
            serializer.validate({'valeur_numerique': None})
        self.assertIn("Cette question attend une valeur numérique", str(ctx.exception))

    def test_serializer_validate_choix_missing_propositions(self):
        from questions.serializers import ReponseUtilisateurSerializer
        from rest_framework.exceptions import ValidationError
        serializer = ReponseUtilisateurSerializer(instance=self.reponse_choix, data={}, partial=True)
        serializer.initial_data = {'propositions_selectionnees': []}
        with self.assertRaises(ValidationError) as ctx:
            serializer.validate({})
        self.assertIn("Cette question attend une ou plusieurs propositions", str(ctx.exception))

    def test_serializer_update_wrong_user(self):
        from questions.serializers import ReponseUtilisateurSerializer
        from rest_framework.exceptions import ValidationError
        from unittest.mock import MagicMock
        
        other_user = User.objects.create_user(username='other_u', password='pwd')
        mock_request = MagicMock()
        mock_request.user = other_user
        
        serializer = ReponseUtilisateurSerializer(instance=self.reponse_slider, context={'request': mock_request})
        with self.assertRaises(ValidationError) as ctx:
            serializer.update(self.reponse_slider, {})
        self.assertIn("Vous ne pouvez pas modifier une réponse qui ne vous appartient pas", str(ctx.exception))
