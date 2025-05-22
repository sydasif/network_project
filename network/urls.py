from django.urls import path

from . import views

urlpatterns = [
    path("", views.home_view, name="home"),  # Home page with navigation
    path(
        "network-task/", views.task_view, name="network_task"
    ),  # Network configuration task
    path(
        "execution-logs/", views.execution_logs, name="execution_logs"
    ),  # Task execution logs
    path("dashboard/", views.dashboard_view, name="dashboard"),  # Network dashboard
    path("devices/", views.device_list_view, name="device_list"),  # Device list page
]
