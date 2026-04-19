from django import forms
from users.models import User, UserActivity, Subscription, Moderator

# from django.contrib.auth.forms import UserCreationForm


class SignInForm(forms.Form):
    """Форма входа"""
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class UserCreationForm(forms.ModelForm):
    """Форма создания пользователя"""
    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "country",
            "nickname",
            "login",
            "password",
        )

class UserUpdateForm(forms.ModelForm):
    """Форма создания пользователя"""
    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "country",
            "nickname",
            "login",
            "avatar",
            "about",
            "password",
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
            "first_name", "last_name", "email", "phone_number", "country", "nickname",
            "login", "about", "avatar", "is_delete", "is_deleted"
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Список полей, которые модератор МОЖЕТ видеть, но НЕ МОЖЕТ менять
        readonly_fields = [
            "first_name", "last_name", "email", "phone_number", "country", "is_deleted",
            "nickname", "login", "about", "avatar"
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
            "phone_number",
            "country",
            "login",
            "avatar",
            "password"
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
            "phone_number",
            "country",
            "avatar",
            "password",
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
