from django.shortcuts import render, get_object_or_404, redirect

from django.urls import reverse_lazy, reverse
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
from blog.models import User, Post, Comment, UserActivity, Subscription, Categories, Moderator
from blog.forms import (
    CategoriesForm,
    PostModeratedControlForm,
    CommentModerationControlForm,
    CommentForm,
    CommentMediaFormSet,
    UserActivityForm,
    UserControlForm,
    UserSubscriptionForm,
    UserDeletionForm,
    UserCreationForm,
    UserUpdateForm,
    PostForm,
    PostDeletionForm,
    PostUpdateForm,
    PostCreationForm,
    PostBaseForm,
    PostMediaFormSet,
    ModeratorBaseForm,
    ModeratorCreationForm,
    ModeratorUpdateForm,
    ModeratorDeletionForm,
)
from django.db.models import F
from django.utils import timezone
from django.db import transaction
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib import messages
from django.contrib.auth import login as auth_login
import os


from config import settings
# from langchain_core.messages import SystemMessage, HumanMessage
# from blog.utils import system_instruction, POST_FORMATTER_PROMPT
# from langchain_openai import ChatOpenAI

# model = ChatOpenAI(model="gpt-4o", api_key="ваш_ключ")


# Create your views here.
class BaseTemplateView(TemplateView):
    """Контроллер позволяет считывать базовую страницу"""
    template_name = "blog/base.html"


class SignInFormView(FormView):
    """Авторизация
    * пока без паролей"""
    template_name = "blog/includes/sign_in.html"
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
            return reverse_lazy("blog:moderator", kwargs={'pk': self.request.user.pk})
        return reverse_lazy("blog:home")


class CatalogRedirectView(RedirectView):
    """Перенаправляем пользователя на главную приложения catalog"""

    def get_redirect_url(self, *args, **kwargs):
        """"""
        print("Пользователь перешел в каталог")
        return super().get_redirect_url(*args, **kwargs)

    pattern_name = "catalog:main"


class HomeListView(ListView):
    """Контроллер позволяет наполнять базовую страницу: """
    model = Post
    page_name = "home"
    context_object_name = 'posts'
    template_name = 'blog/home.html'

    def get_queryset(self, **kwargs):
        """Получение заполнения макета с фильтрацией"""
        # Заготовка на будущее пока что
        queryset = Post.objects.all()
        filter_type = self.request.GET.get("filter")

        if filter_type == "top":
            queryset = queryset.order_by(
                "-popularity"
            )  # Предполагается, что есть поле popularity
        elif filter_type == "newer":
            queryset = queryset.order_by(
                "-created_at"
            )
        elif filter_type == "older":
            queryset = queryset.order_by(
                "created_at"
            )

        return queryset

    # def dispatch(self, request, *args, **kwargs):
    #     """Дебаг-метод для проверки подключения контроллера"""
    #     # Этот принт сработает ПЕРВЫМ при любом обращении к этому URL
    #     print(">>> СИГНАЛ ПОЛУЧЕН: Запрос вошел в HomeListView")
    #     print(f"Папка существует? {os.path.exists(settings.MEDIA_ROOT)}")
    #     return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Метод отвечает за подготовку данных, которые полетят в HTML-шаблон"""
        context = super().get_context_data(**kwargs)
        context['page_name'] = 'home'
        return context


class UserCreateView(CreateView):
    """Контроллер создания пользователя"""
    model = User
    form_class = UserCreationForm
    template_name = "blog/users/user_form.html"
    page_name = "sign_up"

    def get_success_url(self):
        return reverse_lazy("blog:user_detail", kwargs={"pk": self.object.pk})

    # def dispatch(self, request, *args, **kwargs):
    #     """Дебаг-метод для проверки подключения контроллера"""
    #     # Этот принт сработает ПЕРВЫМ при любом обращении к этому URL
    #     print(">>> СИГНАЛ ПОЛУЧЕН: Запрос вошел в UserCreateView")
    #     print(f">>> Данные пути (kwargs): {kwargs}")
    #     return super().dispatch(request, *args, **kwargs)


class UserUpdateView(UpdateView):
    """Контроллер создания пользователя"""
    model = User
    form_class = UserUpdateForm
    template_name = "blog/users/user_form.html"

    def get_success_url(self):
        return reverse_lazy("blog:user_detail", kwargs={"pk": self.object.pk})

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
    template_name = "blog/users/user_detail.html"

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
    template_name = "blog/moderators/user_form.html"

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
    template_name = "blog/users/user_detail.html"

    def get_success_url(self):
        reverse_lazy("blog:home")


