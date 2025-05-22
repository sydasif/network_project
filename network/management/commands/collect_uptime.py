from django.core.management.base import BaseCommand
from nornir import InitNornir
from network.models import NetworkDevice
from core.tasks import get_device_uptime
from nornir.core.filter import F


class Command(BaseCommand):
    help = "Collects uptime from network devices and saves it to the database."

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS("Initializing Nornir..."))
        nr = InitNornir(
            config_file="config.yaml"
        )  # Assuming config.yaml is in the project root

        devices = NetworkDevice.objects.all()
        if not devices:
            self.stdout.write(
                self.style.WARNING("No network devices found in the database.")
            )
            return

        self.stdout.write(
            self.style.SUCCESS(f"Collecting uptime from {devices.count()} devices...")
        )

        for device in devices:
            self.stdout.write(
                f"Attempting to collect uptime from {device.name} ({device.hostname})..."
            )
            try:
                # Filter Nornir inventory for the current device
                device_filter = F(name=device.name)
                filtered_nr = nr.filter(device_filter)

                if not filtered_nr.inventory.hosts:
                    self.stdout.write(
                        self.style.ERROR(
                            f"Device {device.name} not found in Nornir inventory."
                        )
                    )
                    continue

                # Run the get_device_uptime task
                result = filtered_nr.run(task=get_device_uptime)

                # Process results
                for host, task_result in result.items():
                    if task_result.failed:
                        self.stdout.write(
                            self.style.ERROR(
                                f"Failed to collect uptime from {host}: {task_result.exception}"
                            )
                        )
                    else:
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"Successfully collected uptime from {host}."
                            )
                        )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f"An unexpected error occurred for device {device.name}: {e}"
                    )
                )

        self.stdout.write(self.style.SUCCESS("Uptime collection process finished."))
