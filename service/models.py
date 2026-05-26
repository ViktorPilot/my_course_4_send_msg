import datetime

from django.db import models


class Clients(models.Model):
    email = models.CharField(max_length=50, verbose_name='Электронная почта', unique=True)
    name = models.CharField(max_length=100, verbose_name='ФИО')
    comment = models.TextField(verbose_name='Комментарий', null=True, blank=True)

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = 'Получатель'
        verbose_name_plural = 'Получатели'
        ordering = ['id',]
        db_table = 'clients'


class Message(models.Model):
    theme = models.CharField(max_length=100, verbose_name='Тема письма')
    text = models.TextField(verbose_name='Текст письма', null=True, blank=True)

    def __str__(self):
        return self.theme

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
        ordering = ['id',]
        db_table = 'message'


class Distribution(models.Model):
    CHOICES_STATUS = [('finished', 'Завершена'), ('create', 'Создана'), ('progress', 'Запущена')]
    start_time = models.DateTimeField(verbose_name='Дата и время первой отправки',)
    end_time = models.DateTimeField(verbose_name='Дата и время окончания отправки',)
    status = models.CharField(max_length=30, verbose_name='Статус', choices=CHOICES_STATUS, default='Создана')
    message = models.ForeignKey('Message', on_delete=models.CASCADE, related_name='distribution',)
    recipients = models.ManyToManyField('Clients', related_name='distribution')

    def update_status(self):
        if datetime.datetime.now() < self.start_time.replace(tzinfo=None):
            self.status = 'create'
        elif datetime.datetime.now() > self.end_time.replace(tzinfo=None):
            self.status = 'finished'
        else:
            self.status = 'progress'
        self.save()

    def __str__(self):
        return self.status

    class Meta:
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'
        ordering = ['id',]
        db_table = 'distribution'


class Attemp(models.Model):
    CHOICES_STATUS_2 = [('success', 'Успешно'), ('unsuccess', 'Не успешно')]
    attempt_time = models.DateTimeField(verbose_name='Дата и время попытки', null=True, blank=True)
    status_2 = models.CharField(max_length=30, verbose_name='Статус', choices=CHOICES_STATUS_2, default='Успешно')
    server_response = models.TextField(verbose_name='Ответ почтового сервера', null=True, blank=True)
    mailing = models.ForeignKey('Distribution', on_delete=models.CASCADE,
                                               related_name='mailing')

    def __str__(self):
        return self.status_2

    class Meta:
        verbose_name = 'Попытка'
        verbose_name_plural = 'Попытки'
        ordering = ['id',]
        db_table = 'attemp'
