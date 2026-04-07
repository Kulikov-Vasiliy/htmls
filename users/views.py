from django.shortcuts import render, get_object_or_404, redirect

from django.urls import reverse_lazy, reverse
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
    FormView,
)
from users.models import User, UserActivity, Moderator
from users.forms import (
    UserActivityForm,
    UserControlForm,
    UserSubscriptionForm,
    UserDeletionForm,
    UserCreationForm,
    UserUpdateForm,
    ModeratorBaseForm,
    ModeratorCreationForm,
    ModeratorUpdateForm,
    ModeratorDeletionForm,
)

from django.utils import timezone
from django.db import transaction
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib import messages
from django.contrib.auth import login as auth_login
import os

# Create your views here.

class SignInFormView(FormView):
    """Авторизация"""
    template_name = "users/users/sign_in.html"
    page_name = "entry"

    def form_valid(self, form):
        """Валидация пользователя"""
        # Получаем очищенные данные из формы
        u_login = form.cleaned_data.get('login')
        # password = form.cleaned_data.get('password')  # Если добавите поле пароля

        # Находим пользователя (пока без пароля можно использовать .get())
        user_obj = User.objects.filter(username=u_login).first()

        if user_obj:
            auth_login(self.request, user_obj)

            # Вызываем функцию входа, передав объект пользователя
            if user_obj.is_staff:
                messages.success(self.request, "Вход выполнен (Модератор)")
            else:
                messages.success(self.request, "Вход выполнен (Пользователь)")

            return super().form_valid(form)
        else:
            form.add_error('login', 'Пользователь не найден')
            return self.form_invalid(form)

    def get_success_url(self):
        """Куда перейти при успешном входе"""
        if self.request.user.is_staff:
            return reverse_lazy("users:moderator", kwargs={'pk': self.request.user.pk})
        return reverse_lazy("blog:home")


class UserCreateView(CreateView):
    """Контроллер создания пользователя"""
    model = User
    form_class = UserCreationForm
    template_name = "users/users/user_form.html"
    page_name = "sign_up"

    def get_success_url(self):
        return reverse_lazy("users:user_detail", kwargs={"pk": self.object.pk})

    def dispatch(self, request, *args, **kwargs):
        """Дебаг-метод для проверки подключения контроллера"""
        # Этот принт сработает ПЕРВЫМ при любом обращении к этому URL
        print(">>> СИГНАЛ ПОЛУЧЕН: Запрос вошел в UserCreateView")
        print(f">>> Данные пути (kwargs): {kwargs}")
        return super().dispatch(request, *args, **kwargs)


