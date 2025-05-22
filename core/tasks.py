# core/tasks.py
from nornir.core.task import Result, Task
from nornir_netmiko.tasks import netmiko_send_command
from network.models import NetworkDevice, DeviceUptime


def show_ip(task: Task) -> Result:
    result = task.run(
        task=netmiko_send_command, command_string="show ip interface brief"
    )
    return Result(host=task.host, result=result.result)


def save_config(task: Task) -> Result:
    result = task.run(
        task=netmiko_send_command, command_string="copy running-config startup-config"
    )
    return Result(host=task.host, result=result.result)


def get_device_uptime(task: Task) -> Result:
    """
    Collect device uptime using netmiko and TextFSM.
    """
    try:
        result = task.run(
            task=netmiko_send_command, command_string="show version", use_textfsm=True
        )

        # Extract uptime from structured output
        show_ver = result[0].result

        if show_ver and len(show_ver) > 0 and "uptime" in show_ver[0]:
            uptime_string = show_ver[0]["uptime"]
            # Convert uptime string to seconds (example: 1 week, 2 days, 3 hours, 4 minutes)
            # This is a placeholder, actual parsing logic needed here
            uptime_seconds = 3600 * 24 * 7  # 1 week
        else:
            uptime_seconds = 0

        device = NetworkDevice.objects.get(name=task.host.name)
        DeviceUptime.objects.create(device=device, uptime_seconds=uptime_seconds)

        return Result(
            host=task.host, result=f"Uptime collected: {uptime_seconds} seconds"
        )

    except Exception as e:
        return Result(
            host=task.host, result=f"Error collecting uptime: {e}", failed=True
        )
