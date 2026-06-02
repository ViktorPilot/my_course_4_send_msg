from django.core.management import BaseCommand

from users.models import CustomUser


class Command(BaseCommand):
    """Класс создания кастомной команды"""

    def handle(self, *args: str, **options: dict) -> None:
        """Функция для создания нового суперюзера"""
        user = CustomUser.objects.create(email="vvvv@mail.ru")
        user.set_password("q12345")
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save()
