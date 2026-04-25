import pytest
from rest_framework import status


def place_order(api_client, customer_token, book_id, quantity=1):
    """Helper: place a customer order."""
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {customer_token}')
    return api_client.post('/api/orders/', {'items': [{'book_id': book_id, 'quantity': quantity}]}, format='json')


@pytest.mark.django_db
class TestOrderCreation:
    def test_customer_can_place_order(self, api_client, customer_token, sample_book):
        response = place_order(api_client, customer_token, sample_book.id, 2)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['status'] == 'PENDING'
        assert float(response.data['total_amount']) == float(sample_book.price * 2)

    def test_stock_decremented_after_order(self, api_client, customer_token, sample_book):
        initial_stock = sample_book.stock_quantity
        place_order(api_client, customer_token, sample_book.id, 3)
        sample_book.refresh_from_db()
        assert sample_book.stock_quantity == initial_stock - 3

    def test_admin_cannot_place_order(self, api_client, admin_token, sample_book):
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {admin_token}')
        response = api_client.post('/api/orders/', {'items': [{'book_id': sample_book.id, 'quantity': 1}]}, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_insufficient_stock_rejected(self, api_client, customer_token, sample_book):
        response = place_order(api_client, customer_token, sample_book.id, 999)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_nonexistent_book_rejected(self, api_client, customer_token):
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {customer_token}')
        response = api_client.post('/api/orders/', {'items': [{'book_id': 9999, 'quantity': 1}]}, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_unauthenticated_cannot_order(self, api_client, sample_book):
        response = api_client.post('/api/orders/', {'items': [{'book_id': sample_book.id, 'quantity': 1}]}, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestOrderAccess:
    def test_admin_can_list_all_orders(self, api_client, admin_token, customer_token, sample_book):
        place_order(api_client, customer_token, sample_book.id)
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {admin_token}')
        response = api_client.get('/api/orders/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] >= 1

    def test_customer_cannot_list_all_orders(self, api_client, customer_token):
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {customer_token}')
        response = api_client.get('/api/orders/')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_customer_can_view_own_order(self, api_client, customer_token, sample_book):
        create_response = place_order(api_client, customer_token, sample_book.id)
        order_id = create_response.data['id']
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {customer_token}')
        response = api_client.get(f'/api/orders/{order_id}/')
        assert response.status_code == status.HTTP_200_OK

    def test_admin_can_update_order_status(self, api_client, admin_token, customer_token, sample_book):
        create_response = place_order(api_client, customer_token, sample_book.id)
        order_id = create_response.data['id']
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {admin_token}')
        response = api_client.put(f'/api/orders/{order_id}/status/', {'status': 'SHIPPED'})
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'SHIPPED'

    def test_invalid_status_rejected(self, api_client, admin_token, customer_token, sample_book):
        create_response = place_order(api_client, customer_token, sample_book.id)
        order_id = create_response.data['id']
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {admin_token}')
        response = api_client.put(f'/api/orders/{order_id}/status/', {'status': 'INVALID_STATUS'})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
