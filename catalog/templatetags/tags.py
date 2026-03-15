from django import template

register = template.Library()


@register.filter()
def media_filter(path):
    """Регистратор подставляет путь к изображениям/видео"""
    if not path:
        return "#"
    elif str(path).startswith("/media/"):
        return path
    return f"/media/{path}"
