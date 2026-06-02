from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from config.settings import EMAIL_HOST_USER
from service.forms import ClientsForm, DistributionForm, MessageForm
from service.models import Attemp, Clients, Distribution, Message


class ClientsListView(LoginRequiredMixin, ListView):
    """Контроллер страницы списка клиентов"""

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


@method_decorator(cache_page(60), name="dispatch")
class ClientsDetailView(LoginRequiredMixin, DetailView):
    """Контроллер страницы детальной информации о клиенте"""

    model = Clients


class ClientsCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """Контроллер страницы создания нового клиента"""

    model = Clients
    form_class = ClientsForm
    success_url = reverse_lazy("service:clients_list")
    permission_required = "service.add_clients"

    def form_valid(self, form):
        """Метод добавляет текущего пользователя в поле базы данных Clients при создании нового клиента"""
        user = self.request.user
        form.instance.owner = user
        return super().form_valid(form)


class ClientsUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """Контроллер страницы редактирования информации о клиенте"""

    model = Clients
    form_class = ClientsForm
    success_url = reverse_lazy("service:clients_list")
    permission_required = "service.change_clients"

    def form_valid(self, form):
        """Метод добавляет текущего пользователя в поле базы данных Clients при обновлении пользователя"""
        user = self.request.user
        form.instance.owner = user
        return super().form_valid(form)


class ClientsDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """Контроллер страницы удаления клиента"""

    model = Clients
    success_url = reverse_lazy("service:clients_list")
    permission_required = "service.delete_clients"


class MessageListView(LoginRequiredMixin, ListView):
    """Контроллер страницы списка сообщений"""

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


@method_decorator(cache_page(60), name="dispatch")
class MessageDetailView(LoginRequiredMixin, DetailView):
    """Контроллер страницы детальной информации о сообщении"""

    model = Message


class MessageCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """Контроллер страницы создания нового сообщения"""

    model = Message
    form_class = MessageForm
    success_url = reverse_lazy("service:message_list")
    permission_required = "service.add_message"

    def form_valid(self, form):
        """Метод добавляет текущего пользователя в поле базы данных Message при создании нового сообщения"""
        user = self.request.user
        form.instance.owner = user
        return super().form_valid(form)


class MessageUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """Контроллер страницы редактирования сообщения"""

    model = Message
    form_class = MessageForm
    success_url = reverse_lazy("service:message_list")
    permission_required = "service.change_message"

    def form_valid(self, form):
        """Метод добавляет текущего пользователя в поле базы данных Message при обновлении сообщения"""
        user = self.request.user
        form.instance.owner = user
        return super().form_valid(form)


class MessageDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """Контроллер страницы удаления сообщения"""

    model = Message
    success_url = reverse_lazy("service:message_list")
    permission_required = "service.delete_message"


class DistributionListView(LoginRequiredMixin, ListView):
    """Контроллер страницы списка рассылок"""

    model = Distribution

    def get_queryset(self):
        """Метод обновляет статус рассылки и фильтрует список рассылок из БД, предоставляя только
        созданных текущим пользователем, если он не является менеджером"""
        queryset = super().get_queryset()
        user = self.request.user
        if not user.groups.filter(name="manager").exists():
            queryset = queryset.filter(owner=user)
        for obj in queryset:
            if not obj.status == "paused":
                obj.update_status()
        return queryset

    def post(self, request, *args, **kwargs):
        """Метод позволяет менеджеру приостанавливать/возобновлять рассылку"""
        pk = request.POST.get("pk")
        distribution = Distribution.objects.get(pk=pk)
        if distribution.status != "paused":
            distribution.status = "paused"
        else:
            distribution.status = "create"
        distribution.save()
        return redirect("/service/distribution")


