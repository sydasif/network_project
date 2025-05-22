import logging
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.contrib import messages
from nornir.core.filter import F
from core.nornir_init import init_nornir
from core.tasks import save_config, show_ip, get_device_uptime
from .forms import TaskForm
from django.contrib.auth.decorators import login_required
from .models import TaskLog, NetworkDevice, DeviceUptime
from django.db.models import Max

logger = logging.getLogger(__name__)


def home_view(request):
    """Render the home page with navigation links."""
    return render(request, "home.html", {"request": request})


TASK_MAP = {
    "show_ip": show_ip,
    "save_config": save_config,
    "get_device_uptime": get_device_uptime,
}


def process_task_result(result, task_type, user):
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
            task_func = TASK_MAP[task_type]

            try:
                subset = (
                    nr.filter(F(name__in=selected_devices)) if selected_devices else nr
                )
                result = subset.run(task=task_func)
                execution_output = process_task_result(result, task_type, request.user)
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
    tasklogs_list = TaskLog.objects.filter(user=request.user).order_by("-timestamp")
    paginator = Paginator(tasklogs_list, 10)
    page_number = request.GET.get("page")
    tasklogs = paginator.get_page(page_number)
    return render(
        request, "execution_logs.html", {"tasklogs": tasklogs, "page_obj": tasklogs}
    )


@login_required
def dashboard_view(request):
    """
    Display the network automation dashboard with device status and recent tasks.
    """
    # Get base data
    devices = NetworkDevice.objects.all().order_by("name")
    recent_tasks = TaskLog.objects.all().order_by("-timestamp")[:10]
    device_uptimes = DeviceUptime.objects.all().order_by("-timestamp")

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
        task_failure_rate = 0  # Calculate average uptime in hours
    if device_uptimes.exists():
        latest_uptimes = DeviceUptime.objects.values("device").annotate(
            latest_uptime=Max("uptime_seconds")
        )
        total_uptime = sum(item["latest_uptime"] for item in latest_uptimes)
        # Convert seconds to hours
        average_uptime = round((total_uptime / len(latest_uptimes)) / 3600, 1)
    else:
        average_uptime = 0

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
        "device_uptimes": device_uptimes,
        "device_count": device_count,
        "task_success_rate": task_success_rate,
        "task_failure_rate": task_failure_rate,
        "average_uptime": average_uptime,
        "last_backup_time": last_backup_time,
    }

    return render(request, "dashboard.html", context)
