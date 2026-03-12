from django import forms
from django.forms import inlineformset_factory
from catalog.models import Product, ProductMedia


ProductMediaFormSet = inlineformset_factory(
    Product, ProductMedia,
    fields=('file_type', 'image', 'video'),
    extra=1, # сколько пустых полей для загрузки показать сразу
    can_delete=True
)