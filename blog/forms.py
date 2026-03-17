from django import forms
from django.forms import inlineformset_factory
from blog.models import User, Post, PostMedia, Comment, UserActivity, Subscription, Categories, Moderator

PostMediaFormSet = inlineformset_factory(
    Post,
    PostMedia,
    fields=("file_type", "image", "video", "preview"),
    extra=1,  # сколько пустых полей для загрузки показать сразу
    can_delete=True,
)


class PostBaseForm(forms.ModelForm):
    """Базовая форма с общими полями и виджетами"""

    class Meta:
        model = Post
        # Указываем только те поля, которые юзер заполняет руками
        fields = ("title", "tags", "content", "publish_status", "scheduled_at", "preview")
        widgets = {
            # Добавляем класс для ваших кнопок (Bold, Ссылка, Таблица)
            'content': forms.Textarea(attrs={'class': 'editor-area', 'placeholder': 'Начните писать...'}),
            'scheduled_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


class PostCreationForm(PostBaseForm):
    """Форма создания поста"""
    pass


class PostUpdateForm(PostBaseForm):
    """Форма создания поста"""

    class Meta(PostBaseForm.Meta):
        fields = PostBaseForm.Meta.fields + ("is_published",)


class PostDeletionForm(forms.ModelForm):
    """Форма удаления поста"""

    class Meta:
        model = Post
        fields = ("is_deleted",)


class PostForm(forms.ModelForm):
    """Общая форма поста"""

    class Meta:
        model = Post
        fields = (
            "title",
            "tags",
            "content",
            "author",
            "is_published",
            "publish_status",
            "scheduled_at",
        )


class UserCreationForm(forms.ModelForm):
    """Форма создания пользователя"""
    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
            "nickname",
            "login",
            "profile_img",
            "about"
        )


class UserDeletionForm(forms.ModelForm):
    """Форма удаления пользователя"""
    class Meta:
        model = User
        fields = ("is_deleted",)


class UserSubscriptionForm(forms.ModelForm):
    """Форма подписок пользователя"""

    class Meta:
        model = Subscription
        fields = (
            "author",
            "subscriber",
            "is_subscribe",
        )


class UserActivityForm(forms.ModelForm):
    """Форма активности пользователя"""

    class Meta:
        model = UserActivity
        fields = ("post",)


class CommentForm(forms.ModelForm):
    """Форма комментария"""
    class Meta:
        model = Comment
        fields = (
            "icon",
            "text",
            "slug",
            "image",
            "video",
        )


class CommentModerationControlForm(forms.ModelForm):
    """Для одобрения модератором"""
    class Meta:
       model = Moderator
       fields = ("is_active", "message")
       widgets = {
           # Ваша кнопка «Жирный» здесь тоже пригодится для текста причины!
           'message': forms.Textarea(attrs={'class': 'editor-area', 'placeholder': 'Причина решения...'}),
       }


class PostModeratedControlForm(forms.ModelForm):
    """Для оспаривания модерации"""
    class Meta:
       model = Moderator
       fields = ("is_active", "message")
       widgets = {
           # Ваша кнопка «Жирный» здесь тоже пригодится для текста причины!
           'message': forms.Textarea(attrs={'class': 'editor-area', 'placeholder': 'Причина решения...'}),
       }


class CategoriesForm(forms.ModelForm):
    """Форма категорий(тегов)"""

    class Meta:
        model = Categories
        fields = ("name", "slug", "description", "icon", "order")
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Например: Технологии'}),
            'slug': forms.TextInput(attrs={'placeholder': 'technology'}),
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'О чем эта категория...'}),
            'icon': forms.TextInput(attrs={'placeholder': '🚀'}),
        }
