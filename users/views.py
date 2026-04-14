from django.shortcuts import render, get_object_or_404, redirect

from django.urls import reverse_lazy, reverse
from django.core.mail import send_mail
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
    SignInForm,
)

from django.utils import timezone
from django.db import transaction
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages

from config.settings import EMAIL_HOST_USER

import os
import secrets



# Create your views here.

class SignInFormView(FormView):
    """Авторизация"""
    form_class = SignInForm
    template_name = "users/sign_in.html"
    page_name = "entry"

    def form_valid(self, form):
        """Валидация пользователя"""
        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password')

        # authenticate() сама опросит UserBackend и ModeratorBackend
        # и вернет либо объект User, либо объект Moderator
        user_obj = authenticate(self.request, email=email, password=password)

        if user_obj is not None:
            if user_obj.is_active:
                auth_login(self.request, user_obj)

                # Теперь разделяем редирект по типу модели
                if isinstance(user_obj, Moderator):
                    messages.success(self.request, f"Вход выполнен (Модератор: {user_obj.login})")
                    return redirect("users:moderator", pk=user_obj.pk)

                messages.success(self.request, "Вход выполнен (Пользователь)")
                return redirect("users:profile", pk=user_obj.pk)
            else:
                form.add_error('email', 'Аккаунт не активирован.')
                return self.form_invalid(form)
        else:
            # Если authenticate вернул None, значит либо email, либо пароль неверны
            form.add_error(None, 'Неверный email или пароль')
            return self.form_invalid(form)

    # def get_success_url(self):
    #     """Куда перейти при успешном входе"""
    #     if self.request.user.is_staff:
    #         return reverse_lazy("users:moderator", kwargs={'pk': self.request.user.pk})
    #     return reverse_lazy("blog:home")

    def form_invalid(self, form):
        """Отображает что введено неверно"""
        print(">>> ФОРМА НЕВАЛИДНА!")
        print(f">>> Ошибки: {form.errors}")
        return super().form_invalid(form)


class UserCreateView(CreateView):
    """Контроллер создания пользователя"""
    model = User
    form_class = UserCreationForm
    template_name = "users/user_form.html"
    page_name = "sign_up"

    def get_success_url(self):
        return reverse_lazy("users:entry")

    def dispatch(self, request, *args, **kwargs):
        """Дебаг-метод для проверки подключения контроллера"""
        # Этот принт сработает ПЕРВЫМ при любом обращении к этому URL
        print(">>> СИГНАЛ ПОЛУЧЕН: Запрос вошел в UserCreateView")
        print(f">>> Данные пути (kwargs): {kwargs}")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """Отправка письма для подтверждения пользователя"""
        user = form.save(commit=False)
        user.is_active = False

        user.set_password(form.cleaned_data['password'])

        token = secrets.token_hex(16)
        user.token = token
        user.save()

        host = self.request.get_host()
        url = f"http://{host}/users/email-confirmation/{token}/"
        send_mail(
            subject="Подтверждение почты",
            message=f"""
            Здравствуй, уважаемый пользователь!
  При регистрации в нашем приложении был указан Ваш email-адрес.
Если это Ваша почта - чтобы подтвердить личность, перейдите по ссылке.
{url}

Если это письмо пришло по ошибке, то проигнорируйте его.
""",
            from_email=EMAIL_HOST_USER,
            recipient_list=[user.email],
        )

        return super().form_valid(form)

    def form_invalid(self, form):
        """Отображает что введено неверно"""
        print(">>> ФОРМА НЕВАЛИДНА!")
        print(f">>> Ошибки: {form.errors}")
        return super().form_invalid(form)


def email_verification(request, token):
    """Контроллер подтверждения"""
    user = get_object_or_404(User, token=token)
    user.is_active = True
    user.save()
    messages.success(request, "Почта подтверждена! Теперь вы можете войти.")
    return redirect(reverse("users:entry"))


class UserUpdateView(UpdateView):
    """Контроллер обновления пользователя"""
    model = User
    form_class = UserUpdateForm
    template_name = "users/user_form.html"

    def get_success_url(self):
        return reverse_lazy("users:profile", kwargs={"pk": self.object.pk})

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
    template_name = "users/user_detail.html"

    # def dispatch(self, request, *args, **kwargs):
    #     """Дебаг-метод для проверки подключения контроллера"""
    #     # Этот принт сработает ПЕРВЫМ при любом обращении к этому URL
    #     print(">>> СИГНАЛ ПОЛУЧЕН: Запрос вошел в UserDetailView")
    #     print(f">>> Данные пути (kwargs): {kwargs}")
    #     print(f"Ищу файл тут: {os.path.join(settings.MEDIA_ROOT, 'products/product_11/image/test_image.bmp')}")
    #     print(f"Папка существует? {os.path.exists(settings.MEDIA_ROOT)}")
    #     return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Получение данных пользователя"""
        context = super().get_context_data(**kwargs)
        context["subscription_form"] = UserSubscriptionForm()
        return context

    def get_object(self, queryset=None):
        """Привязка пользователя к бд"""
        obj = super().get_object(queryset)

        # Проверяем, авторизован ли тот, кто зашел на страницу
        if self.request.user.is_authenticated:
            UserActivity.objects.get_or_create(
                user=self.request.user,
                post=None,
            )
        return obj


class UserListView(ListView):
    """Информация пользователя"""
    model = User
    form_class = UserControlForm
    page_name = 'user_list'
    template_name = "users/moderators/user_list.html"

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
    template_name = "users/deletion_window.html"

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