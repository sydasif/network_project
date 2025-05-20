from django.urls import path

from .views import task_view

urlpatterns = [
    path("", task_view, name="task_view"),  # Your main view
]
