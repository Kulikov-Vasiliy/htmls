from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager


# Create your models here.
class MyUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email обязателен')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

def get_upload_path(instance, filename):
    """Определяет путь сохранения медиафайла"""
    profile_id = instance.id if instance.id else "new"
    return f"users/user_{profile_id}/{filename}"


class User(AbstractUser):
    """
    Модель пользователя:
    Ник - для отображения в блоге
    Логин - под каким именем будет вход в систему
    """
    username = None
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',  # Уникальное имя
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='users',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions_set',  # Уникальное имя
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )
    objects = MyUserManager()

    first_name = models.CharField(max_length=10, verbose_name="Имя")
    last_name = models.CharField(max_length=20, verbose_name="Фамилия")
    email = models.EmailField(unique=True, verbose_name="Электронная почта")
    phone_number = models.CharField(max_length=11, unique=True, verbose_name="Телефон", blank=True, null=True)
    country = models.CharField(max_length=10, verbose_name="Страна")
    nickname = models.CharField(max_length=10, unique=True, verbose_name="Ник")
    about = models.CharField(max_length=1000, null=True, blank=True, verbose_name="О себе")
    login = models.CharField(max_length=10, unique=True, verbose_name="Логин")
    joined_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    DELETION = [("DELETE", "удалить"), ("CANCEL", "не удалять")]
    is_delete = models.CharField(max_length=10, default="CANCEL", choices=DELETION)
    is_deleted = models.BooleanField(default=False, verbose_name="Удален")
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name="Дата и время удаления")

    avatar = models.ImageField(
        upload_to=get_upload_path,
        null=True,
        blank=True,
        verbose_name="Изображение профиля",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    token = models.CharField(max_length=50, blank=True, null=True, verbose_name="Token")

    def delete(self, *args, **kwargs):
        """Мягкое удаление"""
        # Удаляем файл с диска
        self.is_deleted = True
        self.deleted_at = timezone.now()

        # Физическое удаление фото, чтобы не занимало место:
        if self.avatar:
            self.avatar.delete(save=False)

        # Сохраняем изменения в базе
        self.save()

    def __str__(self):
        """Вывод Ника категории в человекочитаемом виде"""
        if self.phone_number:
            return f"{self.phone_number}"
        elif self.email:
            return f"{self.email}"
        else:
            return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"
        ordering = ["nickname", "joined_at", "country", "first_name", "last_name"]


class UserActivity(models.Model):
    """Класс фильтра отображения"""

    post = models.ForeignKey('blog.Post', on_delete=models.CASCADE)
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
        related_name='subscriptions_list',
        verbose_name="Подписчик"
    )
    SUBSCRIBE = [("subscribe", "Подписаться"), ("unsubscribe", "Отписаться")]
    is_subscribe = models.CharField(max_length=12, default="unsubscribe", choices=SUBSCRIBE)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Подписался")
    unsubscribe = models.DateTimeField(verbose_name="Отписался")

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        # Запрещаем повторную подписку на того же человека
        unique_together = ('author', 'subscriber')

    def __str__(self):
        """"Вывод в человекочитаемом виде"""
        return f"{self.subscriber.nickname} подписан на {self.author.nickname}"


def get_upload_path_moder(instance, filename):
    """Определяет путь сохранения медиафайла"""
    moder_id = instance.id if instance.id else "new"
    return f"users/moderator_{moder_id}/{filename}"


class Moderator(AbstractUser):
    """
    Модель модератора
    """
    username = None
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_moderators_set',  # Уникальное имя
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='moderators',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_moderator_permissions_set',  # Уникальное имя
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='moderator permissions',
    )
    objects = MyUserManager()  # Используем тот же менеджер

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    first_name = models.CharField(max_length=10, verbose_name="Имя")
    last_name = models.CharField(max_length=20, verbose_name="Фамилия")
    email = models.EmailField(unique=True, verbose_name="Электронная почта")
    phone_number = models.CharField(max_length=11, unique=True, verbose_name="Телефон", blank=True, null=True)
    country = models.CharField(max_length=10, verbose_name="Страна")
    login = models.CharField(max_length=10, unique=True, verbose_name="Логин")
    joined_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    DELETION = [("DELETE", "удалить"), ("CANCEL", "не удалять")]
    is_delete = models.CharField(max_length=10, default="CANCEL", choices=DELETION)
    is_deleted = models.BooleanField(default=False, verbose_name="Удален")
    deleted_at = models.DateTimeField(blank=True, null=True, verbose_name="Дата и время удаления")
    post = models.ForeignKey('blog.Post', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Пост")
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Автор поста",
        related_name="moderated_posts_authored"
    )
    message = models.TextField(blank=True, null=True, verbose_name="Текст сообщения от модератора")
    avatar = models.ImageField(
        upload_to=get_upload_path_moder,
        null=True,
        blank=True,
        verbose_name="Фото модератора",
    )
    decision_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="moderator_decisions")
    is_active = models.BooleanField(default=True, verbose_name="Одобрить")
    is_staff  = models.BooleanField(default=False,
        verbose_name="Статус модератора")

    def delete(self, *args, **kwargs):
        """Мягкое удаление"""
        # Удаляем файл с диска
        self.is_deleted = True
        self.deleted_at = timezone.now()

        # Физическое удаление фото, чтобы не занимало место:
        if self.avatar:
            self.avatar.delete(save=False)

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
