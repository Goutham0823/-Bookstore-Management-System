import pytest
from rest_framework import status


@pytest.mark.django_db
class TestRegister:
    def test_register_customer_success(self, api_client):
        response = api_client.post('/api/register/', {
            'name': 'John Doe', 'email': 'john@example.com',
            'password': 'securepass123', 'password_confirm': 'securepass123', 'role': 'CUSTOMER',
        })
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['user']['email'] == 'john@example.com'
        assert response.data['user']['role'] == 'CUSTOMER'

    def test_register_admin_success(self, api_client):
        response = api_client.post('/api/register/', {
            'name': 'Admin', 'email': 'admin2@example.com',
            'password': 'adminpass123', 'password_confirm': 'adminpass123', 'role': 'ADMIN',
        })
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['user']['role'] == 'ADMIN'

    def test_register_duplicate_email(self, api_client, customer_user):
        response = api_client.post('/api/register/', {
            'name': 'Another', 'email': 'customer@bookstore.com',
            'password': 'testpass123', 'password_confirm': 'testpass123', 'role': 'CUSTOMER',
        })
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_password_mismatch(self, api_client):
        response = api_client.post('/api/register/', {
            'name': 'Test', 'email': 'test2@example.com',
            'password': 'pass12345', 'password_confirm': 'different', 'role': 'CUSTOMER',
        })
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_short_password(self, api_client):
        response = api_client.post('/api/register/', {
            'name': 'Test', 'email': 'test3@example.com',
            'password': 'short', 'password_confirm': 'short', 'role': 'CUSTOMER',
        })
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestLogin:
    def test_login_success_returns_tokens(self, api_client, customer_user):
        response = api_client.post('/api/login/', {
            'email': 'customer@bookstore.com', 'password': 'customerpass123',
        })
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data['tokens']
        assert 'refresh' in response.data['tokens']

    def test_login_wrong_password(self, api_client, customer_user):
        response = api_client.post('/api/login/', {
            'email': 'customer@bookstore.com', 'password': 'wrongpassword',
        })
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_nonexistent_email(self, api_client):
        response = api_client.post('/api/login/', {
            'email': 'nobody@example.com', 'password': 'somepass123',
        })
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_profile_requires_auth(self, api_client):
        response = api_client.get('/api/profile/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_profile_with_valid_token(self, api_client, customer_user, customer_token):
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {customer_token}')
        response = api_client.get('/api/profile/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == 'customer@bookstore.com'
        assert response.data['role'] == 'CUSTOMER'
