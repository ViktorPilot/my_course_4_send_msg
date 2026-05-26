from datetime import datetime

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
        if obj is not None and obj.start_time.replace(
                tzinfo=None) < datetime.now() < obj.end_time.replace(tzinfo=None):
            emails = list(obj.recipients.values_list('email', flat=True))
            for email in emails:
                try:
                    send_mail(obj.message.theme, obj.message.text, EMAIL_HOST_USER, [email])
                    attempt_time = datetime.now()
                    status = 'Успешно'
                    server_response = 'Сообщений нет'
                except Exception as e:
                    attempt_time = datetime.now()
                    status = 'Не успешно'
                    server_response = str(e)
                Attemp.objects.create(attempt_time=attempt_time, status_2=status, server_response=server_response,
                                      mailing=obj)
            return render(request,'service/distribution_success.html')
        else:
            return render(request, 'service/distribution_unsuccess.html')


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

def main(requests):
    distributions = Distribution.objects.all()
    distribution_count = distributions.count()
    distributions_active = Distribution.objects.filter(status='progress').count()
    clients_count = Clients.objects.all().count()
    context = {'distribution_count':distribution_count,'distributions_active':distributions_active,'clients_count':clients_count}
    return render(requests, 'service/main.html', context)




