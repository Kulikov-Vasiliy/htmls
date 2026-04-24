from django.db import migrations

def create_groups(apps, schema_editor):
    # Получаем модели через apps, чтобы не зависеть от импортов
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")

    # 1. Создаем группу Модераторов
    moderator_group, created = Group.objects.get_or_create(name="Moderator")

    # 2. Находим нужные права (например, право менять продукт)
    can_publish_product = Permission.objects.get(codename="can publish product"),
    can_unpublish_product  = Permission.objects.get(codename="can unpublish product")
    can_delete_product  = Permission.objects.get(codename="can delete product")
    can_view_product  = Permission.objects.get(codename="can view product")

    # 3. Добавляем права группе
    moderator_group.permissions.add(
        can_publish_product,
        can_delete_product,
        can_view_product,
        can_unpublish_product
    )


def remove_groups(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Group.objects.filter(name="Moderator").delete()