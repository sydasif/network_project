from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class NetworkDevice(models.Model):
    name = models.CharField(max_length=100)
    hostname = models.GenericIPAddressField()
    platform = models.CharField(max_length=50)
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class TaskLog(models.Model):
    device_name = models.CharField(max_length=100)
    task_type = models.CharField(max_length=100)
    output = models.TextField()
    status = models.CharField(
        max_length=20, choices=[("success", "Success"), ("failure", "Failure")]
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="task_logs", null=True
    )

    def __str__(self):
        return f"{self.device_name} - {self.task_type} - {self.status}"
