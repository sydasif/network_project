from django.core.management.base import BaseCommand
import yaml
from network.models import NetworkDevice
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Synchronize network devices from hosts.yaml to database"

    def handle(self, *args, **options):
        base_dir = Path(__file__).resolve().parent.parent.parent.parent
        hosts_file = base_dir / "hosts.yaml"

        try:
            with open(hosts_file) as f:
                hosts = yaml.safe_load(f)

            devices_added = 0
            devices_updated = 0

            for name, data in hosts.items():
                try:
                    device, created = NetworkDevice.objects.update_or_create(
                        name=name,
                        defaults={
                            "hostname": data["hostname"],
                            "platform": data["platform"],
                            "username": data["username"],
                            "password": data["password"],
                        },
                    )

                    if created:
                        devices_added += 1
                        logger.info(f"Added device {name}")
                        self.stdout.write(self.style.SUCCESS(f"Added device {name}"))
                    else:
                        devices_updated += 1
                        logger.info(f"Updated device {name}")
                        self.stdout.write(self.style.SUCCESS(f"Updated device {name}"))
                except KeyError as e:
                    logger.error(f"Missing required field {e} for device {name}")
                    self.stdout.write(
                        self.style.ERROR(
                            f"Missing required field {e} for device {name}"
                        )
                    )
                except Exception as e:
                    logger.error(f"Error processing device {name}: {e}")
                    self.stdout.write(
                        self.style.ERROR(f"Error processing device {name}: {e}")
                    )

            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully synchronized devices. "
                    f"Added: {devices_added}, Updated: {devices_updated}"
                )
            )

        except FileNotFoundError:
            logger.error(f"hosts.yaml not found at {hosts_file}")
            self.stdout.write(self.style.ERROR(f"hosts.yaml not found at {hosts_file}"))
        except Exception as e:
            logger.error(f"Error synchronizing devices: {e}")
            self.stdout.write(
                self.style.ERROR(f"Error synchronizing devices: {str(e)}")
            )
