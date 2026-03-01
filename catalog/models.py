from django.db import models

# Create your models here.
class Category(models.Model):
    """
    Класс для работы с моделью категории и содержит:
    наименование,
    описание
    """

    name = models.CharField(max_length=100, verbose_name="Наименование категории")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")
    created_at = models.DateTimeField(
        blank=True, null=True, auto_now_add=True, verbose_name="Дата создания"
    )
    updated_at = models.DateTimeField(
        blank=True, null=True, auto_now=True, verbose_name="Дата последнего изменения"
    )

    class Meta:
        """Класс мета-параметров для класса категорий"""

        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ["name"]

    def __str__(self):
        """Вывод имени категории в человекочитаемом виде"""
        return self.name


class Product(models.Model):
    """
    Класс для работы с моделью продукта и содержит:
    наименование,
    описание,
    изображение,
    категория,
    цена за покупку,
    дата создания,
    дата последнего изменения
    """

    name = models.CharField(max_length=150, verbose_name="Наименование продукта")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")
    image = models.ImageField(
        upload_to="catalog/image",
        blank=True,
        null=True,
        verbose_name="Изображение продукта",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Категория",
        related_name="products",
    )
    price = models.DecimalField(
        blank=True,
        null=True,
        max_digits=10,
        decimal_places=2,
        verbose_name="Цена за покупку",
    )
    created_at = models.DateTimeField(
        blank=True, null=True, auto_now_add=True, verbose_name="Дата создания"
    )
    updated_at = models.DateTimeField(
        blank=True, null=True, auto_now=True, verbose_name="Дата последнего изменения"
    )

    class Meta:
        """Класс мета-параметров класса продукта"""

        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"
        ordering = ["category", "name"]

    def __str__(self):
        """Вывод имени / имени и категории в человекочитаемом виде"""
        if self.category:
            return f"{self.name} ({self.category})"
        return self.name
