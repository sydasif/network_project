from django.urls import path

from .views import task_view

urlpatterns = [
    path("", task_view, name="task_form"),  # Unified form endpoint
    path("home/", task_view, name="home"),  # Dashboard landing page
]
