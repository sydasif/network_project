from django.core.paginator import Paginator
from django.shortcuts import render
from nornir.core.filter import F
from core.nornir_init import init_nornir
from core.tasks import save_config, show_ip, get_device_uptime
from .forms import TaskForm
from django.contrib.auth.decorators import login_required
from .models import TaskLog, NetworkDevice, DeviceUptime  # Import NetworkDevice


def home_view(request):
    """Render the home page with navigation links."""
    return render(request, "home.html")


TASK_MAP = {
    "show_ip": show_ip,
    "save_config": save_config,
    "get_device_uptime": get_device_uptime,
}


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

            if selected_devices:
                subset = nr.filter(F(name__in=selected_devices))
            else:
                subset = nr

            try:
                result = subset.run(task=task_func)
                execution_output = {}

                for host, task_result in result.items():
                    output = (
                        task_result.result
                        if task_result.failed is False
                        else str(task_result.exception)
                    )
                    status = "failure" if task_result.failed else "success"
                    execution_output[host] = {"output": output, "status": status}

                    # Still log the execution but don't display from DB
                    TaskLog.objects.create(
                        device_name=host,
                        task_type=task_type,
                        output=output,
                        status=status,
                        user=request.user,
                    )
            except Exception as e:
                error_message = str(e)
        else:
            pass  # Form is not valid, handle errors in template if needed
    else:
        form = TaskForm(device_choices=device_choices)

    task_type = request.POST.get("task_type") if request.method == "POST" else None

    # Handle get_device_uptime separately as it doesn't have structured output
    if task_type == "get_device_uptime":
        try:
            if selected_devices:
                subset = nr.filter(F(name__in=selected_devices))
            else:
                subset = nr

            result = subset.run(task=TASK_MAP[task_type])
            execution_output = {}

            for host, task_result in result.items():
                output = (
                    task_result.result
                    if task_result.failed is False
                    else str(task_result.exception)
                )
                status = "failure" if task_result.failed else "success"
                execution_output[host] = {"output": output, "status": status}

                TaskLog.objects.create(
                    device_name=host,
                    task_type=task_type,
                    output=output,
                    status=status,
                    user=request.user,
                )
        except Exception as e:
            error_message = str(e)
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
    """Render the dashboard page with data."""
    # Get device count
    device_count = NetworkDevice.objects.count()

    # Get task status (success rate and failed count)
    total_tasks = TaskLog.objects.filter(user=request.user).count()
    successful_tasks = TaskLog.objects.filter(
        user=request.user, status="success"
    ).count()
    failed_tasks_count = TaskLog.objects.filter(
        user=request.user, status="failure"
    ).count()
    task_success_rate = (successful_tasks / total_tasks * 100) if total_tasks > 0 else 0
    task_failure_rate = (
        (failed_tasks_count / total_tasks * 100) if total_tasks > 0 else 0
    )

    # Get last successful backup time (assuming 'save_config' is the backup task)
    last_backup_log = (
        TaskLog.objects.filter(
            user=request.user, task_type="save_config", status="success"
        )
        .order_by("-timestamp")
        .first()
    )
    last_backup_time = last_backup_log.timestamp if last_backup_log else "N/A"

    context = {
        "device_count": device_count,
        "task_success_rate": round(task_success_rate, 2),  # Round to 2 decimal places
        "failed_tasks_count": failed_tasks_count,  # Keep count for now, might be useful
        "task_failure_rate": round(task_failure_rate, 2),  # Round to 2 decimal places
        # Placeholders for Uptime as data is not directly available
        "average_uptime": "N/A",
        "last_backup_time": last_backup_time,
    }

    # Calculate average uptime
    total_uptime = 0
    device_count_with_uptime = 0
    for device in NetworkDevice.objects.all():
        try:
            last_uptime = (
                DeviceUptime.objects.filter(device=device)
                .order_by("-timestamp")
                .first()
            )
            if last_uptime:
                total_uptime += last_uptime.uptime_seconds
                device_count_with_uptime += 1
        except DeviceUptime.DoesNotExist:
            pass

    average_uptime = (
        total_uptime / device_count_with_uptime if device_count_with_uptime else 0
    )
    context["average_uptime"] = round(average_uptime / (3600), 2)  # in hours

    return render(request, "dashboard.html", context)
