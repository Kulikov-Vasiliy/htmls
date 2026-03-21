from django import template
from django.utils import timezone


register = template.Library()


@register.filter()
def media_filter(path):
    """Регистратор подставляет путь к изображениям/видео"""
    if not path:
        return "#"
    elif str(path).startswith("/media/"):
        return path
    return f"/media/{path}"


@register.filter
def is_current_month(value):
    if not value:
        return False
    now = timezone.now()
    return value.year == now.year and value.month == now.month and value.day == now.day
