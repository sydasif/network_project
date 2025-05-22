import logging
from django.core.management.base import BaseCommand
from core.nornir_init import init_nornir  # Using the common init_nornir function
from network.models import NetworkDevice
from core.tasks import get_device_uptime
from nornir.core.filter import F


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Collects uptime from network devices and saves it to the database."

    def add_arguments(self, parser):
        parser.add_argument(
            "--device",
            help="Collect uptime for a specific device by name",
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Initializing Nornir..."))
        nr = init_nornir()

        # Filter devices if specific device name provided
        devices = NetworkDevice.objects.all()
        if options["device"]:
            devices = devices.filter(name=options["device"])

        if not devices:
            self.stdout.write(
                self.style.WARNING("No matching network devices found in the database.")
            )
            return

        device_count = devices.count()
        self.stdout.write(
            self.style.SUCCESS(f"Collecting uptime from {device_count} device(s)...")
        )

        success_count = 0

        for device in devices:
            self.stdout.write(f"Processing {device.name} ({device.hostname})...")
            try:
                filtered_nr = nr.filter(F(name=device.name))

                if not filtered_nr.inventory.hosts:
                    logger.error(f"Device {device.name} not found in Nornir inventory")
                    self.stdout.write(
                        self.style.ERROR(
                            f"Device {device.name} not found in Nornir inventory"
                        )
                    )
                    continue

                result = filtered_nr.run(task=get_device_uptime)

                for host, task_result in result.items():
                    if task_result.failed:
                        logger.error(
                            f"Failed to collect uptime from {host}: {task_result.exception}"
                        )
                        self.stdout.write(
                            self.style.ERROR(
                                f"Failed to collect uptime from {host}: {task_result.exception}"
                            )
                        )
                    else:
                        success_count += 1
                        logger.info(f"Successfully collected uptime from {host}")
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"Successfully collected uptime from {host}"
                            )
                        )

            except Exception as e:
                logger.exception(f"Error processing device {device.name}")
                self.stdout.write(
                    self.style.ERROR(f"Error processing device {device.name}: {str(e)}")
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Uptime collection completed: {success_count}/{device_count} devices successful"
            )
        )
