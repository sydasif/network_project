import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from datetime import timedelta
from django.shortcuts import get_object_or_404, redirect, render
from nornir.core.filter import F

from core.nornir_init import init_nornir
from core.tasks import save_config, show_ip, run_custom_command

from .forms import DeviceForm, TaskForm, TaskLogFilterForm
from .models import NetworkDevice, TaskLog

logger = logging.getLogger(__name__)


def home_view(request):
    """Render the home page with navigation links."""
    return render(request, "home.html", {"request": request})


TASK_MAP = {
    "show_ip": show_ip,
    "save_config": save_config,
    "custom_command": run_custom_command,
}


def process_task_result(result, task_type, user, custom_command=None):
    """Helper function to process task results and create logs."""
    execution_output = {}

    for host, task_result in result.items():
        output = (
            task_result.result if not task_result.failed else str(task_result.exception)
        )
        status = "failure" if task_result.failed else "success"
        execution_output[host] = {"output": output, "status": status}

        TaskLog.objects.create(
            device_name=host,
            task_type=task_type,
            output=output,
            status=status,
            user=user,
            custom_command=custom_command if task_type == "custom_command" else None,
        )

        if task_result.failed:
            logger.error(f"Task {task_type} failed on {host}: {task_result.exception}")
        else:
            logger.info(f"Task {task_type} successful on {host}")

    return execution_output


@login_required
def task_view(request):
    nr = init_nornir()
    device_choices = [(h, h) for h in nr.inventory.hosts.keys()]
    execution_output = None
    error_message = None

    if request.method == "POST":
        form = TaskForm(request.POST, device_choices=device_choices)
        if form.is_valid():
            task_type = form.cleaned_data["task_type"]
            selected_devices = form.cleaned_data["devices"]
            custom_command = form.cleaned_data.get("custom_command")
            task_func = TASK_MAP[task_type]

            try:
                subset = (
                    nr.filter(F(name__in=selected_devices)) if selected_devices else nr
                )
                if task_type == "custom_command":
                    result = subset.run(task=task_func, command=custom_command)
                else:
                    result = subset.run(task=task_func)
                execution_output = process_task_result(
                    result, task_type, request.user, custom_command
                )
            except Exception as e:
                error_message = str(e)
                logger.exception(f"Error executing task {task_type}: {e}")
    else:
        form = TaskForm(device_choices=device_choices)

    return render(
        request,
        "task_form.html",
        {
            "form": form,
            "execution_output": execution_output,
            "error_message": error_message,
        },
    )


@login_required
def execution_logs(request):
    tasklogs_list = TaskLog.objects.filter(user=request.user)
    form = TaskLogFilterForm(request.GET or None)

    if form.is_valid():
        device_name = form.cleaned_data.get("device_name")
        task_type = form.cleaned_data.get("task_type")
        status = form.cleaned_data.get("status")
        start_date = form.cleaned_data.get("start_date")
        end_date = form.cleaned_data.get("end_date")

        if device_name:
            tasklogs_list = tasklogs_list.filter(device_name=device_name)
        if task_type:
            tasklogs_list = tasklogs_list.filter(task_type=task_type)
        if status:
            tasklogs_list = tasklogs_list.filter(status=status)
        if start_date:
            tasklogs_list = tasklogs_list.filter(timestamp__gte=start_date)
        if end_date:
            # Add one day to the end_date to include the entire day
            tasklogs_list = tasklogs_list.filter(
                timestamp__lt=end_date + timedelta(days=1)
            )

    tasklogs_list = tasklogs_list.order_by("-timestamp")

    paginator = Paginator(tasklogs_list, 10)
    page_number = request.GET.get("page")
    tasklogs = paginator.get_page(page_number)

    return render(
        request,
        "execution_logs.html",
        {"tasklogs": tasklogs, "page_obj": tasklogs, "form": form},
    )


@login_required
def dashboard_view(request):
    """
    Display the network automation dashboard with device status and recent tasks.
    """
    # Get base data
    # Get base data
    devices = NetworkDevice.objects.all().order_by("name")
    recent_tasks = TaskLog.objects.all().order_by("-timestamp")[:10]

    # Calculate device count
    device_count = devices.count()

    # Calculate task success rate and failure rate
    total_tasks = TaskLog.objects.count()
    if total_tasks > 0:
        successful_tasks = TaskLog.objects.filter(status="success").count()
        task_success_rate = round((successful_tasks / total_tasks) * 100, 1)
        task_failure_rate = round(100 - task_success_rate, 1)
    else:
        task_success_rate = 0
        task_failure_rate = 0

    # Get last backup time
    last_backup = (
        TaskLog.objects.filter(task_type="save_config", status="success")
        .order_by("-timestamp")
        .first()
    )
    last_backup_time = last_backup.timestamp if last_backup else "N/A"

    context = {
        "devices": devices,
        "recent_tasks": recent_tasks,
        "device_count": device_count,
        "task_success_rate": task_success_rate,
        "task_failure_rate": task_failure_rate,
        "last_backup_time": last_backup_time,
    }

    return render(request, "dashboard.html", context)


@login_required
def device_list_view(request):
    """Display a list of network devices."""
    devices = NetworkDevice.objects.all().order_by("hostname")
    paginator = Paginator(devices, 10)
    page_number = request.GET.get("page")
    device_list = paginator.get_page(page_number)
    return render(
        request, "device_list.html", {"devices": device_list, "page_obj": device_list}
    )


@login_required
def edit_device(request, device_id):
    device = get_object_or_404(NetworkDevice, id=device_id)
    if request.method == "POST":
        form = DeviceForm(request.POST, instance=device)
        if form.is_valid():
            form.save()
            messages.success(request, f"Device {device.hostname} updated successfully")
            return redirect("device_list")
    else:
        form = DeviceForm(instance=device)
    return render(request, "device_form.html", {"form": form, "device": device})


@login_required
def delete_device(request, device_id):
    device = get_object_or_404(NetworkDevice, id=device_id)
    if request.method == "POST":
        hostname = device.hostname
        device.delete()
        messages.success(request, f"Device {hostname} deleted successfully")
    return redirect("device_list")
