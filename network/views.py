from django.core.paginator import Paginator
from django.shortcuts import render
from nornir.core.filter import F
from core.nornir_init import init_nornir
from core.tasks import save_config, show_ip
from .forms import TaskForm
from django.contrib.auth.decorators import login_required
from .models import TaskLog


def home_view(request):
    """Render the home page with navigation links."""
    return render(request, "home.html")


TASK_MAP = {
    "show_ip": show_ip,
    "save_config": save_config,
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
