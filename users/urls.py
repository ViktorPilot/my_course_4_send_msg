from django.urls import path
from users import views
from users.apps import UsersConfig
from users.views import RegisterView, CustomLoginView, CustomLogoutView, email_verification

app_name = UsersConfig.name

urlpatterns = [
    path("register/", RegisterView.as_view(), name='register'),
    path("login/", CustomLoginView.as_view(), name='login'),
    path("logout/", CustomLogoutView.as_view(), name='logout'),
    path("email_confirm/<str:token>/", email_verification, name='email_confirm'),
    path("success_register/", views.success_register, name='success_register'),
]
