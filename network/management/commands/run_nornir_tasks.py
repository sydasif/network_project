from django.core.management.base import BaseCommand

from core.nornir_init import init_nornir
from core.tasks import save_running_config, show_ip_interface_brief
from network.models import TaskLog


class Command(BaseCommand):
    help = "Run Nornir tasks and log output"

    def handle(self, *args, **kwargs):
        nr = init_nornir()

        for task_func in [show_ip_interface_brief, save_running_config]:
            result = nr.run(task=task_func)
            for host, multi_result in result.items():
                for r in multi_result:
                    TaskLog.objects.create(
                        device_name=host,
                        task_name=task_func.__name__,
                        command=r.name,
                        output=r.result,
                    )
                    print(f"{host} => {r.name}:\n{r.result}\n")
