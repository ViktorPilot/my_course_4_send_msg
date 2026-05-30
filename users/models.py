from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """Класс создания экземпляра пользователя"""

    username = None
    email = models.EmailField(verbose_name="email", unique=True)
    token = models.CharField(max_length=100, verbose_name="Token", blank=True, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        """Магический метод возвращает электронную почту пользователя"""
        return self.email
