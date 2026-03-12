from django.contrib import admin
from catalog.models import Product, Category, ProductMedia

# Register your models here.
class ProductMediaInline(admin.TabularInline):
    """Настройка "вложенного" редактора медиа"""
    model = ProductMedia
    extra = 1  # Количество пустых полей для новых файлов по умолчанию


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Административный класс для продукта"""
    list_display = ('id', 'name', 'price', 'category',)
    list_filter = ('category',)
    search_fields = ('name', 'description',)
    inlines = [ProductMediaInline]


@admin.register(Category)
class ProductAdmin(admin.ModelAdmin):
    """Административный класс для категории"""
    list_display = ('id', 'name',)
