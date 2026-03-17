import django.contrib.auth.models.AbstractUser
from django.utils import timezone
from django.db import models
from pyexpat.errors import messages


# Create your models here.
def get_upload_path(instance, filename):
    """Определяет путь сохранения медиафайла"""
    profile_id = instance.id if instance.id else "new"
    return f"blog/user_{profile_id}/{filename}"


class User(models.Model):
    """
    Модель пользователя:
    Ник - для отображения в блоге
    Логин - под каким именем будет вход в систему
    """
    first_name = models.CharField(max_length=10, verbose_name="Имя")
    last_name = models.CharField(max_length=20, verbose_name="Фамилия")
    email = models.EmailField(unique=True, verbose_name="Электронная почта")
    nickname = models.CharField(max_length=10, unique=True, verbose_name="Ник")
    about = models.CharField(max_length=1000, unique=True, verbose_name="О себе")
    login = models.CharField(max_length=10, unique=True, verbose_name="Логин")
    joined_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    DELETION = [("DELETE", "удалить"), ("CANCEL", "не удалять")]
    is_delete = models.CharField(max_length= 10, default="CANCEL", choices=DELETION)
    is_deleted = models.BooleanField(default=False, verbose_name="Удален")
    deleted_at = models.DateTimeField(verbose_name="Дата и время удаления")

    profile_img = models.ImageField(
        upload_to=get_upload_path,
        null=True,
        blank=True,
        verbose_name="Изображение профиля",
    )

    def delete(self, *args, **kwargs):
        """Мягкое удаление"""
        # Удаляем файл с диска
        self.is_deleted = True
        self.deleted_at = timezone.now()

        # Физическое удаление фото, чтобы не занимало место:
        if self.profile_img:
            self.profile_img.delete(save=False)

        # Сохраняем изменения в базе
        self.save()

    def __str__(self):
        """Вывод Ника категории в человекочитаемом виде"""
        if self.nickname:
            return f"{self.nickname}"
        elif self.login:
            return f"{self.login}"
        elif self.email:
            return f"{self.email}"
        elif self.first_name:
            return f"{self.first_name}"
        elif self.last_name:
            return f"{self.last_name}"

    class Meta:
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"
        ordering = ["nickname", "joined_at", "login", "first_name", "last_name"]


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
        User,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name="Категория",
        related_name="посты",
    )
    title = models.CharField(max_length=200, verbose_name="Название поста")
    content = models.TextField(blank=True, null=True, verbose_name="Cодержание")
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
    published_at = models.DateField(auto_now_add=True, verbose_name="Дата публикации")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата последнего изменения")
    is_published = models.BooleanField(default=False, verbose_name="Опубликовано")
    popularity = models.IntegerField(default=0,  verbose_name="Популярность")
    category = models.ForeignKey(Categories, on_delete=models.SET_NULL, null=True)

    is_deleted = models.BooleanField(default=False, verbose_name="Удален")
    likes = models.PositiveIntegerField(default=0, verbose_name="Счетчик лайков")
    dislikes = models.PositiveIntegerField(default=0, verbose_name="Счетчик дизлайков")
    favorites = models.ManyToManyField(
        User.nickname,
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
            "title",
            "author",
            "-created_at",
        ]

    def __str__(self):
        """"Вывод заголовка, автора и категории в человекочитаемом виде"""
        return f"title: {self.title} (thematics: {self.tags}, publisher:{self.author})"