class DistributionDetailView(LoginRequiredMixin, DetailView):
    """Контроллер страницы детальной информации о рассылке"""

    model = Distribution

    def post(self, request, *args, **kwargs):
        """Метод отправляет рассылку получателям при выполнении условий: если статус рассылки
        не приостановлен модератором и текущее дата/время находятся в диапазоне возможного периода рассылки"""
        obj = self.get_object()
        if (
            obj is not None
            and obj.start_time.replace(tzinfo=None) < datetime.now() < obj.end_time.replace(tzinfo=None)
            and obj.status != "paused"
        ):
            emails = list(obj.recipients.values_list("email", flat=True))
            try:
                send_mail(obj.message.theme, obj.message.text, EMAIL_HOST_USER, emails)
                status = "Успешно"
                server_response = "Сообщений нет"
            except Exception as e:
                status = "Не успешно"
                server_response = str(e)
            finally:
                count_emails = len(emails)
                attempt_time = datetime.now()
                owner = request.user
            Attemp.objects.create(
                attempt_time=attempt_time,
                status_2=status,
                server_response=server_response,
                mailing=obj,
                count_emails=count_emails,
                owner=owner,
            )
            return render(request, "service/distribution_success.html")
        else:
            return render(request, "service/distribution_unsuccess.html")


class DistributionCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """Контроллер страницы создания новой рассылки"""

    model = Distribution
    form_class = DistributionForm
    success_url = reverse_lazy("service:distribution_list")
    permission_required = "service.add_distribution"

    def get_form(self, form_class=None):
        """Метод фильтрует список клиентов в форме, предоставляя только созданных текущим пользователем"""
        user = self.request.user
        form = super().get_form(form_class)
        form.fields["recipients"].queryset = Clients.objects.filter(owner=user)
        form.fields["message"].queryset = Message.objects.filter(owner=user)
        return form

    def form_valid(self, form):
        """Метод добавляет текущего пользователя в поле базы данных Distribution при создании новой рассылки"""
        user = self.request.user
        form.instance.owner = user
        return super().form_valid(form)


class DistributionUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """Контроллер страницы редактирования рассылки"""

    model = Distribution
    form_class = DistributionForm
    success_url = reverse_lazy("service:distribution_list")
    permission_required = "service.change_distribution"

    def get_form(self, form_class=None):
        """Метод фильтрует список клиентов в форме, предоставляя только созданных текущим пользователем"""
        user = self.request.user
        form = super().get_form(form_class)
        form.fields["recipients"].queryset = Clients.objects.filter(owner=user)
        return form

    def form_valid(self, form):
        """Метод добавляет текущего пользователя в поле базы данных Distribution при обновлении рассылки"""
        user = self.request.user
        form.instance.owner = user
        return super().form_valid(form)


class DistributionDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """Контроллер страницы удаления рассылки"""

    model = Distribution
    success_url = reverse_lazy("service:distribution_list")
    permission_required = "service.delete_distribution"


class AttempListView(LoginRequiredMixin, ListView):
    """Контроллер страницы списка попыток рассылок"""

    model = Attemp

    def render_to_response(self, context, **response_kwargs):
        """Клиентское кэширование страницы 'Попытки рассылок' на 60 секунд"""
        response = super().render_to_response(context, **response_kwargs)
        response["Cache-Control"] = "max-age=60"
        return response

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
def main(request):
    """Контроллер главной страницы"""
    user = request.user
    if user.groups.filter(name="manager").exists():
        distributions = Distribution.objects.all()
        for obj in distributions:
            obj.update_status()
        clients_count = Clients.objects.all().count()
        distributions_active = Distribution.objects.filter(status="progress").count()
    else:
        distributions = Distribution.objects.filter(owner=user)
        for obj in distributions:
            if not obj.status == "paused":
                obj.update_status()
        clients_count = Clients.objects.filter(owner=user).count()
        distributions_active = Distribution.objects.filter(owner=user, status="progress").count()
    distribution_count = distributions.count()

    context = {
        "distribution_count": distribution_count,
        "distributions_active": distributions_active,
        "clients_count": clients_count,
    }
    return render(request, "service/main.html", context)


@login_required()
def get_statistic(request):
    """Контроллер страницы статистики рассылок пользователей"""
    user = request.user
    if user.groups.filter(name="manager").exists():
        attemps = Attemp.objects.all()
    else:
        attemps = Attemp.objects.filter(owner=user)
    count_success = len([attemp for attemp in attemps if attemp.status_2 == "Успешно"])
    count_unsuccess = len(attemps) - count_success
    message = sum([attemp.count_emails for attemp in attemps if attemp.status_2 == "Успешно"])
    context = {"count_success": count_success, "count_unsuccess": count_unsuccess, "message": message}
    return render(request, "service/statistic.html", context)
