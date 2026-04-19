from django.utils import timezone
from django.db import models
from django.urls import reverse

from config import settings
from users.models import User


# Create your models here.
class Categories(models.Model):
    """Модель категорий (обозначены как теги)"""
    CONTENT_TYPES = [
        ("World", "Мировые"),
        ("Russia", "Россия"),
        ("Technology", "Технологии"),
        ("Design", "Дизайн"),
        ("Culture", "Культура"),
        ("Business", "Бизнес"),
        ("Politics", "Политика"),
        ("Opinion", "Мнение"),
        ("Science", "Наука"),
        ("Health", "Здоровье"),
        ("Style", "Стиль"),
        ("Travel", "Путешествия"),
    ]
    tag = models.CharField(max_length=20, choices=CONTENT_TYPES)
    name = models.CharField(max_length=50, unique=True, verbose_name="Название")
    slug = models.SlugField(max_length=60, unique=True, verbose_name="URL-адрес")
    description = models.TextField(blank=True, verbose_name="Описание")
    icon = models.CharField(max_length=10, blank=True, verbose_name="Эмодзи-иконка")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок сортировки")

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ['order', 'name']

    def __str__(self):
        """Вывод категории в человекочитаемом виде"""
        return f"{self.icon} {self.name}"


class Post(models.Model):
    """
    заголовок,
    содержимое,
    превью (изображение),
    дата создания,
    признак публикации (булевое поле),
    количество просмотров.
    """
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        verbose_name="Автор",
        related_name="посты",
    )
    title = models.CharField(max_length=200, verbose_name="Заголовок поста")
    content = models.TextField(blank=True, null=True, verbose_name="Cодержание")
    about_content = models.TextField(max_length=300, blank=True, null=True, verbose_name="Кратко о содержании")
    viewed = models.PositiveIntegerField(default=0, verbose_name="Счетчик просмотров")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    PUBLICATION_NOW_LATER = [("YES", "Опубликовать"), ("NO", "Позже")]
    publish_status = models.CharField(
        max_length=12,
        choices=PUBLICATION_NOW_LATER,
        default="NO",
        verbose_name="Опубликовать сразу"
    )

    scheduled_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Когда опубликовать?"
    )
    published_at = models.DateField(blank=True, null=True, verbose_name="Дата публикации")
    updated_at = models.DateTimeField(blank=True, null=True, auto_now=True, verbose_name="Дата последнего изменения")
    is_published = models.BooleanField(default=False, verbose_name="Опубликовано")
    popularity = models.IntegerField(default=0, verbose_name="Популярность")
    tag = models.ForeignKey(Categories, on_delete=models.SET_NULL, null=True)
    DELETION = [("YES", "Удалить"), ("NO", "Отменить")]
    is_deleted = models.BooleanField(default=False, verbose_name="Удален")
    likes = models.PositiveIntegerField(default=0, verbose_name="Счетчик лайков")
    dislikes = models.PositiveIntegerField(default=0, verbose_name="Счетчик дизлайков")
    favorites = models.ManyToManyField(
        User,
        related_name='favorite_posts',
        blank=True,
        verbose_name="В избранном у пользователей"
    )
    is_active = models.BooleanField(default=True, verbose_name="Активен")  # Для модерации: одобрять или нет
    is_formatted = models.BooleanField(default=False)  # чтобы модератор видел,
    # использовал ли пользователь наши кнопки (Bold, Link, Table)

    class Meta:
        """"Класс мета-параметров"""

        verbose_name = "Пост"
        verbose_name_plural = "Посты"
        ordering = [
            "-created_at",
            "title",
            "author",
            "tag"
        ]

    def __str__(self):
        """"Вывод заголовка, автора и категории в человекочитаемом виде"""
        return f"Заголовок: {self.title} (тема: {self.tag}, автор:{self.author})"

    def get_absolute_url(self):
        """Определяет абсолютный путь при создании поста"""
        return reverse('blog:post_detail', kwargs={'pk': self.pk})


def get_upload_path_pm(instance, filename):
    """Путь к медиа"""
    nickname = instance.post.author.nickname if instance.post.author else "anonymous"
    # Определяем подпапку по расширению или наличию данных в полях
    if filename.endswith(('.mp4', '.avi', '.mov')):
        subfolder = 'video'
    else:
        subfolder = 'images'
    return f"blog/user_{nickname}/post_{instance.post.id}/{subfolder}/{filename}"


class PostMedia(models.Model):
    """Класс для работы с медиафайлами поста"""

    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="media_list"
    )

    image = models.ImageField(
        upload_to=get_upload_path_pm,
        null=True,
        blank=True,
        verbose_name="Изображение поста",
    )
    preview = models.ImageField(
        upload_to=get_upload_path_pm,
        null=True,
        blank=True,
        verbose_name="Превью поста",
    )
    video = models.FileField(
        upload_to=get_upload_path_pm,
        null=True,
        blank=True,
        verbose_name="Видео поста",
    )

    class Meta:
        verbose_name = "Медиа поста"
        verbose_name_plural = "Медиа постов"


def get_comment_media_path(instance, filename):
    """Определяем путь к медиа комментария"""
    return f"blog/comments/post_{instance.post.id}/user_{instance.author.id}/{filename}"


class Comment(models.Model):
    """Модель комментария"""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    icon = models.CharField(max_length=10, blank=True, verbose_name="Эмодзи-иконка")
    text = models.TextField(max_length=1000, verbose_name="Комментарий")
    slug = models.SlugField(max_length=60, verbose_name="URL-адрес")

    # Поле для медиа (опционально)
    image = models.ImageField(
        upload_to=get_comment_media_path,
        null=True,
        blank=True,
        verbose_name="Изображение к комментарию"
    )
    video = models.FileField(
        upload_to=get_comment_media_path,
        null=True,
        blank=True,
        verbose_name="Видео к комментарию"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата написания")
    is_active = models.BooleanField(default=True, verbose_name="Активен")  # Для модерации
    is_formatted = models.BooleanField(default=False)  # чтобы модератор видел,
    # использовал ли пользователь наши кнопки (Bold, Link, Table)

    class Meta:
        """Метакласс для комментариев"""
        ordering = ['-created_at']  # Сначала новые
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"

    def __str__(self):
        """Вывод в человекочитаемом виде"""
        return f"{self.author.nickname} к посту {self.post.id}"
