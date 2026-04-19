from django.contrib.auth.hashers import check_password
from users.models import Moderator, User


class ModeratorBackend:
    """Поиск в бд по таблице модераторов"""
    def authenticate(self, request, email=None, password=None, **kwargs):
        try:
            # Ищем именно в таблице модераторов
            moderator = Moderator.objects.get(email=email)
            # Проверяем хэш пароля
            if moderator.check_password(password):
                return moderator
        except Moderator.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            # Позволяет Django "узнавать" модератора при переходе по страницам
            return Moderator.objects.get(pk=user_id)
        except Moderator.DoesNotExist:
            return None


class UserBackend:
    """Поиск в бд по таблице пользователей"""
    def authenticate(self, request, email=None, password=None, **kwargs):
        try:
            # Ищем именно в таблице пользователя
            user = User.objects.get(email=email)
            # Проверяем хэш пароля
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            # Позволяет Django "узнавать" пользователя при переходе по страницам
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None