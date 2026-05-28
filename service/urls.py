from service import views
from service.apps import ServiceConfig
from django.urls import path

from service.views import ClientsListView, ClientsDetailView, ClientsUpdateView, ClientsCreateView, ClientsDeleteView, \
    MessageListView, MessageUpdateView, MessageCreateView, MessageDeleteView, MessageDetailView, DistributionListView, \
    DistributionUpdateView, DistributionCreateView, DistributionDeleteView, DistributionDetailView, AttempListView, main

app_name = ServiceConfig.name

urlpatterns = [
    path("", views.main, name="main"),
    path("clients/", ClientsListView.as_view(), name="clients_list"),
    path("clients/<int:pk>/", ClientsDetailView.as_view(), name="clients_detail"),
    path("clients/<int:pk>/update/", ClientsUpdateView.as_view(), name="clients_update"),
    path("clients/create/", ClientsCreateView.as_view(), name="clients_create"),
    path("clients/<int:pk>/delete/", ClientsDeleteView.as_view(), name="clients_delete"),
    path("message/", MessageListView.as_view(), name="message_list"),
    path("message/<int:pk>/", MessageDetailView.as_view(), name="message_detail"),
    path("message/<int:pk>/update/", MessageUpdateView.as_view(), name="message_update"),
    path("message/create/", MessageCreateView.as_view(), name="message_create"),
    path("message/<int:pk>/delete/", MessageDeleteView.as_view(), name="message_delete"),
    path("distribution/", DistributionListView.as_view(), name="distribution_list"),
    path("distribution/<int:pk>/", DistributionDetailView.as_view(), name="distribution_detail"),
    path("distribution/<int:pk>/update/", DistributionUpdateView.as_view(), name="distribution_update"),
    path("distribution/create/", DistributionCreateView.as_view(), name="distribution_create"),
    path("distribution/<int:pk>/delete/", DistributionDeleteView.as_view(), name="distribution_delete"),
    path("attemp/", AttempListView.as_view(), name="attemp_list"),
    path("statistic/", views.get_statistic, name="statistic"),
]
