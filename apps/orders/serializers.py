from rest_framework import serializers
from django.db import transaction
from .models import Order, OrderItem
from apps.books.models import Book


class OrderItemSerializer(serializers.ModelSerializer):
    """Read serializer for order line items."""
    book_title = serializers.SerializerMethodField()
    book_author = serializers.SerializerMethodField()
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'book', 'book_title', 'book_author', 'quantity', 'price_at_purchase', 'subtotal']
        read_only_fields = ['id', 'price_at_purchase', 'subtotal']

    def get_book_title(self, obj):
        return obj.book.title if obj.book else 'Deleted Book'

    def get_book_author(self, obj):
        return obj.book.author if obj.book else 'Unknown'


class OrderCreateItemSerializer(serializers.Serializer):
    """Represents a single item in the order creation request."""
    book_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)


class OrderCreateSerializer(serializers.Serializer):
    """Serializer for placing a new order."""
    items = OrderCreateItemSerializer(many=True, min_length=1)

    def validate_items(self, items):
        book_ids = [item['book_id'] for item in items]
        if len(book_ids) != len(set(book_ids)):
            raise serializers.ValidationError('Duplicate books found. Combine quantities instead.')
        return items

    def validate(self, attrs):
        validated_items = []
        for item in attrs['items']:
            try:
                book = Book.objects.get(id=item['book_id'])
            except Book.DoesNotExist:
                raise serializers.ValidationError(
                    {'items': f'Book with id {item["book_id"]} does not exist.'}
                )
            if book.stock_quantity < item['quantity']:
                raise serializers.ValidationError(
                    {'items': f'Insufficient stock for "{book.title}". Available: {book.stock_quantity}.'}
                )
            validated_items.append({'book': book, 'quantity': item['quantity']})
        attrs['validated_items'] = validated_items
        return attrs

    @transaction.atomic
    def save(self, **kwargs):
        user = self.context['request'].user
        validated_items = self.validated_data['validated_items']

        order = Order.objects.create(user=user)
        total = 0

        for item in validated_items:
            book = item['book']
            quantity = item['quantity']
            price = book.price

            OrderItem.objects.create(
                order=order,
                book=book,
                quantity=quantity,
                price_at_purchase=price,
            )
            # Decrement stock atomically
            book.stock_quantity -= quantity
            book.save(update_fields=['stock_quantity'])
            total += quantity * price

        order.total_amount = total
        order.save(update_fields=['total_amount'])
        return order


class OrderSerializer(serializers.ModelSerializer):
    """Full read serializer for orders."""
    items = OrderItemSerializer(many=True, read_only=True)
    user_name = serializers.SerializerMethodField()
    user_email = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id', 'user_name', 'user_email',
            'status', 'payment_status', 'total_amount',
            'items', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'total_amount', 'created_at', 'updated_at']

    def get_user_name(self, obj):
        return obj.user.name

    def get_user_email(self, obj):
        return obj.user.email


class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    """Serializer for admin status/payment updates."""
    class Meta:
        model = Order
        fields = ['status', 'payment_status']

    def validate_status(self, value):
        valid = ['PENDING', 'SHIPPED', 'DELIVERED', 'CANCELLED']
        if value not in valid:
            raise serializers.ValidationError(f'Status must be one of: {", ".join(valid)}')
        return value

    def validate_payment_status(self, value):
        valid = ['UNPAID', 'PAID', 'REFUNDED']
        if value not in valid:
            raise serializers.ValidationError(f'Payment status must be one of: {", ".join(valid)}')
        return value
