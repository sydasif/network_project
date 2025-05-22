import logging
from nornir.core.task import Result, Task
from nornir_netmiko.tasks import netmiko_send_command
from network.models import NetworkDevice, DeviceUptime

logger = logging.getLogger(__name__)


def show_ip(task: Task) -> Result:
    """Execute 'show ip interface brief' command on device."""
    try:
        result = task.run(
            task=netmiko_send_command, command_string="show ip interface brief"
        )
        logger.info(f"Successfully retrieved IP interface info from {task.host.name}")
        return Result(host=task.host, result=result.result)
    except Exception as e:
        logger.error(f"Error getting IP interface info from {task.host.name}: {str(e)}")
        return Result(host=task.host, result=str(e), failed=True)


def save_config(task: Task) -> Result:
    """Save running configuration to startup config."""
    try:
        result = task.run(
            task=netmiko_send_command,
            command_string="copy running-config startup-config",
        )
        logger.info(f"Successfully saved config on {task.host.name}")
        return Result(host=task.host, result=result.result)
    except Exception as e:
        logger.error(f"Error saving config on {task.host.name}: {str(e)}")
        return Result(host=task.host, result=str(e), failed=True)


def parse_uptime_string(uptime_string: str) -> int:
    """Convert uptime string to seconds."""
    import re
    from datetime import timedelta

    # Initialize values
    weeks = days = hours = minutes = 0

    # Extract values using regex
    if match := re.search(r"(\d+)\s+week", uptime_string):
        weeks = int(match.group(1))
    if match := re.search(r"(\d+)\s+day", uptime_string):
        days = int(match.group(1))
    if match := re.search(r"(\d+)\s+hour", uptime_string):
        hours = int(match.group(1))
    if match := re.search(r"(\d+)\s+minute", uptime_string):
        minutes = int(match.group(1))

    # Calculate total seconds
    td = timedelta(weeks=weeks, days=days, hours=hours, minutes=minutes)
    return int(td.total_seconds())


def get_device_uptime(task: Task) -> Result:
    """Collect device uptime using netmiko and TextFSM."""
    try:
        result = task.run(
            task=netmiko_send_command, command_string="show version", use_textfsm=True
        )

        if not result[0].failed:
            show_ver = result[0].result

            if show_ver and len(show_ver) > 0 and "uptime" in show_ver[0]:
                uptime_string = show_ver[0]["uptime"]
                uptime_seconds = parse_uptime_string(uptime_string)

                try:
                    # Get or create the device from the inventory data
                    device, created = NetworkDevice.objects.get_or_create(
                        name=task.host.name,
                        defaults={
                            "hostname": task.host.hostname,
                            "platform": task.host.platform,
                            "username": task.host.username,
                            "password": task.host.password,
                        },
                    )

                    if created:
                        logger.info(f"Created new device record for {task.host.name}")

                    DeviceUptime.objects.create(
                        device=device, uptime_seconds=uptime_seconds
                    )

                    logger.info(
                        f"Successfully collected and stored uptime for {task.host.name}"
                    )
                    return Result(
                        host=task.host,
                        result=f"Uptime collected: {uptime_seconds} seconds ({uptime_string})",
                    )

                except Exception as e:
                    logger.error(f"Error storing uptime for {task.host.name}: {str(e)}")
                    return Result(
                        host=task.host,
                        result=f"Error storing uptime: {str(e)}",
                        failed=True,
                    )
            else:
                msg = "Could not parse uptime from show version output"
                logger.error(f"{msg} for {task.host.name}")
                return Result(host=task.host, result=msg, failed=True)
        else:
            return Result(
                host=task.host,
                result="Failed to execute show version command",
                failed=True,
            )

    except Exception as e:
        logger.error(f"Error collecting uptime from {task.host.name}: {str(e)}")
        return Result(
            host=task.host, result=f"Error collecting uptime: {str(e)}", failed=True
        )
