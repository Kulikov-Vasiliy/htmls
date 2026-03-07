from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from catalog.models import Product, Category
from django.utils import timezone


# Create your views here.


# def category_view(request, pk):
#     """Контроллер позволяет наполнять базовую страницу: категорией"""
#     page_name = "category"
#     current_category = get_object_or_404(Category, pk=pk)
#     products = Product.objects.filter(category=current_category)
#     context = {
#         "category": current_category,
#         "object_list": products,
#         "page_name": page_name
#     }
#     return render(request, 'catalog/category.html', context)


class ProductListView(ListView):
    """Контроллер позволяет наполнять базовую страницу: продуктами"""
    model = Product
    page_name = "category"
    template_name = 'catalog/category.html'
    context_object_name = "object_list"

    def dispatch(self, request, *args, **kwargs):
        """Дебаг-метод для проверки подключения контроллера"""
        # Этот принт сработает ПЕРВЫМ при любом обращении к этому URL
        print(">>> СИГНАЛ ПОЛУЧЕН: Запрос вошел в ProductListView")
        print(f">>> Данные пути (kwargs): {kwargs}")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        """Метод получения товара в категории по ид"""
        category_id = self.kwargs.get('category_id')
        queryset = Product.objects.filter(category_id=category_id)
        return queryset

    def get_context_data(self, **kwargs):
        """Метод переопределения контекста для получения данных о категории"""
        context = super().get_context_data(**kwargs)
        # Находим категорию по ID из URL и передаем в шаблон
        category_id = self.kwargs.get('category_id')
        context['category'] = get_object_or_404(Category, pk=category_id)
        context['page_name'] = 'category'
        return context


class ProductDetailView(DetailView):
    """Контроллер позволяет детализировать базовую страницу: информацией о продуктах"""
    model = Product
    page_name = "product"
    template_name = 'catalog/product_detail.html'
    # context_object_name = "object"

    def get_context_data(self, **kwargs):
        """Метод отвечает за подготовку данных, которые полетят в HTML-шаблон"""
        context = super().get_context_data(**kwargs)
        context['page_name'] = 'product'
        return context


def home_view(request):
    """Контроллер позволяет наполнять базовую страницу: общими товарами"""
    page_name = "home"
    products = Product.objects.all()
    context = {"object_list": products, "page_name": page_name}
    return render(request, 'catalog/home.html', context)


def base_view(request):
    """Контроллер позволяет считывать базовую страницу"""
    return render(request, 'catalog/base.html')


def catalogue_view(request):
    """Контроллер позволяет наполнять базовую страницу: каталогом"""
    page_name = "catalogue"
    catalogue = Category.objects.all()
    context = {"catalogue": catalogue, "page_name": page_name}
    return render(request, 'catalog/catalogue.html', context)


def contacts_view(request):
    """Контроллер позволяет наполнять базовую страницу: контактами"""
    page_name = "contacts"
    context = {"page_name": page_name}
    return render(request, 'catalog/contacts.html', context)
