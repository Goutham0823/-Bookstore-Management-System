from rest_framework import viewsets, filters, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter

from .models import Book
from .serializers import BookSerializer, BookListSerializer
from .filters import BookFilter
from .permissions import IsAdminOrReadOnly


@extend_schema_view(
    list=extend_schema(
        tags=['Books'],
        summary='List all books (public)',
        description=(
            'Returns a paginated list of all books. '
            'Supports full-text search (title, author, genre) and filtering by price range and stock availability.'
        ),
        parameters=[
            OpenApiParameter('search', str, description='Search by title, author, or genre'),
            OpenApiParameter('genre', str, description='Filter by exact genre (case-insensitive)'),
            OpenApiParameter('min_price', float, description='Filter books with price >= value'),
            OpenApiParameter('max_price', float, description='Filter books with price <= value'),
            OpenApiParameter('in_stock', bool, description='true = in-stock only, false = out-of-stock only'),
            OpenApiParameter('ordering', str, description='Order by: title, price, created_at, stock_quantity'),
            OpenApiParameter('page', int, description='Page number (default 10 results per page)'),
        ],
    ),
    create=extend_schema(tags=['Books'], summary='Add a new book — Admin only'),
    retrieve=extend_schema(tags=['Books'], summary='Retrieve a book by ID (public)'),
    update=extend_schema(tags=['Books'], summary='Update a book — Admin only'),
    partial_update=extend_schema(tags=['Books'], summary='Partially update a book — Admin only'),
    destroy=extend_schema(tags=['Books'], summary='Delete a book — Admin only'),
)
class BookViewSet(viewsets.ModelViewSet):
    """
    Book CRUD API.
    - List / Retrieve: public (no auth required)
    - Create / Update / Delete: ADMIN role required
    """
    queryset = Book.objects.all()
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = BookFilter
    search_fields = ['title', 'author', 'genre']
    ordering_fields = ['title', 'price', 'created_at', 'stock_quantity']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return BookListSerializer
        return BookSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAdminOrReadOnly()]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        title = instance.title
        self.perform_destroy(instance)
        return Response({'message': f'Book "{title}" deleted successfully.'}, status=status.HTTP_200_OK)