class ModeratorCreateView(CreateView):
    """Контроллер создания пользователя"""
    model = Moderator
    form_class = ModeratorCreationForm
    template_name = "blog/moderators/moderator_form.html"

    def get_success_url(self):
        return reverse_lazy("blog:moderator_detail", kwargs={"pk": self.object.pk})

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
    template_name = "blog/moderators/moderator_form.html"

    def get_success_url(self):
        return reverse_lazy("blog:user_detail", kwargs={"pk": self.object.pk})

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
    template_name = "blog/moderators/moderator_detail.html"
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
    template_name = "blog/moderators/moderator_list.html"
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
    template_name = "blog/moderators/moderator_list.html"

    def get_success_url(self):
        reverse_lazy("blog:moderator_list")


class PostCreateView(CreateView):
    """Создает пост"""
    model = Post
    form_class = PostCreationForm

    def get_success_url(self):
        return reverse_lazy("blog:post_detail", kwargs={"pk": self.object.pk})

    def form_valid_user_authorship(self, form):
        """Автоматически назначаем автора текущего пользователя"""
        form.instance.author = self.request.user
        return super().form_valid(form)

    # def dispatch(self, request, *args, **kwargs):
    #     """Дебаг-метод для проверки подключения контроллера"""
    #     # Этот принт сработает ПЕРВЫМ при любом обращении к этому URL
    #     print(">>> СИГНАЛ ПОЛУЧЕН: Запрос вошел в PostCreateView")
    #     print(f">>> Данные пути (kwargs): {kwargs}")
    #     return super().dispatch(request, *args, **kwargs)
    #
    #
    # def ai_format_text(request):
    #     """ИИ-подгон стилизации текста при нажатии кнопок(B/I)
    #     пока не внедрено"""
    #     if request.method == "POST":
    #         user_text = request.POST.get("text")
    #         action = request.POST.get("action")
    #
    #         # 1. Выбираем инструкцию
    #         if action in ["разбей на разделы", "структурируй"]:
    #             # Используем промпт для H2/H3
    #             system_prompt = POST_FORMATTER_PROMPT
    #         else:
    #             # Используем промпт для кнопок (B, I, таблицы и т.д.)
    #             system_prompt = system_instruction.content
    #
    #         # 2. Обращаемся к ИИ
    #         ai_response = model.invoke([
    #             SystemMessage(content=system_prompt),
    #             HumanMessage(content=f"Действие: {action}. Текст: {user_text}")
    #         ])
    #
    #         return JsonResponse({"result": ai_response.content})

    def get_context_data(self, **kwargs):
        """Позволяет добавлять медиафайлы"""
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data["media_formset"] = PostMediaFormSet(
                self.request.POST, self.request.FILES
            )
        else:
            data["media_formset"] = PostMediaFormSet()

        return data

    def form_valid(self, form):
        """Позволяет работать с медиафайлами"""
        context = self.get_context_data()
        media_formset = context["media_formset"]

        with transaction.atomic():
            # 1. Подготовка и сохранение основного объекта
            self.object = form.save(commit=False)
            self.object.author = self.request.user
            self.object.post_id = self.kwargs.get('pk')  # ID поста из URL
            self.object.save()

            # 2. Валидация и сохранение медиа-формсета
            if media_formset.is_valid():
                media_formset.instance = self.object
                media_formset.save()
            else:
                # Если картинки «кривые», откатываем транзакцию и показываем ошибки
                return self.form_invalid(form)

        # 3. Дебаг
        if hasattr(self.object, 'image') and self.object.image:
            print(f"Файл создан: {self.object.image.path}")
        elif hasattr(self.object, 'video') and self.object.video:
            print(f"Файл создан: {self.object.video.path}")

        # 4. Финальный редирект
        return HttpResponseRedirect(self.get_success_url())


class PostDetailView(DetailView):
    """Просмотр поста"""
    model = Post
    page_name = 'post_detail'
    form_class = PostBaseForm

    def get_object(self, queryset=None):
        """Получаем пост и увеличиваем n просмотров на 1"""
        # 1. Получаем сам объект поста
        obj = super().get_object(queryset=queryset)

        # 2. Проверяем: если пользователь залогинен и он НЕ автор поста
        if self.request.user.is_authenticated:
            if obj.author != self.request.user:
                # Используем F-выражение для защиты от ошибок одновременной записи
                obj.views_count = F('viewed') + 1
                obj.save(update_fields=['viewed'])
                # Обновляем объект, чтобы в шаблоне число тоже было актуальным
                obj.refresh_from_db()
        else:
            # Если нужно считать просмотры и от анонимов:
            obj.views_count = F('viewed') + 1
            obj.save(update_fields=['viewed'])
            obj.refresh_from_db()

        return obj

    # def dispatch(self, request, *args, **kwargs):
    #     """Дебаг-метод для проверки подключения контроллера"""
    #     # Этот принт сработает ПЕРВЫМ при любом обращении к этому URL
    #     print(">>> СИГНАЛ ПОЛУЧЕН: Запрос вошел в PostDetailView")
    #     print(f">>> Данные пути (kwargs): {kwargs}")
    #     print(f"Ищу файл тут: {os.path.join(settings.MEDIA_ROOT, 'products/product_11/image/test_image.bmp')}")
    #     print(f"Папка существует? {os.path.exists(settings.MEDIA_ROOT)}")
    #     return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["post"] = PostForm()
        return context


