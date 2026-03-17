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
from blog.models import
from blog.forms import
from django.utils import timezone
from django.db import transaction
import os
from config import settings
from langchain_core.messages import SystemMessage, HumanMessage

# Create your views here.
"""Позволяет оборачивать текст в жирный, делать его ссылкой, создавать таблицу"""
# Вот сюда вставляете ваш текст
system_instruction = SystemMessage(content="""
Ты — помощник по оформлению контента. Твоя задача — возвращать текст в строгом HTML-формате. 
1. Жирный: <strong>. 
2. Ссылка: <a href="URL"> (если нет URL, ставь #). 
3. Таблица: <table><tr><td>...</td></tr></table>. 
Выдавай только чистый HTML без пояснений.
""")
# Пример запроса от кнопки "Жирный"
user_prompt = HumanMessage(content="Сделай жирным текст: 'Подписаться на новости'")
# Отправка модели (псевдокод)
# response = model.invoke([system_instruction, user_prompt])


class BaseTemplateView(TemplateView):
    """Контроллер позволяет считывать базовую страницу"""
    template_name = "base.html"


class CatalogRedirectView(RedirectView):
    """Перенаправляем пользователя на главную приложения catalog"""
    def get_redirect_url(self, *args, **kwargs):
        """"""
        print("Пользователь перешел в блог")
        return super().get_redirect_url(*args, **kwargs)

    pattern_name = "catalog:home"


class HomeListView(ListView):
    """Контроллер позволяет наполнять базовую страницу: продуктами"""

    model =
    page_name = "home"
    template_name = "blog/home.html"

    def get_queryset(self, **kwargs):
        """Получение заполнения макета с фильтрацией"""
        # Заготовка на будущее пока что
        queryset = .objects.all()
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
# Сортировка по лайкам (от большего к меньшему)
posts = Post.objects.all().order_by('-likes')

# Сортировка по названию (А-Я)
posts = Post.objects.all().order_by('title')

# Сортировка по количеству просмотров
posts = Post.objects.all().order_by('-viewed')

вы планируете часто сортировать по viewed или likes, добавьте в поле параметр db_index=True

def post_list(request):
    sort_by = request.GET.get('sort', '-created_at') # По умолчанию — новые
    posts = Post.objects.all().order_by(sort_by)
    return render(request, 'blog/list.html', {'posts': posts})


def toggle_subscription(request, author_id):
    author = User.objects.get(id=author_id)
    subscriber = request.user  # Текущий залогиненный юзер

    # Пытаемся найти подписку
    subscription = Subscription.objects.filter(author=author, subscriber=subscriber)

    if subscription.exists():
        # ЕСЛИ ЕСТЬ — ОТПИСЫВАЕМ (удаляем запись)
        subscription.delete()
        message = "Вы отписались"
    else:
        # ЕСЛИ НЕТ — ПОДПИСЫВАЕМ (создаем запись)
        Subscription.objects.create(author=author, subscriber=subscriber)
        message = "Вы подписаны"

    return JsonResponse({"status": "ok", "message": message})