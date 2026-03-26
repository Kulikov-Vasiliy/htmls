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

    def get_upload_path(instance, filename):
        """Определяет путь сохранения медиафайла"""
        category_id = instance.id if instance.id else "new"
        return f"catalogue/category_{category_id}/{filename}"

    image = models.ImageField(
        upload_to=get_upload_path,
        null=True,
        blank=True,
        verbose_name="Изображение категории",
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
    popularity = models.IntegerField(default=0)

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


class ProductMedia(models.Model):
    """Класс для работы с медиафайлами продукта"""

    # Связь "Многие к Одному": много медиа к одному продукту
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="media_list"
    )

    # Поле для определения типа контента
    CONTENT_TYPES = [("image", "Изображение"), ("video", "Видео")]
    file_type = models.CharField(max_length=10, choices=CONTENT_TYPES)

    def get_upload_path(instance, filename):
        """Определяет путь сохранения медиафайла"""
        return f"products/product_{instance.product.id}/{instance.file_type}/{filename}"

    image = models.ImageField(
        upload_to=get_upload_path,
        null=True,
        blank=True,
        verbose_name="Изображение продукта",
    )
    video = models.FileField(
        upload_to=get_upload_path,
        null=True,
        blank=True,
        verbose_name="Видео-презентация продукта",
    )

    def __str__(self):
        """Вывод в виде: тип файла для продукта такого-то"""
        return f"{self.file_type} для {self.product.name}"


class User(models.Model):
    """Класс пользователя, применяемый для фильтра отображения"""

    pass


class UserActivity(models.Model):
    """Класс фильтра отображения"""

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey("User", on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Активность"
        verbose_name_plural = "Активности"

    def __str__(self):
        """Вывод в человекочитаемом виде"""
        if self.user:
            return f"{self.user}"
        elif self.product:
            return f"{self.product.name}"
        return f"Активность пользователя {self.user} по товару {self.product.name}"