class UserUpdateView(UpdateView):
    """Контроллер создания пользователя"""
    model = User
    form_class = UserUpdateForm
    template_name = "users/users/user_form.html"

    def get_success_url(self):
        return reverse_lazy("users:user_detail", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        """Позволяет добавлять медиафайлы"""
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data["media_formset"] = UserUpdateForm(
                self.request.POST, self.request.FILES
            )
        else:
            data["media_formset"] = UserUpdateForm()
        return data


class UserDetailView(DetailView):
    """Информация пользователя"""
    model = User
    page_name = 'profile'
    template_name = "users/users/user_detail.html"

    # def dispatch(self, request, *args, **kwargs):
    #     """Дебаг-метод для проверки подключения контроллера"""
    #     # Этот принт сработает ПЕРВЫМ при любом обращении к этому URL
    #     print(">>> СИГНАЛ ПОЛУЧЕН: Запрос вошел в UserDetailView")
    #     print(f">>> Данные пути (kwargs): {kwargs}")
    #     print(f"Ищу файл тут: {os.path.join(settings.MEDIA_ROOT, 'products/product_11/image/test_image.bmp')}")
    #     print(f"Папка существует? {os.path.exists(settings.MEDIA_ROOT)}")
    #     return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["subscription_form"] = UserSubscriptionForm()
        return context

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # Автоматическая запись активности БЕЗ ФОРМЫ

        UserActivity.objects.create(
            user=self.request.user,
            post=None,  # Если это профиль, а не пост
            content_object=obj  # Или другая логика связи
        )
        return obj


class UserListView(ListView):
    """Информация пользователя"""
    model = User
    form_class = UserControlForm
    page_name = 'user_list'
    template_name = "users/moderators/user_form.html"

    def get_queryset(self):
        # 1. Берем базовый набор (например, всех не удаленных по умолчанию)
        queryset = User.objects.all()

        # 2. Получаем фильтр из URL (например, ?status=staff)
        search_query = self.request.GET.get('search')

        # 3. Применяем фильтры, если они переданы
        if search_query:
            queryset = queryset.filter(login__icontains=search_query)

        return queryset.order_by('-joined_at', '-nickname')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_name"] = "user_list"
        # Прокидываем текущий поиск обратно в шаблон, чтобы в инпуте остался текст
        context["search_value"] = self.request.GET.get('search', '')
        return context


class UserDeleteView(DeleteView):
    """Удаление пользователя"""
    model = User
    form_class = UserDeletionForm
    template_name = "users/users/user_detail.html"

    def get_success_url(self):
        reverse_lazy("blog:home")


class ModeratorCreateView(CreateView):
    """Контроллер создания пользователя"""
    model = Moderator
    form_class = ModeratorCreationForm
    template_name = "users/moderators/moderator_form.html"

    def get_success_url(self):
        return reverse_lazy("users:moderator_detail", kwargs={"pk": self.object.pk})

    # def dispatch(self, request, *args, **kwargs):
    #     """Дебаг-метод для проверки подключения контроллера"""
    #     # Этот принт сработает ПЕРВЫМ при любом обращении к этому URL
    #     print(">>> СИГНАЛ ПОЛУЧЕН: Запрос вошел в UserCreateView")
    #     print(f">>> Данные пути (kwargs): {kwargs}")
    #     return super().dispatch(request, *args, **kwargs)


class ModeratorUpdateView(UpdateView):
    """Контроллер создания пользователя"""
    model = Moderator
    form_class = ModeratorUpdateForm
    template_name = "users/moderators/moderator_form.html"

    def get_success_url(self):
        return reverse_lazy("users:user_detail", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        """Позволяет добавлять медиафайлы"""
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data["media_formset"] = ModeratorUpdateForm(
                self.request.POST, self.request.FILES
            )
        else:
            data["media_formset"] = ModeratorUpdateForm()
        return data


class ModeratorDetailView(DetailView):
    """Информация пользователя"""
    model = Moderator
    form_class = ModeratorBaseForm
    template_name = "users/moderators/moderator_detail.html"
    page_name = 'moderator'

    # def dispatch(self, request, *args, **kwargs):
    #     """Дебаг-метод для проверки подключения контроллера"""
    #     # Этот принт сработает ПЕРВЫМ при любом обращении к этому URL
    #     print(">>> СИГНАЛ ПОЛУЧЕН: Запрос вошел в UserDetailView")
    #     print(f">>> Данные пути (kwargs): {kwargs}")
    #     print(f"Ищу файл тут: {os.path.join(settings.MEDIA_ROOT, 'products/product_11/image/test_image.bmp')}")
    #     print(f"Папка существует? {os.path.exists(settings.MEDIA_ROOT)}")
    #     return super().dispatch(request, *args, **kwargs)


class ModeratorsListView(ListView):
    """Список модераторов"""
    model = Moderator
    form_class = ModeratorBaseForm
    template_name = "users/moderators/moderator_list.html"
    page_name = 'moderator_list'

    def get_queryset(self):
        # 1. Берем базовый набор (например, всех не удаленных по умолчанию)
        queryset = Moderator.objects.filter(is_deleted=False)

        # 2. Получаем фильтр из URL (например, ?status=staff)
        status_filter = self.request.GET.get('status')
        search_query = self.request.GET.get('search')

        # 3. Применяем фильтры, если они переданы
        if status_filter == 'staff':
            queryset = queryset.filter(is_staff=True)

        if search_query:
            queryset = queryset.filter(login__icontains=search_query)

        return queryset.order_by('-joined_at', 'first_name', 'last_name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_name"] = "moderator_list"
        # Прокидываем текущий поиск обратно в шаблон, чтобы в инпуте остался текст
        context["search_value"] = self.request.GET.get('search', '')
        return context

    # def dispatch(self, request, *args, **kwargs):
    #     """Дебаг-метод для проверки подключения контроллера"""
    #     # Этот принт сработает ПЕРВЫМ при любом обращении к этому URL
    #     print(">>> СИГНАЛ ПОЛУЧЕН: Запрос вошел в ModeratorListView")
    #     print(f">>> Данные пути (kwargs): {kwargs}")
    #     print(f"Ищу файл тут: {os.path.join(settings.MEDIA_ROOT, 'products/product_11/image/test_image.bmp')}")
    #     print(f"Папка существует? {os.path.exists(settings.MEDIA_ROOT)}")
    #     return super().dispatch(request, *args, **kwargs)


class ModeratorDeleteView(DeleteView):
    """Удаление пользователя"""
    model = Moderator
    form_class = ModeratorDeletionForm
    template_name = "users/moderators/moderator_list.html"

    def get_success_url(self):
        reverse_lazy("users:moderator_list")