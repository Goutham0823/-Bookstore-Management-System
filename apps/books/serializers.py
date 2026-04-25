from rest_framework import serializers
from .models import Book


class BookSerializer(serializers.ModelSerializer):
    """Full serializer for Book CRUD operations."""
    in_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = Book
        fields = [
            'id', 'title', 'author', 'genre', 'isbn',
            'price', 'description', 'stock_quantity',
            'image_url', 'in_stock', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_isbn(self, value):
        isbn = value.replace('-', '')
        if len(isbn) not in (10, 13):
            raise serializers.ValidationError('ISBN must be 10 or 13 digits.')
        if not isbn.isdigit():
            raise serializers.ValidationError('ISBN must contain only digits.')
        return isbn

    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError('Price cannot be negative.')
        return value


class BookListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views."""
    in_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'genre', 'isbn', 'price', 'stock_quantity', 'in_stock', 'image_url']
