from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from users.models import CustomUser

class UserTestCase(APITestCase):
    def setUp(self):
        self.username = 'testuser'
        self.email = 'testuser@example.com'
        self.password = 'strongpassword123'
        self.user = CustomUser.objects.create_user(
            username=self.username,
            email=self.email,
            password=self.password,
            first_name='Test',
            last_name='User'
        )

    def test_create_user_returns_tokens(self):
        url = reverse('user-list')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpassword123',
            'first_name': 'New',
            'last_name': 'User'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['username'], 'newuser')
        self.assertEqual(response.data['email'], 'newuser@example.com')
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertTrue(len(response.data['access']) > 0)
        self.assertTrue(len(response.data['refresh']) > 0)
        self.assertTrue(CustomUser.objects.filter(username='newuser').exists())

    def test_obtain_token_success(self):
        url = reverse('token_obtain_pair')
        data = {
            'username': self.username,
            'password': self.password
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_obtain_token_invalid_credentials(self):
        url = reverse('token_obtain_pair')
        data = {
            'username': self.username,
            'password': 'wrongpassword'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_token(self):
        url_obtain = reverse('token_obtain_pair')
        data_obtain = {
            'username': self.username,
            'password': self.password
        }
        response_obtain = self.client.post(url_obtain, data_obtain, format='json')
        refresh_token = response_obtain.data['refresh']

        url_refresh = reverse('token_refresh')
        data_refresh = {
            'refresh': refresh_token
        }
        response_refresh = self.client.post(url_refresh, data_refresh, format='json')
        self.assertEqual(response_refresh.status_code, status.HTTP_200_OK)
        self.assertIn('access', response_refresh.data)

    def test_get_me_unauthenticated(self):
        url = reverse('user-me')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_me_authenticated(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('user-me')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.username)
        self.assertEqual(response.data['email'], self.email)

    def test_update_me_patch(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('user-me')
        data = {
            'first_name': 'UpdatedFirst',
            'last_name': 'UpdatedLast'
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'UpdatedFirst')
        self.assertEqual(response.data['last_name'], 'UpdatedLast')
        
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'UpdatedFirst')
        self.assertEqual(self.user.last_name, 'UpdatedLast')

    def test_update_me_put(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('user-me')
        data = {
            'username': self.username,
            'email': 'updatedemail@example.com',
            'first_name': 'UpdatedFirstPut',
            'last_name': 'UpdatedLastPut',
            'password': self.password
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'updatedemail@example.com')
        self.assertEqual(response.data['first_name'], 'UpdatedFirstPut')
        self.assertEqual(response.data['last_name'], 'UpdatedLastPut')
        
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'updatedemail@example.com')
        self.assertEqual(self.user.first_name, 'UpdatedFirstPut')

    def test_custom_user_str(self):
        self.assertEqual(str(self.user), self.username)
