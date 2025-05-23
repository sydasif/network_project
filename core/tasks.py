import logging
from nornir.core.task import Result, Task
from nornir_netmiko.tasks import netmiko_send_command
from network.models import NetworkDevice

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


def run_custom_command(task: Task, command: str) -> Result:
    """Execute a custom command on device."""
    try:
        result = task.run(task=netmiko_send_command, command_string=command)
        logger.info(f"Successfully executed command '{command}' on {task.host.name}")
        return Result(host=task.host, result=result.result)
    except Exception as e:
        logger.error(
            f"Error executing command '{command}' on {task.host.name}: {str(e)}"
        )
        return Result(host=task.host, result=str(e), failed=True)
