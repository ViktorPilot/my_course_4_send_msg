import secrets

from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, reverse, render

from config.settings import EMAIL_HOST_USER
from users.forms import CustomCreationForm, UserAuthenticationForm
from users.models import CustomUser


class RegisterView(CreateView):
    """Класс контроллера создания нового пользователя"""
    model = CustomUser
    form_class = CustomCreationForm
    success_url = reverse_lazy('users:success_register')

    def form_valid(self, form):
        """Метод отправляет на электронную почту пользователя письмо с токеном для подтверждения регистрации"""
        user = form.save()
        user.is_active = False
        token = secrets.token_hex(16)
        user.token = token
        user.save()
        host = self.request.get_host()
        url = f'http://{host}/users/email_confirm/{token}/'
        send_mail(subject='Подтверждение регистрации',
                  message=f'Для подтверждения регистрации перейдите по ссылке: {url}',
                  from_email=EMAIL_HOST_USER,
                  recipient_list=[user.email],)
        return super().form_valid(form)

def email_verification(request, token):
    """Метод делает пользователя активным после подтверждения регистрации по электронной почте"""
    user = get_object_or_404(CustomUser, token=token)
    user.is_active = True
    user.save()
    return redirect(reverse('users:login'))

class CustomLoginView(LoginView):
    """Класс контроллера входа пользователя в аккаунт"""
    model = CustomUser
    form_class = UserAuthenticationForm
    template_name = 'users/login.html'


class CustomLogoutView(LogoutView):
    """Класс контроллера выхода пользователя из аккаунта"""
    model = CustomUser

def success_register(request):
    """Представление, рендерирующее страницу успешной регистрации пользователя"""
    return render(request, 'users/success_register.html')
