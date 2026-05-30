import datetime

from django.db import models

from users.models import CustomUser


class Clients(models.Model):
    """Класс создания экземпляра модели клиента"""
    email = models.CharField(max_length=50, verbose_name='Электронная почта', unique=True)
    name = models.CharField(max_length=100, verbose_name='ФИО')
    comment = models.TextField(verbose_name='Комментарий', null=True, blank=True)
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='clients', null=True, blank=True)

    def __str__(self):
        """Магический метод возвращает электронную почту клиента"""
        return self.email

    class Meta:
        """Метакласс модели клиента"""
        verbose_name = 'Получатель'
        verbose_name_plural = 'Получатели'
        ordering = ['id',]
        db_table = 'clients'


class Message(models.Model):
    """Класс создания экземпляра модели сообщения"""
    theme = models.CharField(max_length=100, verbose_name='Тема письма')
    text = models.TextField(verbose_name='Текст письма', null=True, blank=True)
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='message', null=True, blank=True)

    def __str__(self):
        """Магический метод возвращает тему сообщения"""
        return self.theme

    class Meta:
        """Метакласс модели сообщения"""
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
        ordering = ['id',]
        db_table = 'message'


class Distribution(models.Model):
    """Класс создания экземпляра модели рассылки"""
    CHOICES_STATUS = [('finished', 'Завершена'), ('create', 'Создана'), ('progress', 'Запущена'), ('paused', 'Приостановлена')]
    start_time = models.DateTimeField(verbose_name='Дата и время первой отправки',)
    end_time = models.DateTimeField(verbose_name='Дата и время окончания отправки',)
    status = models.CharField(max_length=30, verbose_name='Статус', choices=CHOICES_STATUS, default='Создана')
    message = models.ForeignKey('Message', on_delete=models.CASCADE, related_name='distribution',)
    recipients = models.ManyToManyField('Clients', related_name='distribution')
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='distribution', null=True, blank=True)

    def update_status(self):
        """Метод обновляет статус рассылки в БД, учитывая текущее время и дату"""
        if datetime.datetime.now() < self.start_time.replace(tzinfo=None):
            self.status = 'create'
        elif datetime.datetime.now() > self.end_time.replace(tzinfo=None):
            self.status = 'finished'
        else:
            self.status = 'progress'
        self.save()

    def __str__(self):
        """Магический метод возвращает статус рассылки"""
        return self.status

    class Meta:
        """Метакласс модели рассылки"""
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'
        ordering = ['id',]
        db_table = 'distribution'


class Attemp(models.Model):
    """Класс создания экземпляра попытки рассылки"""
    CHOICES_STATUS_2 = [('success', 'Успешно'), ('unsuccess', 'Не успешно')]
    attempt_time = models.DateTimeField(verbose_name='Дата и время попытки', null=True, blank=True)
    status_2 = models.CharField(max_length=30, verbose_name='Статус', choices=CHOICES_STATUS_2, default='Успешно')
    server_response = models.TextField(verbose_name='Ответ почтового сервера', null=True, blank=True)
    mailing = models.ForeignKey('Distribution', on_delete=models.CASCADE,
                                               related_name='mailing')
    count_emails = models.PositiveIntegerField(verbose_name='Количество получателей', default=1)
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='attemp', null=True, blank=True)

    def __str__(self):
        """Магический метод возвращает статус попытки рассылки"""
        return self.status_2

    class Meta:
        """Метакласс модели попытки рассылки"""
        verbose_name = 'Попытка'
        verbose_name_plural = 'Попытки'
        ordering = ['id',]
        db_table = 'attemp'
