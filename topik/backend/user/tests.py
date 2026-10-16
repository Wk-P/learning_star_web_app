from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from .models import User


def make_user(username='testuser', password='pass1234', is_staff=False, is_superuser=False):
    user = User.objects.create_user(username=username, email=f'{username}@test.com', password=password)
    user.is_staff = is_staff
    user.is_superuser = is_superuser
    user.save()
    return user


def get_auth_header(client: APIClient, username='testuser', password='pass1234'):
    resp = client.post('/api/auth/token/', {'username': username, 'password': password}, format='json')
    token = resp.data['access']
    return {'HTTP_AUTHORIZATION': f'Bearer {token}'}


class UserListViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = make_user('admin', 'admin1234', is_staff=True, is_superuser=True)
        self.normal = make_user('normal', 'pass1234')

    def test_admin_can_list_users(self):
        headers = get_auth_header(self.client, 'admin', 'admin1234')
        resp = self.client.get('/api/user/', **headers)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIsInstance(resp.data, list)

    def test_normal_user_is_forbidden(self):
        headers = get_auth_header(self.client, 'normal', 'pass1234')
        resp = self.client.get('/api/user/', **headers)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_is_unauthorized(self):
        resp = self.client.get('/api/user/')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)


class UserDetailViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = make_user('admin', 'admin1234', is_staff=True, is_superuser=True)
        self.normal = make_user('normal', 'pass1234')
        self.target = make_user('target', 'pass1234')

    def test_admin_can_get_existing_user(self):
        headers = get_auth_header(self.client, 'admin', 'admin1234')
        resp = self.client.get(f'/api/user/detail/?id={self.target.id}', **headers)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['username'], 'target')

    def test_nonexistent_user_returns_404(self):
        headers = get_auth_header(self.client, 'admin', 'admin1234')
        resp = self.client.get('/api/user/detail/?id=99999', **headers)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_normal_user_is_forbidden(self):
        headers = get_auth_header(self.client, 'normal', 'pass1234')
        resp = self.client.get(f'/api/user/detail/?id={self.target.id}', **headers)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)