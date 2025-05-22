import logging
from django.core.management.base import BaseCommand
from core.nornir_init import init_nornir
from core.tasks import save_config, show_ip
from network.models import TaskLog


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Run Nornir tasks and log output"

    def add_arguments(self, parser):
        parser.add_argument(
            "--tasks",
            nargs="+",
            type=str,
            help="Specify tasks to run (show_ip, save_config)",
            choices=["show_ip", "save_config"],
            default=["show_ip", "save_config"],
        )

    def process_task_result(self, host, task_result, task_name):
        """Process and log an individual task result."""
        if task_result.failed:
            status = "failure"
            output = (
                str(task_result.exception)
                if task_result.exception
                else "Task failed without exception"
            )
        else:
            status = "success"
            output = task_result.result

        # Create DB log entry
        TaskLog.objects.create(
            device_name=host,
            task_type=task_name,
            output=output,
            status=status,
        )

        # Log to console and file
        msg = f"{host} => {task_name}:\n{output}\n"
        if status == "success":
            logger.info(f"Task {task_name} succeeded on {host}")
            self.stdout.write(self.style.SUCCESS(msg))
        else:
            logger.error(f"Task {task_name} failed on {host}: {output}")
            self.stdout.write(self.style.ERROR(msg))

    def handle(self, *args, **options):
        try:
            nr = init_nornir()
            task_map = {"show_ip": show_ip, "save_config": save_config}

            requested_tasks = options["tasks"]

            for task_name in requested_tasks:
                task_func = task_map[task_name]
                self.stdout.write(f"\nExecuting {task_name}...")
                try:
                    result = nr.run(task=task_func)
                    for host, host_result in result.items():
                        if isinstance(host_result, list):
                            for r in host_result:
                                self.process_task_result(host, r, task_func.__name__)
                        else:
                            self.process_task_result(
                                host, host_result, task_func.__name__
                            )

                except Exception as e:
                    logger.exception(f"Error executing {task_name}")
                    self.stdout.write(
                        self.style.ERROR(f"Error executing {task_name}: {str(e)}")
                    )

            self.stdout.write(self.style.SUCCESS("\nAll tasks completed"))

        except Exception as e:
            logger.exception("Error in command execution")
            self.stdout.write(self.style.ERROR(f"Error in command execution: {str(e)}"))
