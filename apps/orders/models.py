from django.db import models
from django.conf import settings
from apps.books.models import Book


class Order(models.Model):
    """Represents a customer order in the bookstore."""
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SHIPPED', 'Shipped'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    ]
    PAYMENT_STATUS_CHOICES = [
        ('UNPAID', 'Unpaid'),
        ('PAID', 'Paid'),
        ('REFUNDED', 'Refunded'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='UNPAID')
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'orders'
        ordering = ['-created_at']

    def __str__(self):
        return f'Order #{self.id} by {self.user.name} [{self.status}]'


class OrderItem(models.Model):
    """Represents a single line item within an order."""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    # SET_NULL so orders survive book deletion; title snapshot handles display
    book = models.ForeignKey(Book, on_delete=models.SET_NULL, null=True, related_name='order_items')
    quantity = models.PositiveIntegerField()
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)  # Price snapshot

    class Meta:
        db_table = 'order_items'

    def __str__(self):
        title = self.book.title if self.book else 'Deleted Book'
        return f'{self.quantity}x {title}'

    @property
    def subtotal(self):
        return self.quantity * self.price_at_purchase
