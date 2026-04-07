from django import forms
from django.forms import inlineformset_factory
from blog.models import Post, PostMedia, Comment, Categories


PostMediaFormSet = inlineformset_factory(
    Post,
    PostMedia,
    fields=("image", "video", "preview"),
    extra=1,  # сколько пустых полей для загрузки показать сразу
    can_delete=True,
)


CommentMediaFormSet = inlineformset_factory(
    Post,
    PostMedia,
    fields=("image", "video",),
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
    confirm_delete = forms.ChoiceField(
        choices=[("YES", "Да, удалить"), ("NO", "Нет, оставить")],
        widget=forms.RadioSelect,
        label="Вы действительно хотите удалить пост?"
    )

    class Meta:
        model = Post
        fields = []


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
