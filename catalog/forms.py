from django import forms
from django.forms import inlineformset_factory
from catalog.models import Product, ProductMedia, Category

ProductMediaFormSet = inlineformset_factory(
    Product,
    ProductMedia,
    fields=("file_type", "image", "video"),
    extra=1,  # сколько пустых полей для загрузки показать сразу
    can_delete=True,
)


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ("name", "description", "image")
        extra = (1,)  # Показать одно пустое поле
        max_num = (1,)  # Запретить добавлять больше одного

        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "image": forms.FileInput(
                attrs={"class": "form-control"}
            ),  # Это принудительно создаст кнопку
        }


class ContactsForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    message = forms.CharField(widget=forms.Textarea)
