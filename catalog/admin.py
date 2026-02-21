from django.contrib import admin
from catalog.models import Product, Category

# Register your models here.
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Административный класс для продукта"""
    list_display = ('id', 'name', 'price', 'category',)
    list_filter = ('category',)
    search_fields = ('name', 'description',)


@admin.register(Category)
class ProductAdmin(admin.ModelAdmin):
    """Административный класс для категории"""
    list_display = ('id', 'name',)
