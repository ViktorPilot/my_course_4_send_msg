from django.urls import path

from users.apps import UsersConfig
from users.views import RegisterView, CustomLoginView, CustomLogoutView

app_name = UsersConfig.name

urlpatterns = [
    path("register/", RegisterView.as_view(), name='register'),
    path("login/", CustomLoginView.as_view(), name='login'),
    path("logout/", CustomLogoutView.as_view(), name='logout'),
]
