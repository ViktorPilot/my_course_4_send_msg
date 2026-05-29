from datetime import datetime

from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.shortcuts import render
from django.core.mail import send_mail
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required

from config.settings import EMAIL_HOST_USER
from service.forms import ClientsForm, MessageForm, DistributionForm
from service.models import Clients, Message, Distribution, Attemp
from users.models import CustomUser


class ClientsListView(LoginRequiredMixin, ListView):
    model = Clients

    def get_queryset(self):
        """Метод фильтрует список клиентов из БД, предоставляя только созданных текущим пользователем,
        если он не является менеджером"""
        queryset = super().get_queryset()
        user = self.request.user
        if user.groups.filter(name="manager").exists():
            return queryset
        else:
            return queryset.filter(owner=user)



class ClientsDetailView(LoginRequiredMixin, DetailView):
    model = Clients


class ClientsCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Clients
    form_class = ClientsForm
    success_url = reverse_lazy('service:clients_list')
    permission_required = 'service.add_clients'

    def form_valid(self, form):
        """Метод добавляет текущего пользователя в поле базы данных Clients при создании нового клиента"""
        user = self.request.user
        form.instance.owner = user
        return super().form_valid(form)


class ClientsUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Clients
    form_class = ClientsForm
    success_url = reverse_lazy('service:clients_list')
    permission_required = 'service.change_clients'

    def form_valid(self, form):
        """Метод добавляет текущего пользователя в поле базы данных Clients при обновлении пользователя"""
        user = self.request.user
        form.instance.owner = user
        return super().form_valid(form)


class ClientsDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Clients
    success_url = reverse_lazy('service:clients_list')
    permission_required = 'service.delete_clients'

class MessageListView(LoginRequiredMixin, ListView):
    model = Message

    def get_queryset(self):
        """Метод фильтрует список сообщений из БД, предоставляя только созданных текущим пользователем,
        если он не является менеджером"""
        queryset = super().get_queryset()
        user = self.request.user
        if user.groups.filter(name="manager").exists():
            return queryset
        else:
            return queryset.filter(owner=user)

class MessageDetailView(LoginRequiredMixin, DetailView):
    model = Message


class MessageCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Message
    form_class = MessageForm
    success_url = reverse_lazy('service:message_list')
    permission_required = 'service.add_message'

    def form_valid(self, form):
        """Метод добавляет текущего пользователя в поле базы данных Message при создании нового сообщения"""
        user = self.request.user
        form.instance.owner = user
        return super().form_valid(form)


class MessageUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Message
    form_class = MessageForm
    success_url = reverse_lazy('service:message_list')
    permission_required = 'service.change_message'

    def form_valid(self, form):
        """Метод добавляет текущего пользователя в поле базы данных Message при обновлении сообщения"""
        user = self.request.user
        form.instance.owner = user
        return super().form_valid(form)


class MessageDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Message
    success_url = reverse_lazy('service:message_list')
    permission_required = 'service.delete_message'

class DistributionListView(LoginRequiredMixin, ListView):
    model = Distribution

    def get_queryset(self):
        """Метод обновляет статус рассылки и фильтрует список рассылок из БД, предоставляя только
        созданных текущим пользователем, если он не является менеджером"""
        queryset = super().get_queryset()
        user = self.request.user
        if not user.groups.filter(name="manager").exists():
            queryset = queryset.filter(owner=user)
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


class DistributionCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Distribution
    form_class = DistributionForm
    success_url = reverse_lazy('service:distribution_list')
    permission_required = 'service.add_distribution'

    def get_form(self, form_class=None):
        """Метод фильтрует список клиентов в форме, предоставляя только созданных текущим пользователем"""
        user = self.request.user
        form = super().get_form(form_class)
        form.fields['recipients'].queryset = Clients.objects.filter(owner=user)
        form.fields['message'].queryset = Message.objects.filter(owner=user)
        return form

    def form_valid(self, form):
        """Метод добавляет текущего пользователя в поле базы данных Distribution при создании новой рассылки"""
        user = self.request.user
        form.instance.owner = user
        return super().form_valid(form)


class DistributionUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Distribution
    form_class = DistributionForm
    success_url = reverse_lazy('service:distribution_list')
    permission_required = 'service.change_distribution'

    def get_form(self, form_class=None):
        """Метод фильтрует список клиентов в форме, предоставляя только созданных текущим пользователем"""
        user = self.request.user
        form = super().get_form(form_class)
        form.fields['recipients'].queryset = Clients.objects.filter(owner=user)
        return form

    def form_valid(self, form):
        """Метод добавляет текущего пользователя в поле базы данных Distribution при обновлении рассылки"""
        user = self.request.user
        form.instance.owner = user
        return super().form_valid(form)


class DistributionDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Distribution
    success_url = reverse_lazy('service:distribution_list')
    permission_required = 'service.delete_distribution'

class AttempListView(LoginRequiredMixin, ListView):
    model = Attemp
    def get_queryset(self):
        """Метод фильтрует попытки отправки рассылок из БД, предоставляя только созданных текущим пользователем,
        если он не является менеджером"""
        queryset = super().get_queryset()
        user = self.request.user
        if user.groups.filter(name="manager").exists():
            return queryset
        else:
            return queryset.filter(owner=user)

@login_required()
def main(requests):
    """Контроллер главной страницы"""
    user = requests.user
    if user.groups.filter(name="manager").exists():
        distributions = Distribution.objects.all()
        for obj in distributions:
            obj.update_status()
        clients_count = Clients.objects.all().count()
        distributions_active = Distribution.objects.filter(status='progress').count()
    else:
        distributions = Distribution.objects.filter(owner=user)
        for obj in distributions:
            obj.update_status()
        clients_count = Clients.objects.filter(owner=user).count()
        distributions_active = Distribution.objects.filter(owner=user, status='progress').count()
    distribution_count = distributions.count()

    context = {'distribution_count': distribution_count, 'distributions_active': distributions_active,
               'clients_count': clients_count}
    return render(requests, 'service/main.html', context)

@login_required()
def get_statistic(requests):
    """Контроллер страницы статистики рассылок пользователей"""
    user = requests.user
    if user.groups.filter(name="manager").exists():
        attemps = Attemp.objects.all()
    else:
        attemps = Attemp.objects.filter(owner=user)
    count_success = len([attemp for attemp in attemps if attemp.status_2 == 'Успешно'])
    count_unsuccess = len(attemps) - count_success
    message = sum([attemp.count_emails for attemp in attemps if attemp.status_2 == 'Успешно'])
    context = {'count_success': count_success, 'count_unsuccess': count_unsuccess, 'message': message, }
    return render(requests, 'service/statistic.html', context)

