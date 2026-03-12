from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from catalog.models import Product, Category
from catalog.forms import  ProductMediaFormSet
# ^ProductForm
from django.utils import timezone
from django.db import transaction
import os


from config import settings


# Create your views here.
class ProductListView(ListView):
    """Контроллер позволяет наполнять базовую страницу: продуктами"""
    model = Product
    page_name = "category"
    template_name = 'catalog/category.html'
    context_object_name = "object_list"

    # def dispatch(self, request, *args, **kwargs):
    #     """Дебаг-метод для проверки подключения контроллера"""
    #     # Этот принт сработает ПЕРВЫМ при любом обращении к этому URL
    #     print(">>> СИГНАЛ ПОЛУЧЕН: Запрос вошел в ProductListView")
    #     print(f">>> Данные пути (kwargs): {kwargs}")
    #     print(f"Ищу файл тут: {os.path.join(settings.MEDIA_ROOT, 'category/images/#')}")  # замениить # на имя для категории
    #     print(f"Папка существует? {os.path.exists(settings.MEDIA_ROOT)}")
    #     return super().dispatch(request, *args, **kwargs)

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
    context_object_name = "object"

    # def dispatch(self, request, *args, **kwargs):
    #     """Дебаг-метод для проверки подключения контроллера"""
    #     # Этот принт сработает ПЕРВЫМ при любом обращении к этому URL
    #     print(">>> СИГНАЛ ПОЛУЧЕН: Запрос вошел в ProductDetailView")
    #     print(f">>> Данные пути (kwargs): {kwargs}")
    #     print(f"Ищу файл тут: {os.path.join(settings.MEDIA_ROOT, 'products/product_11/image/test_image.bmp')}")
    #     print(f"Папка существует? {os.path.exists(settings.MEDIA_ROOT)}")
    #     return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Метод отвечает за подготовку данных, которые полетят в HTML-шаблон"""
        context = super().get_context_data(**kwargs)
        pk = self.kwargs.get('pk')
        context['product'] = get_object_or_404(Product, pk=pk)
        context['page_name'] = 'product'
        return context


class ProductCreateView(CreateView):
    """Контроллер создания продукта"""
    model = Product
    fields = ("name", "description", "category", "price",)
    template_name = 'catalog/product_form.html'
    success_url = reverse_lazy("catalog:category_id")

    def get_context_data(self, **kwargs):
        """Позволяет добавлять медиафайлы"""
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['media_formset'] = ProductMediaFormSet(self.request.POST, self.request.FILES)
        else:
            data['media_formset'] = ProductMediaFormSet()
        return data

    def post(self, requests, pk):
        """Позволяет добавлять медиафайлы"""
        return redirect('catalog:product_detail', pk=pk)
    #
    # def dispatch(self, request, *args, **kwargs):
    #     """Дебаг-метод для проверки подключения контроллера"""
    #     # Этот принт сработает ПЕРВЫМ при любом обращении к этому URL
    #     print(">>> СИГНАЛ ПОЛУЧЕН: Запрос вошел в ProductCreateView")
    #     print(f">>> Данные пути (kwargs): {kwargs}")
    #     return super().dispatch(request, *args, **kwargs)

    def form_valid_before(self, form):
        """Дебаг-метод для проверки подключения контроллера"""
        context = self.get_context_data()
        media_formset = context['media_formset']
        with transaction.atomic():
            self.object = form.save()
            if media_formset.is_valid():
                media_formset.instance = self.object
                media_formset.save()
        return super().form_valid(form)

    def form_valid_after(self, form):
        """Дебаг-метод для проверки успешного создания продукта"""
        # Сначала сохраняем объект
        response = super().form_valid(form)

        # Теперь у нас есть self.object
        if self.object.image:
            print(f"--- ФАЙЛ СОЗДАН ---")

            print(f"Путь в БД: {self.object.image.name}")
            print(f"Абсолютный путь на диске: {self.object.image.path}")
            print(f"Существует ли файл физически? {os.path.exists(self.object.image.path)}")
        elif self.object.video:
            print(f"--- ФАЙЛ СОЗДАН ---")

            print(f"Путь в БД: {self.object.video.name}")
            print(f"Абсолютный путь на диске: {self.object.video.path}")
            print(f"Существует ли файл физически? {os.path.exists(self.object.video.path)}")

        return response


class ProductUpdateView(UpdateView):
    """Контроллер изменения информации продукта"""
    model = Product
    fields = ("name", "description", "category", "price",)
    template_name = 'catalog/product_form.html'

    def get_context_data(self, **kwargs):
        """Позволяет добавлять медиафайлы"""
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['media_formset'] = ProductMediaFormSet(self.request.POST, self.request.FILES)
        else:
            data['media_formset'] = ProductMediaFormSet()
        return data

    def post(self, requests, pk):
        """Позволяет добавлять медиафайлы"""
        return redirect('catalog:product_detail', pk=pk)

    def get_success_url(self):
        """Метод перенаправления на обновленную страницу товара"""
        success_url = reverse_lazy("catalog:product_detail", kwargs={'pk': self.object.pk})
        return success_url

    def form_valid(self, form):
        """Дебаг-метод для проверки успешного создания продукта"""
        # Сначала сохраняем объект
        response = super().form_valid(form)

        # Теперь у нас есть self.object
        if self.object.image:
            print(f"--- ФАЙЛ СОХРАНЕН ---")

            print(f"Путь в БД: {self.object.image.name}")
            print(f"Абсолютный путь на диске: {self.object.image.path}")
            print(f"Существует ли файл физически? {os.path.exists(self.object.image.path)}")
        elif self.object.video:
            print(f"--- ФАЙЛ СОХРАНЕН ---")

            print(f"Путь в БД: {self.object.video.name}")
            print(f"Абсолютный путь на диске: {self.object.video.path}")
            print(f"Существует ли файл физически? {os.path.exists(self.object.video.path)}")

        return response


class ProductDeleteView(DeleteView):
    """Контроллер удаления продукта"""
    model = Product

    def get_success_url(self):
        """Метод перенаправления на обновленную страницу категории"""
        category_id = self.object.category.id
        success_url = reverse_lazy("catalog:category", kwargs={'pk': category_id})
        return success_url


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
