from datetime import datetime

from django import forms
from django.core.exceptions import ValidationError
from service.models import Clients, Message, Distribution


class StyleMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if field not in ['start_time', 'end_time']:
                self.fields[field].widget.attrs.update({'class': 'form-control'})
            else:
                self.fields[field].widget.attrs.update({'class': 'form-control', 'placeholder': 'YYYY-MM-DD HH:MM'})


class ClientsForm(StyleMixin, forms.ModelForm):
    class Meta:
        model = Clients
        fields = '__all__'


class MessageForm(StyleMixin, forms.ModelForm):
    class Meta:
        model = Message
        fields = '__all__'


class DistributionForm(StyleMixin, forms.ModelForm):
    class Meta:
        model = Distribution
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        if start_time >= end_time:
            raise ValidationError('Время начала отправки должно быть меньше времени окончания отправки!')
        elif datetime.now() > start_time.replace(tzinfo=None):
            raise ValidationError('Время начала отправки должно быть меньше текущего времени!')
