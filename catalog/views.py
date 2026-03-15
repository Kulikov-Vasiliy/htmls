from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
    FormView,
    TemplateView,
    RedirectView,
)
from django.contrib import messages
from catalog.models import Product, Category
from catalog.forms import ProductMediaFormSet, ContactsForm, CategoryForm
from django.utils import timezone
from django.db import transaction
import os
from config import settings


# Create your views here.
class BaseTemplateView(TemplateView):
    """Контроллер позволяет считывать базовую страницу"""

    template_name = "catalog/base.html"


class ProductListView(ListView):
    """Контроллер позволяет наполнять базовую страницу: продуктами"""

    model = Product
    page_name = "category"
    template_name = "catalog/category.html"
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
        category_id = self.kwargs.get("category.pk")
        queryset = Product.objects.filter(category_id=self.kwargs.get("pk"))
        return queryset

    def get_context_data(self, **kwargs):
        """Метод переопределения контекста для получения данных о категории"""
        context = super().get_context_data(**kwargs)
        # Находим категорию по ID из URL и передаем в шаблон
        category_id = self.kwargs.get("pk")
        context["category"] = get_object_or_404(Category, pk=category_id)
        context["page_name"] = "category"
        return context


class ProductDetailView(DetailView):
    """Контроллер позволяет детализировать базовую страницу: информацией о продуктах"""

    model = Product
    page_name = "product"
    template_name = "catalog/product_detail.html"
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
        pk = self.kwargs.get("pk")
        context["product"] = get_object_or_404(Product, pk=pk)
        context["page_name"] = "product"
        return context


class ProductCreateView(CreateView):
    """Контроллер создания продукта"""

    model = Product
    fields = (
        "name",
        "description",
        "category",
        "price",
    )
    template_name = "catalog/product_form.html"
    success_url = reverse_lazy("catalog:category.pk")

    def get_context_data(self, **kwargs):
        """Позволяет добавлять медиафайлы"""
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data["media_formset"] = ProductMediaFormSet(
                self.request.POST, self.request.FILES
            )
        else:
            data["media_formset"] = ProductMediaFormSet()
        return data

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
        media_formset = context["media_formset"]
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
            print(
                f"Существует ли файл физически? {os.path.exists(self.object.image.path)}"
            )
        elif self.object.video:
            print(f"--- ФАЙЛ СОЗДАН ---")

            print(f"Путь в БД: {self.object.video.name}")
            print(f"Абсолютный путь на диске: {self.object.video.path}")
            print(
                f"Существует ли файл физически? {os.path.exists(self.object.video.path)}"
            )

        return response


class ProductUpdateView(UpdateView):
    """Контроллер изменения информации продукта"""

    model = Product
    fields = (
        "name",
        "description",
        "category",
        "price",
    )
    template_name = "catalog/product_form.html"

    def get_context_data(self, **kwargs):
        """Позволяет добавлять медиафайлы"""
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data["media_formset"] = ProductMediaFormSet(
                self.request.POST, self.request.FILES
            )
        else:
            data["media_formset"] = ProductMediaFormSet()
        return data

    def get_success_url(self):
        """Метод перенаправления на обновленную страницу товара"""
        success_url = reverse_lazy(
            "catalog:product_detail", kwargs={"pk": self.object.pk}
        )
        return success_url

    def form_valid_before(self, form):
        """Дебаг-метод для проверки подключения контроллера"""
        context = self.get_context_data()
        media_formset = context["media_formset"]
        with transaction.atomic():
            self.object = form.save()
            if media_formset.is_valid():
                media_formset.instance = self.object
                media_formset.save()
        return super().form_valid(form)

    def form_valid(self, form):
        """Дебаг-метод для проверки успешного создания продукта"""
        # Сначала сохраняем объект
        response = super().form_valid(form)

        # Теперь у нас есть self.object
        if self.object.image:
            print(f"--- ФАЙЛ СОХРАНЕН ---")

            print(f"Путь в БД: {self.object.image.name}")
            print(f"Абсолютный путь на диске: {self.object.image.path}")
            print(
                f"Существует ли файл физически? {os.path.exists(self.object.image.path)}"
            )
        elif self.object.video:
            print(f"--- ФАЙЛ СОХРАНЕН ---")

            print(f"Путь в БД: {self.object.video.name}")
            print(f"Абсолютный путь на диске: {self.object.video.path}")
            print(
                f"Существует ли файл физически? {os.path.exists(self.object.video.path)}"
            )

        return response


