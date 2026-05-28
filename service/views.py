from datetime import datetime

from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.shortcuts import render
from django.core.mail import send_mail
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

from config.settings import EMAIL_HOST_USER
from service.forms import ClientsForm, MessageForm, DistributionForm
from service.models import Clients, Message, Distribution, Attemp


class ClientsListView(LoginRequiredMixin, ListView):
    model = Clients


class ClientsDetailView(LoginRequiredMixin, DetailView):
    model = Clients


class ClientsCreateView(LoginRequiredMixin, CreateView):
    model = Clients
    form_class = ClientsForm
    success_url = reverse_lazy('service:clients_list')

    def form_valid(self, form):
        user = self.request.user
        form.instance.owner = user
        return super().form_valid(form)


class ClientsUpdateView(LoginRequiredMixin, UpdateView):
    model = Clients
    form_class = ClientsForm
    success_url = reverse_lazy('service:clients_list')

    def form_valid(self, form):
        user = self.request.user
        form.instance.owner = user
        return super().form_valid(form)


class ClientsDeleteView(LoginRequiredMixin, DeleteView):
    model = Clients
    success_url = reverse_lazy('service:clients_list')


class MessageListView(LoginRequiredMixin, ListView):
    model = Message


class MessageDetailView(LoginRequiredMixin, DetailView):
    model = Message


class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    form_class = MessageForm
    success_url = reverse_lazy('service:message_list')

    def form_valid(self, form):
        user = self.request.user
        form.instance.owner = user
        return super().form_valid(form)


class MessageUpdateView(LoginRequiredMixin, UpdateView):
    model = Message
    form_class = MessageForm
    success_url = reverse_lazy('service:message_list')

    def form_valid(self, form):
        user = self.request.user
        form.instance.owner = user
        return super().form_valid(form)


class MessageDeleteView(LoginRequiredMixin, DeleteView):
    model = Message
    success_url = reverse_lazy('service:message_list')


class DistributionListView(LoginRequiredMixin, ListView):
    model = Distribution

    def get_queryset(self):
        """Метод обновляет статус рассылки"""
        queryset = super().get_queryset()
        for obj in queryset:
            obj.update_status()
        return queryset


class DistributionDetailView(LoginRequiredMixin, DetailView):
    model = Distribution

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj is not None and obj.start_time.replace(
                tzinfo=None) < datetime.now() < obj.end_time.replace(tzinfo=None):
            emails = list(obj.recipients.values_list('email', flat=True))
            try:
                send_mail(obj.message.theme, obj.message.text, EMAIL_HOST_USER, emails)
                status = 'Успешно'
                server_response = 'Сообщений нет'
            except Exception as e:
                status = 'Не успешно'
                server_response = str(e)
            finally:
                count_emails = len(emails)
                attempt_time = datetime.now()
                owner = request.user
            Attemp.objects.create(attempt_time=attempt_time, status_2=status, server_response=server_response,
                                  mailing=obj, count_emails=count_emails, owner=owner)
            return render(request, 'service/distribution_success.html')
        else:
            return render(request, 'service/distribution_unsuccess.html')


class DistributionCreateView(LoginRequiredMixin, CreateView):
    model = Distribution
    form_class = DistributionForm
    success_url = reverse_lazy('service:distribution_list')

    def form_valid(self, form):
        user = self.request.user
        form.instance.owner = user
        return super().form_valid(form)


class DistributionUpdateView(LoginRequiredMixin, UpdateView):
    model = Distribution
    form_class = DistributionForm
    success_url = reverse_lazy('service:distribution_list')

    def form_valid(self, form):
        user = self.request.user
        form.instance.owner = user
        return super().form_valid(form)


class DistributionDeleteView(LoginRequiredMixin, DeleteView):
    model = Distribution
    success_url = reverse_lazy('service:distribution_list')


class AttempListView(LoginRequiredMixin, ListView):
    model = Attemp

@login_required()
def main(requests):
    distributions = Distribution.objects.all()
    distribution_count = distributions.count()
    distributions_active = Distribution.objects.filter(status='progress').count()
    clients_count = Clients.objects.all().count()
    context = {'distribution_count': distribution_count, 'distributions_active': distributions_active,
               'clients_count': clients_count}
    return render(requests, 'service/main.html', context)

@login_required()
def get_statistic(requests):
    attemps = Attemp.objects.all()
    count_success = len([attemp for attemp in attemps if attemp.status_2 == 'Успешно'])
    count_unsuccess = len(attemps) - count_success
    message = sum([attemp.count_emails for attemp in attemps if attemp.status_2 == 'Успешно'])
    context = {'count_success': count_success, 'count_unsuccess': count_unsuccess, 'message': message, }
    return render(requests, 'service/statistic.html', context)
