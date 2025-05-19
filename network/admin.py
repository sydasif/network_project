from django.contrib import admin
from .models import NetworkDevice, TaskLog

# Register your models here.
admin.site.register(NetworkDevice)
admin.site.register(TaskLog)
