from django.contrib import admin
from .models import Book


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'genre', 'price', 'stock_quantity', 'isbn', 'created_at']
    list_filter = ['genre']
    search_fields = ['title', 'author', 'isbn']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
