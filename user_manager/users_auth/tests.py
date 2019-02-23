from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from rest_auth.models import TokenModel


class TestUserVerification(TestCase):
    def create_user(self):
        return User.objects.create(
            username='username',
            email='email@email.com'
        )

    def create_token(self, user):
        return TokenModel.objects.create(user=user)

    def test_verify_valid_token(self):
        user = self.create_user()
        token = self.create_token(user)
        url = reverse('verify-token')
        data = {'token': token.key, 'username': user.username}
        expected = {'is_valid': True, 'user_id': user.id}
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        self.assertDictEqual(expected, response.json())

    def test_verify_invalid_token(self):
        user = self.create_user()
        token = self.create_token(user)
        url = reverse('verify-token')
        data = {'token': user.username, 'username': user.username}
        expected = {'is_valid': False, 'user_id': None}
        response = self.client.post(url, data=data)
        self.assertEqual(400, response.status_code)
        self.assertDictEqual(expected, response.json())

    def test_get_players_data(self):
        user = self.create_user()
        url = reverse('user-data')
        response = self.client.get(url, data={'player_id': [1, 2]})
        self.assertEqual(200, response.status_code)
        self.assertDictEqual(
            {str(user.id): user.username},
            response.json().get('players')
        )
