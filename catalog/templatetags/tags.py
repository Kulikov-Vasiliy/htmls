from django import template

register = template.Library()

@register.filter()
def media_filter(path):
    """Регистратор подставляет путь к изображениям/видео"""
    if path:
        return f"/media/{path}"
    return "#"