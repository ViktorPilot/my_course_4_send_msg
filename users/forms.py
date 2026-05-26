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
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ['email', 'password1', 'password2']

class UserAuthenticationForm(StyleMixin, AuthenticationForm):
    class Meta(AuthenticationForm):
        model = CustomUser
        fields = ['email', 'password']
