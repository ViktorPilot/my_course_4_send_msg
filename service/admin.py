from django.contrib import admin

from service.models import Clients, Message, Distribution, Attemp

admin.site.register(Clients)
admin.site.register(Message)
admin.site.register(Distribution)
admin.site.register(Attemp)
