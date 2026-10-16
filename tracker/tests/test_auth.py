from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase


class AuthTests(APITestCase):
    def setUp(self):
        self.register_url = reverse('accounts:register')
        self.login_url = reverse('accounts:login')
        self.me_url = reverse('accounts:current_user')
        self.user_data = {
            'username': 'candidate1',
            'email': 'candidate1@example.com',
            'password': 'StrongPassword123!',
            'password_confirm': 'StrongPassword123!'
        }

    def test_user_registration_success(self):
        """User can register and immediately receives JWT tokens."""
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['username'], 'candidate1')
        self.assertEqual(response.data['email'], 'candidate1@example.com')
        self.assertIn('tokens', response.data)
        self.assertIn('access', response.data['tokens'])
        self.assertIn('refresh', response.data['tokens'])
        self.assertTrue(User.objects.filter(username='candidate1').exists())

    def test_user_registration_password_mismatch(self):
        """Registration fails if passwords do not match."""
        invalid_data = self.user_data.copy()
        invalid_data['password_confirm'] = 'DifferentPassword123!'
        response = self.client.post(self.register_url, invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password_confirm', response.data)

    def test_user_registration_duplicate_username(self):
        """Registration fails when username already exists."""
        User.objects.create_user(username='candidate1', email='old@example.com', password='password123')
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)

    def test_user_login_success(self):
        """User can login with valid credentials and receive JWT access/refresh tokens."""
        User.objects.create_user(
            username=self.user_data['username'],
            email=self.user_data['email'],
            password=self.user_data['password']
        )
        login_payload = {
            'username': self.user_data['username'],
            'password': self.user_data['password']
        }
        response = self.client.post(self.login_url, login_payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_user_login_invalid_credentials(self):
        """Login fails with invalid password."""
        User.objects.create_user(
            username='candidate1',
            email='c1@example.com',
            password='CorrectPassword123!'
        )
        response = self.client.post(self.login_url, {
            'username': 'candidate1',
            'password': 'WrongPassword!'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_current_user_profile(self):
        """Authenticated user can query their own profile; unauthenticated returns 401."""
        user = User.objects.create_user(
            username='candidate_profile',
            email='profile@example.com',
            password='Password123!'
        )

        # Unauthenticated
        unauth_res = self.client.get(self.me_url)
        self.assertEqual(unauth_res.status_code, status.HTTP_401_UNAUTHORIZED)

        # Authenticated
        self.client.force_authenticate(user=user)
        auth_res = self.client.get(self.me_url)
        self.assertEqual(auth_res.status_code, status.HTTP_200_OK)
        self.assertEqual(auth_res.data['username'], 'candidate_profile')
        self.assertEqual(auth_res.data['email'], 'profile@example.com')
