from datetime import datetime

from django.core.mail import send_mail
from django.core.management.base import BaseCommand

from config.settings import EMAIL_HOST_USER
from service.models import Attemp, Distribution


class Command(BaseCommand):

    def add_arguments(self, parser):
        """Парсер для отделения id рассылки из кастомной команды"""
        parser.add_argument("--id", type=int, help="ID of the mailing")

    def handle(self, *args, **kwargs):
        """Метод осуществляет отправку сообщения заданной рассылки адресатам"""
        mailing_id = kwargs["id"]
        if mailing_id is not None:
            self.stdout.write(f"Запускаем рассылку с ID: {mailing_id}")
            distribution = Distribution.objects.get(id=mailing_id)
            if distribution is not None and distribution.start_time.replace(
                tzinfo=None
            ) < datetime.now() < distribution.end_time.replace(tzinfo=None):
                emails = list(distribution.recipients.values_list("email", flat=True))
                for email in emails:
                    try:
                        send_mail(distribution.message.theme, distribution.message.text, EMAIL_HOST_USER, [email])
                        attempt_time = datetime.now()
                        status = "Успешно"
                        server_response = "Сообщений нет"
                    except Exception as e:
                        attempt_time = datetime.now()
                        status = "Не успешно"
                        server_response = str(e)
                    Attemp.objects.create(
                        attempt_time=attempt_time,
                        status_2=status,
                        server_response=server_response,
                        mailing=distribution,
                    )
            else:
                self.stdout.write("Отправка вне указанных сроков запрещена!")

        else:
            self.stdout.write("ID не указан!")
