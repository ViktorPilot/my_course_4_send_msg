import secrets

from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, reverse, render
from django.contrib.auth.models import Permission

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
                  recipient_list=[user.email], )
        return super().form_valid(form)


def email_verification(request, token):
    """Метод делает пользователя активным после подтверждения регистрации по электронной почте"""
    user = get_object_or_404(CustomUser, token=token)
    user.is_active = True
    add_permissions(user)
    user.save()
    return redirect(reverse('users:login'))

def add_permissions(user):
    """Метод добавляет права пользователю после регистрации"""
    add_clients_permission = Permission.objects.get(codename='add_clients')
    change_clients_permission = Permission.objects.get(codename='change_clients')
    delete_clients_permission = Permission.objects.get(codename='delete_clients')
    add_message_permission = Permission.objects.get(codename='add_message')
    change_message_permission = Permission.objects.get(codename='change_message')
    delete_message_permission = Permission.objects.get(codename='delete_message')
    add_distribution_permission = Permission.objects.get(codename='add_distribution')
    change_distribution_permission = Permission.objects.get(codename='change_distribution')
    delete_distribution_permission = Permission.objects.get(codename='delete_distribution')
    return user.user_permissions.add(add_clients_permission,
                              change_clients_permission,
                              delete_clients_permission,
                              add_message_permission,
                              change_message_permission,
                              delete_message_permission,
                              add_distribution_permission,
                              change_distribution_permission,
                              delete_distribution_permission, )

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

def get_users(requests):
    """Контроллер страницы списка пользователей"""
    users = CustomUser.objects.all()
    context = {'users':users,}
    return render(requests, 'users/list_users.html', context=context)

def users_block(requests, pk):
    """Контроллер для блокировки/разблокировки пользователя"""
    user = CustomUser.objects.get(pk=pk)
    if requests.method == 'POST':
        if user.is_active:
            user.is_active = False
        else:
            user.is_active = True
        user.save()
        return redirect('/users/list_users')
    else:
        context = {'user':user}
        return render(requests, 'users/users_block.html', context=context)













