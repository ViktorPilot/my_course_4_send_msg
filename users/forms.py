from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from users.models import CustomUser

class StyleMixin:
    """Миксин создающий экземпляр класса для стилизации web-страницы"""

    def __init__(self, *args, **kwargs) -> None:
        """Метод задает стиль web-страниц"""
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({"class": "form-control"})

class CustomCreationForm(StyleMixin, UserCreationForm):
    """Класс формы создания нового пользователя"""
    class Meta(UserCreationForm.Meta):
        """Метакласс формы создания нового пользователя"""
        model = CustomUser
        fields = ['email', 'password1', 'password2']

class UserAuthenticationForm(StyleMixin, AuthenticationForm):
    """Класс формы аутентификации пользователя"""
    class Meta(AuthenticationForm):
        """Метакласс формы аутентификации пользователя"""
        model = CustomUser
        fields = ['email', 'password']
