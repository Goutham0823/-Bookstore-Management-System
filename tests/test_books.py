import pytest
from rest_framework import status
from apps.books.models import Book


@pytest.mark.django_db
class TestBookList:
    def test_list_books_unauthenticated(self, api_client, sample_book):
        response = api_client.get('/api/books/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] >= 1

    def test_search_by_title(self, api_client, sample_book):
        response = api_client.get('/api/books/?search=Pragmatic')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] >= 1

    def test_search_by_author(self, api_client, sample_book):
        response = api_client.get('/api/books/?search=David')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] >= 1

    def test_filter_by_genre(self, api_client, sample_book):
        response = api_client.get('/api/books/?genre=Technology')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] >= 1

    def test_filter_by_price_range(self, api_client, sample_book):
        response = api_client.get('/api/books/?min_price=40&max_price=60')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] >= 1

    def test_filter_in_stock(self, api_client, sample_book):
        response = api_client.get('/api/books/?in_stock=true')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] >= 1


@pytest.mark.django_db
class TestBookDetail:
    def test_get_book_by_id(self, api_client, sample_book):
        response = api_client.get(f'/api/books/{sample_book.id}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == sample_book.title
        assert response.data['isbn'] == sample_book.isbn

    def test_get_nonexistent_book_returns_404(self, api_client):
        response = api_client.get('/api/books/99999/')
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestBookCRUD:
    def test_admin_can_create_book(self, api_client, admin_token):
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {admin_token}')
        response = api_client.post('/api/books/', {
            'title': 'Clean Code', 'author': 'Robert C. Martin',
            'genre': 'Technology', 'isbn': '9780132350884',
            'price': '39.99', 'description': 'Agile craftsmanship.', 'stock_quantity': 20,
        })
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['title'] == 'Clean Code'

    def test_customer_cannot_create_book(self, api_client, customer_token):
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {customer_token}')
        response = api_client.post('/api/books/', {
            'title': 'Hack Book', 'author': 'Hacker',
            'genre': 'Fiction', 'isbn': '1234567890123',
            'price': '10.00', 'stock_quantity': 5,
        })
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated_cannot_create_book(self, api_client):
        response = api_client.post('/api/books/', {
            'title': 'Test', 'author': 'Test', 'genre': 'Test',
            'isbn': '9990000000001', 'price': '5.00', 'stock_quantity': 1,
        })
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_can_update_book(self, api_client, admin_token, sample_book):
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {admin_token}')
        response = api_client.patch(f'/api/books/{sample_book.id}/', {'price': '59.99'})
        assert response.status_code == status.HTTP_200_OK
        assert float(response.data['price']) == 59.99

    def test_admin_can_delete_book(self, api_client, admin_token, sample_book):
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {admin_token}')
        response = api_client.delete(f'/api/books/{sample_book.id}/')
        assert response.status_code == status.HTTP_200_OK
        assert 'deleted' in response.data['message'].lower()

    def test_duplicate_isbn_rejected(self, api_client, admin_token, sample_book):
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {admin_token}')
        response = api_client.post('/api/books/', {
            'title': 'Duplicate', 'author': 'Author', 'genre': 'Fiction',
            'isbn': sample_book.isbn, 'price': '10.00', 'stock_quantity': 1,
        })
        assert response.status_code == status.HTTP_400_BAD_REQUEST
