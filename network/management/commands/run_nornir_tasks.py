from django.core.management.base import BaseCommand
from core.nornir_init import init_nornir
from core.tasks import save_config, show_ip
from network.models import TaskLog


class Command(BaseCommand):
    help = "Run Nornir tasks and log output"

    def handle(self, *args, **kwargs):
        nr = init_nornir()

        for task_func in [show_ip, save_config]:
            result = nr.run(task=task_func)
            for host, multi_result in result.items():
                for r in multi_result:
                    TaskLog.objects.create(
                        device_name=host,
                        task_type=task_func.__name__,
                        output=r.result,
                        status="success" if not r.failed else "failure",
                    )
                    self.stdout.write(
                        self.style.SUCCESS(f"{host} => {r.name}:\n{r.result}\n")
                        if not r.failed
                        else self.style.ERROR(f"{host} => {r.name}:\n{r.result}\n")
                    )
