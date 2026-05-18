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
