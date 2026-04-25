from django.db import models
from django.core.validators import MinValueValidator


class Book(models.Model):
    """Represents a book in the bookstore inventory."""
    title = models.CharField(max_length=500)
    author = models.CharField(max_length=255)
    genre = models.CharField(max_length=100)
    isbn = models.CharField(max_length=13, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    description = models.TextField(blank=True, default='')
    stock_quantity = models.PositiveIntegerField(default=0)
    image_url = models.URLField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'books'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['author']),
            models.Index(fields=['genre']),
        ]

    def __str__(self):
        return f'{self.title} by {self.author}'

    @property
    def in_stock(self):
        return self.stock_quantity > 0