class ProductDeleteView(DeleteView):
    """Контроллер удаления продукта"""

    model = Product

    def get_success_url(self):
        """Метод перенаправления на обновленную страницу категории"""
        category_id = self.object.category.pk
        success_url = reverse_lazy("catalog:category", kwargs={"pk": category_id})
        return success_url


class ContactsFormView(FormView):
    """Контроллер позволяет наполнять базовую страницу: контактами"""

    template_name = "catalog/contacts.html"
    form_class = ContactsForm
    success_url = reverse_lazy("catalog:contacts")

    def get_context_data(self, **kwargs):
        """Получение наполнения"""
        context = super().get_context_data(**kwargs)
        context["page_name"] = "contacts"
        return context

    def form_valid(self, form):
        """Метод позволяет обработать данные формы при успешной отправке"""
        messages.success(self.request, "success")  # Метка для JS
        return super().form_valid(form)

    def form_invalid(self, form):
        """Метод позволяет обработать данные формы при провале отправки"""
        if form.errors:
            messages.error(self.request, "error", extra_tags="known_error")
        else:
            # Если форма верная, но что-то пошло не так (неизвестная ошибка)
            messages.error(self.request, "error", extra_tags="unknown_error")

        return super().form_invalid(form)


class HomeListView(ListView):
    """Контроллер позволяет наполнять базовую страницу: продуктами"""

    model = Product
    page_name = "home"
    template_name = "catalog/home.html"

    def get_queryset(self, **kwargs):
        """Получение заполнения макета с фильтрацией"""
        # Заготовка на будущее пока что
        queryset = Product.objects.all()
        filter_type = self.request.GET.get("filter")

        if filter_type == "top":
            queryset = queryset.order_by(
                "-popularity"
            )  # Предполагается, что есть поле popularity
        elif filter_type == "recent":
            # Здесь нужно добавить логику для последних просмотренных
            pass

        return queryset

    def dispatch(self, request, *args, **kwargs):
        """Дебаг-метод для проверки подключения контроллера"""
        # Этот принт сработает ПЕРВЫМ при любом обращении к этому URL
        print(">>> СИГНАЛ ПОЛУЧЕН: Запрос вошел в HomeListView")
        print(f"Папка существует? {os.path.exists(settings.MEDIA_ROOT)}")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Метод отвечает за подготовку данных, которые полетят в HTML-шаблон"""
        context = super().get_context_data(**kwargs)
        context["page_name"] = "home"
        return context


class CategoryCreateView(CreateView):
    """Контроллер создания категории"""

    model = Category
    fields = ("name", "description", "image")
    template_name = "catalog/category_form.html"
    success_url = reverse_lazy("catalog:catalogue")

    def get_context_data(self, **kwargs):
        """Позволяет добавлять медиафайлы"""
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            # При обновлении ОБЯЗАТЕЛЬНО передаем instance=self.object
            # и request.FILES (иначе картинки не загрузятся)
            data["media_formset"] = CategoryForm(
                self.request.POST, self.request.FILES, instance=self.object
            )
        else:
            # Если это просто открытие страницы (GET), подтягиваем
            # уже существующие в базе картинки для этой категории
            data["media_formset"] = CategoryForm(instance=self.object)
        return data

    #
    # def dispatch(self, request, *args, **kwargs):
    #     """Дебаг-метод для проверки подключения контроллера"""
    #     # Этот принт сработает ПЕРВЫМ при любом обращении к этому URL
    #     print(">>> СИГНАЛ ПОЛУЧЕН: Запрос вошел в CategoryCreateView")
    #     print(f">>> Данные пути (kwargs): {kwargs}")
    #     return super().dispatch(request, *args, **kwargs)

    def form_valid_before(self, form):
        """Дебаг-метод для проверки подключения контроллера"""
        context = self.get_context_data()
        media_formset = context["media_formset"]
        with transaction.atomic():
            self.object = form.save()
            if media_formset.is_valid():
                media_formset.instance = self.object
                media_formset.save()
        return super().form_valid(form)

    def form_valid_after(self, form):
        """Дебаг-метод для проверки успешного создания категории"""
        # Сначала сохраняем объект
        response = super().form_valid(form)

        # Теперь у нас есть self.object
        if self.object.image:
            print(f"--- ФАЙЛ СОЗДАН ---")

            print(f"Путь в БД: {self.object.image.name}")
            print(f"Абсолютный путь на диске: {self.object.image.path}")
            print(
                f"Существует ли файл физически? {os.path.exists(self.object.image.path)}"
            )
        return response


class CategoryUpdateView(UpdateView):
    """Контроллер изменения информации категории"""

    model = Category
    fields = (
        "name",
        "description",
        "image",
    )
    template_name = "catalog/category_form.html"

    def get_context_data(self, **kwargs):
        """Позволяет добавлять медиафайлы"""
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            if self.request.POST:
                # При обновлении ОБЯЗАТЕЛЬНО передаем instance=self.object
                # и request.FILES (иначе картинки не загрузятся)
                data["media_formset"] = CategoryForm(
                    self.request.POST, self.request.FILES, instance=self.object
                )
            else:
                # Если это просто открытие страницы (GET), подтягиваем
                # уже существующие в базе картинки для этой категории
                data["media_formset"] = CategoryForm(instance=self.object)

        return data

    def get_success_url(self):
        """Метод перенаправления на обновленную страницу категории"""
        success_url = reverse_lazy("catalog:category", kwargs={"pk": self.object.id})
        return success_url

    def form_valid_before(self, form):
        """Дебаг-метод для проверки подключения контроллера"""
        context = self.get_context_data()
        media_formset = context["media_formset"]
        with transaction.atomic():
            self.object = form.save()
            if media_formset.is_valid():
                media_formset.instance = self.object
                media_formset.save()
        return super().form_valid(form)

    def form_valid(self, form):
        """Дебаг-метод для проверки успешного создания категории"""
        # Сначала сохраняем объект
        response = super().form_valid(form)

        # Теперь у нас есть self.object
        if self.object.image:
            print(f"--- ФАЙЛ СОХРАНЕН ---")

            print(f"Путь в БД: {self.object.image.name}")
            print(f"Абсолютный путь на диске: {self.object.image.path}")
            print(
                f"Существует ли файл физически? {os.path.exists(self.object.image.path)}"
            )

        return response


class CategoryDeleteView(DeleteView):
    """Контроллер удаления категории"""

    model = Category

    def get_success_url(self):
        """Метод перенаправления на обновленную страницу категории"""
        success_url = reverse_lazy("catalog:catalogue")
        return success_url


class CatalogueListView(ListView):
    """Контроллер позволяет наполнять базовую страницу: каталогом"""

    page_name = "catalogue"
    template_name = "catalog/catalogue.html"
    context_object_name = "catalogue"

    def get_context_data(self, **kwargs):
        """Метод переопределения контекста для получения данных о категории"""
        context = super().get_context_data(**kwargs)
        context["page_name"] = "catalogue"
        return context

    def get_queryset(self, **kwargs):
        """Получение данных заполнения"""
        queryset = Category.objects.all()
        return queryset


class BlogRedirectView(RedirectView):
    """Перенаправляем пользователя на главную страницу блога"""

    def get_redirect_url(self, *args, **kwargs):
        """"""
        print("Пользователь перешел в блог")
        return super().get_redirect_url(*args, **kwargs)

    pattern_name = "blog:home"
