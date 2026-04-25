import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from apps.books.models import Book

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def admin_user(db):
    return User.objects.create_user(
        email='admin@bookstore.com', name='Admin User', password='adminpass123', role='ADMIN'
    )


@pytest.fixture
def customer_user(db):
    return User.objects.create_user(
        email='customer@bookstore.com', name='Customer User', password='customerpass123', role='CUSTOMER'
    )


@pytest.fixture
def admin_token(api_client, admin_user):
    response = api_client.post('/api/login/', {'email': 'admin@bookstore.com', 'password': 'adminpass123'})
    return response.data['tokens']['access']


@pytest.fixture
def customer_token(api_client, customer_user):
    response = api_client.post(
        '/api/login/', {'email': 'customer@bookstore.com', 'password': 'customerpass123'}
    )
    return response.data['tokens']['access']


@pytest.fixture
def sample_book(db):
    return Book.objects.create(
        title='The Pragmatic Programmer',
        author='David Thomas',
        genre='Technology',
        isbn='9780135957059',
        price=49.99,
        description='A classic programming book.',
        stock_quantity=10,
        image_url='https://example.com/pragmatic.jpg',
    )
