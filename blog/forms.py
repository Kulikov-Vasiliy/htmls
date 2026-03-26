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


CommentMediaFormSet = inlineformset_factory(
    Post,
    PostMedia,
    fields=("file_type", "image", "video",),
    extra=1,  # сколько пустых полей для загрузки показать сразу
    can_delete=True,
)


class PostBaseForm(forms.ModelForm):
    """Базовая форма с общими полями и виджетами"""

    class Meta:
        model = Post
        # Указываем только те поля, которые автор заполняет руками
        fields = ("title", "tag", "about_content", "content", "publish_status", "scheduled_at",)
        widgets = {
            # Добавляем класс для кнопок (Bold, Ссылка, Таблица)
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
        fields = PostBaseForm.Meta.fields + ("is_delete",)


class PostForm(forms.ModelForm):
    """Общая форма поста"""

    class Meta:
        model = Post
        fields = (
            "title",
            "tag",
            "about_content",
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
        )

class UserUpdateForm(forms.ModelForm):
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
            "about",
            "profile_img"
        )


class UserDeletionForm(forms.ModelForm):
    """Форма удаления пользователя"""
    class Meta:
        model = User
        fields = ("is_delete",)


class UserControlForm(forms.ModelForm):
    """Базовая форма пользователя для действий модераторов"""

    class Meta:
        model = User
        fields = (
            "first_name", "last_name", "email", "nickname",
            "login", "about", "profile_img", "is_delete", "is_deleted"
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Список полей, которые модератор МОЖЕТ видеть, но НЕ МОЖЕТ менять
        readonly_fields = [
            "first_name", "last_name", "email", "is_deleted",
            "nickname", "login", "about", "profile_img"
        ]

        for field in readonly_fields:
            if field in self.fields:
                self.fields[field].widget.attrs['readonly'] = True
                # Дополнительно можно добавить класс для стилизации серым цветом
                self.fields[field].widget.attrs['class'] = 'form-control-plaintext'


class ModeratorBaseForm(forms.ModelForm):
    """Базовая форма модератора"""
    class Meta:
        model = Moderator
        fields = (
            "first_name",
            "last_name",
            "email",
            "login",
            "profile_img"
        )


class ModeratorCreationForm(forms.ModelForm):
    """Форма создания модератора"""
    class Meta:
        model = Moderator
        fields = ModeratorBaseForm.Meta.fields + ("is_staff",)

    def save(self, commit=True):
        # 1. Получаем объект, но не сохраняем в БД сразу
        user = super().save(commit=False)

        # 2. Принудительно ставим статус персонала
        user.is_staff = True

        # 3. Если нужно, чтобы он мог заходить в админку,
        # можно добавить и user.is_active = True

        if commit:
            user.save()
        return user


class ModeratorUpdateForm(forms.ModelForm):
    """Форма обновления модератора"""
    class Meta:
        model = Moderator
        fields = (
            "first_name",
            "last_name",
            "email",
            "profile_img",
        )


class ModeratorDeletionForm(forms.ModelForm):
    """Форма удаления модератора"""
    class Meta:
        model = Moderator
        fields = ModeratorBaseForm.Meta.fields + ("is_delete",)


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
