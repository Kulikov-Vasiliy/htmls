from django import forms
from django.forms import inlineformset_factory, ModelForm, BooleanField
from catalog.models import Product, ProductMedia, Category
from django.core.exceptions import ValidationError


ProductMediaFormSet = inlineformset_factory(
    Product,
    ProductMedia,
    fields=("file_type", "image", "video"),
    extra=1,  # сколько пустых полей для загрузки показать сразу
    can_delete=True,
)


EXCLUSION_LIST = [
    "казино",
    "дешево",
    "радар",
    "криптовалюта",
    "бесплатно",
    "безплатно",
    "биржа",
    "крипта",
    "обман",
    "полиция",
]


class StyleFormMixin:
    """Общая стилизация форм"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field, BooleanField):
                field.widget.attrs["class"] = "form-check-input"
            else:
                field.widget.attrs["class"] = "form-class"



class CategoryForm(forms.ModelForm):
    """Задает поля при создании категорий"""
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
    """Задает поля контактов"""
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    message = forms.CharField(widget=forms.Textarea)


class ProductValidationForm(StyleFormMixin, ModelForm):
    """Запрещенные слова, которые нельзя использовать в названиях и описаниях продуктов:
    * казино           * дешево       * радар
    * криптовалюта     * бесплатно    * биржа
    * крипта           * обман        * полиция
    """

    class Meta:
        model = Product
        fields = ("name", "description", "price", "category")
        exclude = ("popularity",)

    def clean(self):
        """Очищает описание и название продукта от запрещенки"""
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        description = cleaned_data.get('description')
        for el in EXCLUSION_LIST:
            if el.lower() in name.lower():
                self.add_error("name", f"Название не может содержать слово {el}")
            elif el.lower() in description.lower():
                self.add_error("description", f"Описание не может содержать слово {el}")

        return cleaned_data

    def clean_price(self):
        """Проверять, что цена продукта не может быть отрицательной.
        Если цена введена неправильно, отобразите соответствующее сообщение пользователю
        """
        price = self.cleaned_data.get('price')
        if price and price is None or int(price) <= 0:
            raise ValidationError('Цена должна быть больше 0')
        return price
