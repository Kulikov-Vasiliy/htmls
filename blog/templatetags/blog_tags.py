from django import template
from django.utils import timezone
from blog.models import Categories


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


@register.filter
def is_last_months(value):
    if not value: return False
    now = timezone.now()
    # Если год меньше текущего ИЛИ год тот же, но месяц меньше
    return value.year < now.year or (value.year == now.year and value.month < now.month)


@register.inclusion_tag('blog/includes/top_nav_items.html')
def render_top_nav():
    # Получаем все категории из базы, чтобы построить кнопки
    categories = Categories.objects.all().order_by('order') # сортировка по вашему полю order
    return {'categories_list': categories}


# @register.inclusion_tag('blog/includes/top_nav.html')
# def show_categories():
#     categories = Categories.objects.all()
#     return {'categories': categories}