# views.py
from django.shortcuts import redirect, render

from core.nornir_init import init_nornir  # Your Nornir loader
from core.tasks import save_config, show_ip  # Your task handlers

from .forms import TaskForm
from .models import TaskLog

TASK_MAP = {
    "show_ip": show_ip,
    "save_config": save_config,
}


def task_view(request):
    nr = init_nornir()
    device_choices = [(h, h) for h in nr.inventory.hosts.keys()]

    if request.method == "POST":
        form = TaskForm(request.POST, device_choices=device_choices)
        if form.is_valid():
            task_type = form.cleaned_data["task_type"]
            selected_devices = form.cleaned_data["devices"]
            task_func = TASK_MAP[task_type]

            if selected_devices:
                if len(selected_devices) == 1:
                    # Filter by exact host name if only one device is selected
                    subset = nr.filter(name=selected_devices[0])
                else:
                    # Use name__in filter for multiple selected devices
                    subset = nr.filter(name__in=selected_devices)
            else:
                # Use full inventory if no devices are selected
                subset = nr

            try:
                result = subset.run(task=task_func)

                for host, task_result in result.items():
                    TaskLog.objects.create(
                        device_name=host,
                        task_type=task_type,
                        output=(
                            task_result.result
                            if task_result.failed is False
                            else str(task_result.exception)
                        ),
                        status="failure" if task_result.failed else "success",
                    )
            except Exception as e:
                print(f"An error occurred during Nornir task execution: {e}")
                # Optionally, you could log this error to the database as well
                # TaskLog.objects.create(...)

            return redirect("task_view")
        else:
            pass  # Form is not valid, handle errors in template if needed
    else:
        form = TaskForm(device_choices=device_choices)

    logs = TaskLog.objects.order_by("-timestamp")[:10]
    return render(request, "task_form.html", {"form": form, "logs": logs})
