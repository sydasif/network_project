from django.db import models

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
    task_name = models.CharField(max_length=100)
    command = models.TextField()
    output = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.device_name} | {self.task_name} | {self.timestamp}"
