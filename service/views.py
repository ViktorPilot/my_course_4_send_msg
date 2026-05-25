from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.shortcuts import render
from django.http.response import HttpResponse
from django.core.mail import send_mail

from config.settings import EMAIL_HOST_USER
from service.forms import ClientsForm, MessageForm, DistributionForm
from service.models import Clients, Message, Distribution, Attemp


class ClientsListView(ListView):
    model = Clients

class ClientsDetailView(DetailView):
    model = Clients


class ClientsCreateView(CreateView):
    model = Clients
    form_class = ClientsForm
    success_url = reverse_lazy('service:clients_list')

class ClientsUpdateView(UpdateView):
    model = Clients
    form_class = ClientsForm
    success_url = reverse_lazy('service:clients_list')

class ClientsDeleteView(DeleteView):
    model = Clients
    success_url = reverse_lazy('service:clients_list')

class MessageListView(ListView):
    model = Message

class MessageDetailView(DetailView):
    model = Message

class MessageCreateView(CreateView):
    model = Message
    form_class = MessageForm
    success_url = reverse_lazy('service:message_list')

class MessageUpdateView(UpdateView):
    model = Message
    form_class = MessageForm
    success_url = reverse_lazy('service:message_list')

class MessageDeleteView(DeleteView):
    model = Message
    success_url = reverse_lazy('service:message_list')


class DistributionListView(ListView):
    model = Distribution

class DistributionDetailView(DetailView):
    model = Distribution

    def post(self, request, *args, **kwargs):
        obj  = self.get_object()
        list_emails = obj.addressee.all().values_list('email', flat=True)
        recipient_list = [i for i in list_emails]
        subject = obj.distribution_message.theme
        message = obj.distribution_message.text
        send_mail(subject=subject, message= message, from_email=EMAIL_HOST_USER, recipient_list=recipient_list)
        return render(request,'service/distribution_success.html')

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.update_status()
        return obj

class DistributionCreateView(CreateView):
    model = Distribution
    form_class = DistributionForm
    success_url = reverse_lazy('service:distribution_list')


class DistributionUpdateView(UpdateView):
    model = Distribution
    form_class = DistributionForm
    success_url = reverse_lazy('service:distribution_list')

class DistributionDeleteView(DeleteView):
    model = Distribution
    success_url = reverse_lazy('service:distribution_list')

class AttempListView(ListView):
    model = Attemp





