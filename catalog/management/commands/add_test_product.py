from django.core.management.base import BaseCommand
from catalog.models import Category, Product
from django.core.management import call_command
import os
from config import settings


class Command(BaseCommand):
    """Класс кастомной команды"""

    help = "Load test data from fixture"

    def handle(self, *args, **kwargs):
        """Удаление существующих данных и запись новых в бд"""

        # Удаляем существующие записи
        try:
            product_del = Product.objects.all().delete()
            category_del = Category.objects.all().delete()
            self.stdout.write(
                self.style.SUCCESS(f"Successfully deleted data in {product_del}")
            )
            self.stdout.write(
                self.style.SUCCESS(f"Successfully deleted data in {category_del}")
            )

        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f"Can not delete data. Cause: {str(e)}")
            )
        else:

            # Остальной код команды
            """
            # Выгружаем из готовой фикстуры
            fixture_path = os.path.join(
                settings.BASE_DIR, "catalog", "data", "catalog.json"
            )
            try:
                call_command("loaddata", fixture_path)
                self.stdout.write(
                    self.style.SUCCESS("Successfully loaded data from fixture")
                )
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f"Can not load data from fixture. Cause: {str(e)}")
                )"""

            # Альтернативно создаем
            category_1, _ = Category.objects.get_or_create(
                name="Категория 1",
                description="",
            )
            category_2, _ = Category.objects.get_or_create(
                name="Категория 2",
                description="",
            )

            products = [
                {
                    "name": "Продукт 1",
                    "description": "Описание 1",
                    "category": category_1,
                },
                {
                    "name": "Продукт 3",
                    "description": "Описание 3",
                    "category": category_1,
                },
                {
                    "name": "Продукт 2",
                    "description": "Описание 2",
                    "category": category_2,
                },
            ]

            for product in products:
                product, created = Product.objects.get_or_create(**product)
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Successfully added product: {product.name}"
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f"Product already exists: {product.name}")
                    )