class PostUpdateView(UpdateView):
    """Обновление поста"""
    model = Post
    form_class = PostUpdateForm

    def get_success_url(self):
        """Меняет путь к обновленному посту"""
        return reverse_lazy("blog:post_detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        context = self.get_context_data()
        media_formset = context["media_formset"]

        with transaction.atomic():
            # 1. Подготовка и сохранение основного объекта
            self.object = form.save(commit=False)
            self.object.author = self.request.user
            self.object.post_id = self.kwargs.get('pk')  # ID поста из URL
            self.object.save()

            # 2. Валидация и сохранение медиа-формсета
            if media_formset.is_valid():
                media_formset.instance = self.object
                media_formset.save()
            else:
                # Если картинки «кривые», откатываем транзакцию и показываем ошибки
                return self.form_invalid(form)

        # 3. Дебаг
        if hasattr(self.object, 'image') and self.object.image:
            print(f"Файл создан: {self.object.image.path}")
        elif hasattr(self.object, 'video') and self.object.video:
            print(f"Файл создан: {self.object.video.path}")

        # 4. Финальный редирект
        return HttpResponseRedirect(self.get_success_url())

    # def dispatch(self, request, *args, **kwargs):
    #     """Дебаг-метод для проверки подключения контроллера"""
    #     # Этот принт сработает ПЕРВЫМ при любом обращении к этому URL
    #     print(">>> СИГНАЛ ПОЛУЧЕН: Запрос вошел в PostUpdateView")
    #     print(f">>> Данные пути (kwargs): {kwargs}")
    #     return super().dispatch(request, *args, **kwargs)
    #
    # def ai_format_text(request):
    #     """ИИ-подгон стилизации текста при нажатии кнопок(B/I)
    #     пока не внедрено"""
    #     if request.method == "POST":
    #         user_text = request.POST.get("text")
    #         action = request.POST.get("action")
    #
    #         # 1. Выбираем инструкцию
    #         if action in ["разбей на разделы", "структурируй"]:
    #             # Используем промпт для H2/H3
    #             system_prompt = POST_FORMATTER_PROMPT
    #         else:
    #             # Используем промпт для кнопок (B, I, таблицы и т.д.)
    #             system_prompt = system_instruction.content
    #
    #         # 2. Обращаемся к ИИ
    #         ai_response = model.invoke([
    #             SystemMessage(content=system_prompt),
    #             HumanMessage(content=f"Действие: {action}. Текст: {user_text}")
    #         ])
    #
    #         return JsonResponse({"result": ai_response.content})

    def get_context_data(self, **kwargs):
        """Позволяет добавлять медиафайлы"""
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data["media_formset"] = PostMediaFormSet(
                self.request.POST, self.request.FILES
            )
        else:
            data["media_formset"] = PostMediaFormSet()

        return data


class PostDeleteView(DeleteView):
    """Удаление поста"""
    model = Post
    form_class = PostDeletionForm

    def get_success_url(self):
        reverse_lazy("blog:home")


class CommentCreateView(CreateView):
    """Создание комментария к посту"""
    model = Comment
    form_class = CommentForm

    def get_success_url(self):
        return reverse("blog:post_detail", kwargs={"pk": self.object.post.pk})

    def form_valid(self, form):
        context = self.get_context_data()
        media_formset = context["media_formset"]

        with transaction.atomic():
            # 1. Подготовка и сохранение основного объекта
            self.object = form.save(commit=False)
            self.object.author = self.request.user
            self.object.post_id = self.kwargs.get('pk')  # ID поста из URL
            self.object.save()

            # 2. Валидация и сохранение медиа-формсета
            if media_formset.is_valid():
                media_formset.instance = self.object
                media_formset.save()
            else:
                # Если картинки «кривые», откатываем транзакцию и показываем ошибки
                return self.form_invalid(form)

        # 3. Дебаг
        if hasattr(self.object, 'image') and self.object.image:
            print(f"Файл создан: {self.object.image.path}")
        elif hasattr(self.object, 'video') and self.object.video:
            print(f"Файл создан: {self.object.video.path}")

        # 4. Финальный редирект
        return HttpResponseRedirect(self.get_success_url())

    # def dispatch(self, request, *args, **kwargs):
    #     """Дебаг-метод для проверки подключения контроллера"""
    #     # Этот принт сработает ПЕРВЫМ при любом обращении к этому URL
    #     print(">>> СИГНАЛ ПОЛУЧЕН: Запрос вошел в CommentCreateView")
    #     print(f">>> Данные пути (kwargs): {kwargs}")
    #     return super().dispatch(request, *args, **kwargs)

    # def ai_format_text(request):
    #     """ИИ-подгон стилизации текста при нажатии кнопок(B/I)
    #     пока не внедрено"""
    #     if request.method == "POST":
    #         user_text = request.POST.get("text")
    #         action = request.POST.get("action")
    #
    #         # 1. Выбираем инструкцию
    #         if action in ["разбей на разделы", "структурируй"]:
    #             # Используем промпт для H2/H3
    #             system_prompt = POST_FORMATTER_PROMPT
    #         else:
    #             # Используем промпт для кнопок (B, I, таблицы и т.д.)
    #             system_prompt = system_instruction.content
    #
    #         # 2. Обращаемся к ИИ
    #         ai_response = model.invoke([
    #             SystemMessage(content=system_prompt),
    #             HumanMessage(content=f"Действие: {action}. Текст: {user_text}")
    #         ])
    #
    #         return JsonResponse({"result": ai_response.content})

    def get_context_data(self, **kwargs):
        """Позволяет добавлять медиафайлы"""
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data["media_formset"] = CommentForm(
                self.request.POST, self.request.FILES
            )
        else:
            data["media_formset"] = CommentForm()

        return data


class CommentUpdateView(UpdateView):
    """Создание комментария к посту"""
    model = Comment
    form_class = CommentForm

    # def dispatch(self, request, *args, **kwargs):
    #     """Дебаг-метод для проверки подключения контроллера"""
    #     # Этот принт сработает ПЕРВЫМ при любом обращении к этому URL
    #     print(">>> СИГНАЛ ПОЛУЧЕН: Запрос вошел в CommentUpdateView")
    #     print(f">>> Данные пути (kwargs): {kwargs}")
    #     return super().dispatch(request, *args, **kwargs)
    #
    # def ai_format_text(request):
    #     """ИИ-подгон стилизации текста при нажатии кнопок(B/I)
    #     пока не внедрено"""
    #     if request.method == "POST":
    #         user_text = request.POST.get("text")
    #         action = request.POST.get("action")
    #
    #         # 1. Выбираем инструкцию
    #         if action in ["разбей на разделы", "структурируй"]:
    #             # Используем промпт для H2/H3
    #             system_prompt = POST_FORMATTER_PROMPT
    #         else:
    #             # Используем промпт для кнопок (B, I, таблицы и т.д.)
    #             system_prompt = system_instruction.content
    #
    #         # 2. Обращаемся к ИИ
    #         ai_response = model.invoke([
    #             SystemMessage(content=system_prompt),
    #             HumanMessage(content=f"Действие: {action}. Текст: {user_text}")
    #         ])
    #
    #         return JsonResponse({"result": ai_response.content})

    def get_success_url(self):
        # self.object.post — это связь с постом, к которому привязан коммент
        return reverse("blog:post_detail", kwargs={"pk": self.kwargs.get("post_pk")})

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        # Если медиа — это отдельный формсет:
        if self.request.POST:
            data["media_formset"] = CommentMediaFormSet(self.request.POST, self.request.FILES, instance=self.object)
        else:
            # ПЕРЕДАЕМ instance=self.object, чтобы увидеть старые картинки
            data["media_formset"] = CommentMediaFormSet(instance=self.object)
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        media_formset = context["media_formset"]

        with transaction.atomic():
            self.object = form.save()  # Автор и пост уже есть в базе, менять их не надо

            if media_formset.is_valid():
                media_formset.save()
            else:
                return self.form_invalid(form)

        return HttpResponseRedirect(self.get_success_url())


class CommentDeleteView(DeleteView):
    """Создание комментария к посту"""
    model = Comment
    form_class = CommentForm

    # def dispatch(self, request, *args, **kwargs):
    #     """Дебаг-метод для проверки подключения контроллера"""
    #     # Этот принт сработает ПЕРВЫМ при любом обращении к этому URL
    #     print(">>> СИГНАЛ ПОЛУЧЕН: Запрос вошел в CommentDeleteView")
    #     print(f">>> Данные пути (kwargs): {kwargs}")
    #     return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy("blog:post_delete", kwargs={"pk": self.object.post.pk})


class CategoriesDetailView(DetailView):
    """Тематика постов"""
    model = Categories
    template_name = 'blog/categories.html'
    context_object_name = 'categories'

    # def dispatch(self, request, *args, **kwargs):
    #     """Дебаг-метод для проверки подключения контроллера"""
    #     # Этот принт сработает ПЕРВЫМ при любом обращении к этому URL
    #     print(">>> СИГНАЛ ПОЛУЧЕН: Запрос вошел в CategoriesDetailView")
    #     print(f">>> Данные пути (kwargs): {kwargs}")
    #     return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Метод отвечает за подготовку данных, которые полетят в HTML-шаблон"""
        context = super().get_context_data(**kwargs)
        posts = Post.objects.filter(category=self.object)


        # Сюда можно добавить вашу логику фильтрации (newer/older)
        filter_type = self.request.GET.get("filter")
        if filter_type == "newer":
            posts = posts.order_by("-created_at")
        elif filter_type == "older":
            posts = posts.order_by("created_at")

        context["posts"] = posts
        context["page_name"] = "categories"
        context["categories_list"] = Categories.objects.all()
        return context

#
# class CategoryUpdateView(UpdateView):
#     """Обновление категорий"""
#     model = Categories
#     form_class = CategoriesForm
#     template_name = 'blog/category_form.html'
#     success_url = '/thanks/'


class FavoritesListView(ListView):
    """Избранные посты"""
    model = Post
    context_object_name = "fav_posts"

    # def dispatch(self, request, *args, **kwargs):
    #     """Дебаг-метод для проверки подключения контроллера"""
    #     # Этот принт сработает ПЕРВЫМ при любом обращении к этому URL
    #     print(">>> СИГНАЛ ПОЛУЧЕН: Запрос вошел в CategoriesListView")
    #     print(f">>> Данные пути (kwargs): {kwargs}")
    #     return super().dispatch(request, *args, **kwargs)

    def get_queryset(self, **kwargs):
        """Получение заполнения макета с фильтрацией"""
        # Заготовка на будущее пока что
        queryset = Post.objects.all()
        filter_type = self.request.GET.get("filter")

        if filter_type == "top":
            queryset = queryset.order_by(
                "-popularity"
            )  # Предполагается, что есть поле popularity
        elif filter_type == "newer":
            queryset = queryset.order_by(
                "-created_at"
            )
        elif filter_type == "older":
            queryset = queryset.order_by(
                "created_at"
            )

        return queryset

    def get_context_data(self, **kwargs):
        """Метод отвечает за подготовку данных, которые полетят в HTML-шаблон"""
        context = super().get_context_data(**kwargs)
        context["context_object_name"] = "fav_posts"
        return context


class SetPostMainView(UserPassesTestMixin, UpdateView):
    model = Post

    def get_success_url(self):
        return reverse("blog:post_detail", kwargs={"pk": self.object.post.pk})

    def test_func(self):
        # Проверяем: залогинен ли и есть ли статус модератора (или персонала)
        return self.request.user.is_staff






# # Сортировка по лайкам (от большего к меньшему)
# posts = Post.objects.all().order_by('-likes')
#
# # Сортировка по названию (А-Я)
# posts = Post.objects.all().order_by('title')
#
# # Сортировка по количеству просмотров
# posts = Post.objects.all().order_by('-viewed')
#
# планируем часто сортировать по viewed или likes, добавить в поле параметр db_index=True
#
# def post_list(request):
#     sort_by = request.GET.get('sort', '-created_at') # По умолчанию — новые
#     posts = Post.objects.all().order_by(sort_by)
#     return render(request, 'blog/list.html', {'posts': posts})
#
#
# def toggle_subscription(request, author_id):
#     author = User.objects.get(id=author_id)
#     subscriber = request.user  # Текущий залогиненный юзер
#
#     # Пытаемся найти подписку
#     subscription = Subscription.objects.filter(author=author, subscriber=subscriber)
#
#     if subscription.exists():
#         # ЕСЛИ ЕСТЬ — ОТПИСЫВАЕМ (удаляем запись)
#         subscription.delete()
#         message = "Вы отписались"
#     else:
#         # ЕСЛИ НЕТ — ПОДПИСЫВАЕМ (создаем запись)
#         Subscription.objects.create(author=author, subscriber=subscriber)
#         message = "Вы подписаны"
#
#     return JsonResponse({"status": "ok", "message": message})
