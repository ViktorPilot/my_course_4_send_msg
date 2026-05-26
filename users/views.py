from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView

from users.forms import CustomCreationForm, UserAuthenticationForm
from users.models import CustomUser


class RegisterView(CreateView):
    model = CustomUser
    form_class = CustomCreationForm
    success_url = reverse_lazy('users:login')

class CustomLoginView(LoginView):
    model = CustomUser
    form_class = UserAuthenticationForm
    template_name = 'users/login.html'

class CustomLogoutView(LogoutView):
    model = CustomUser