class PostMedia(models.Model):
    """Класс для работы с медиафайлами поста"""

    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="media_list"
    )

    # Поле для определения типа контента
    CONTENT_TYPES = [("image", "Изображение"),("preview", "Превью"), ("video", "Видео")]
    file_type = models.CharField(max_length=10, choices=CONTENT_TYPES)

    def get_upload_path(instance, filename):
        """Определяет путь сохранения медиафайла"""
        if instance.post.author.nickname:
            return f"blog/user_{instance.user.nickname}/post_{instance.post.id}/{instance.file_type}/{filename}"

    image = models.ImageField(
        upload_to=get_upload_path,
        null=True,
        blank=True,
        verbose_name="Изображение поста",
    )
    preview = models.ImageField(
        upload_to=get_upload_path,
        null=True,
        blank=True,
        verbose_name="Превью поста",
    )
    video = models.FileField(
        upload_to=get_upload_path,
        null=True,
        blank=True,
        verbose_name="Видео-презентация продукта",
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
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    icon = models.CharField(max_length=10, blank=True, verbose_name="Эмодзи-иконка")
    text = models.TextField(max_length=1000, verbose_name="Комментарий")
    slug = models.SlugField(max_length=60, unique=True, verbose_name="URL-адрес")

    # Поле для медиа (опционально)
    image = models.ImageField(
        upload_to=get_comment_media_path,
        null=True,
        blank=True,
        verbose_name="Изображение к комментарию"
    )
    video = models.FileField( upload_to=get_comment_media_path,
        null=True,
        blank=True,
        verbose_name="Видео к комментарию"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата написания")
    is_active = models.BooleanField(default=True, verbose_name="Активен")  # Для модерации
    is_formatted = models.BooleanField(default=False) # чтобы модератор видел,
    # использовал ли пользователь наши кнопки (Bold, Link, Table)

    class Meta:
        """Метакласс для комментариев"""
        ordering = ['-created_at']  # Сначала новые
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"

    def __str__(self):
        """Вывод в человекочитаемом виде"""
        return f"{self.author.nickname} к посту {self.post.id}"


class UserActivity(models.Model):
    """Класс фильтра отображения"""

    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ['user', 'post']
        verbose_name = "Активность"
        verbose_name_plural = "Активности"

    def __str__(self):
        """"Вывод в человекочитаемом виде"""
        return f"Активность пользователя {self.user.nickname} в посте {self.post.id}"


class Subscription(models.Model):
    """Подписки пользователей"""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribers_list',
        verbose_name="Автор"
    )
    subscriber = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name = 'subscriptions_list',
        verbose_name = "Подписчик"
    )
    SUBSCRIBE = [("subscribe", "Подписаться"),("unsubscribe", "Отписаться")]
    is_subscribe = models.CharField(max_length=12, default="unsubscribe", choices=SUBSCRIBE)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Подписался")
    unsubscribed_at = models.DateTimeField(auto_now_add=True, verbose_name="Отписался")

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        # Запрещаем повторную подписку на того же человека
        unique_together = ('author', 'subscriber')

    def __str__(self):
        """"Вывод в человекочитаемом виде"""
        return f"{self.subscriber.nickname} подписан на {self.author.nickname}"


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
    tags = models.CharField(max_length=20, choices=CONTENT_TYPES)
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


def get_upload_path_moder(instance, filename):
    """Определяет путь сохранения медиафайла"""
    moder_id = instance.id if instance.id else "new"
    return f"blog/moderator_{moder_id}/{filename}"


class Moderator(models.Model):
    """
    Модель модератора
    """
    first_name = models.CharField(max_length=10, verbose_name="Имя")
    last_name = models.CharField(max_length=20, verbose_name="Фамилия")
    email = models.EmailField(unique=True, verbose_name="Электронная почта")
    login = models.CharField(max_length=10, unique=True, verbose_name="Логин")
    joined_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    DELETION = [("DELETE", "удалить"), ("CANCEL", "не удалять")]
    is_delete = models.CharField(max_length= 10, default="CANCEL", choices=DELETION)
    is_deleted = models.BooleanField(default=False, verbose_name="Удален")
    deleted_at = models.DateTimeField(verbose_name="Дата и время удаления")
    post = models.ForeignKey(Post, on_delete=models.SET_NULL, null=True, verbose_name="Пост")
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Автор поста")
    message = models.TextField(blank=True, null=True, verbose_name="Текст сообщения от модератора")
    profile_img = models.ImageField(
        upload_to=get_upload_path_moder,
        null=True,
        blank=True,
        verbose_name="Фото модератора",
    )
    decision_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def delete(self, *args, **kwargs):
        """Мягкое удаление"""
        # Удаляем файл с диска
        self.is_deleted = True
        self.deleted_at = timezone.now()

        # Физическое удаление фото, чтобы не занимало место:
        if self.profile_img:
            self.profile_img.delete(save=False)

        # Сохраняем изменения в базе
        self.save()

    def __str__(self):
        """Вывод в человекочитаемом виде"""
        if self.login:
            return f"{self.login}"
        elif self.email:
            return f"{self.email}"
        else:
            return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = "Профиль модератора"
        verbose_name_plural = "Профили модераторов"
        ordering = ["joined_at", "login", "first_name", "last_name", "deleted_at", "-message"]
