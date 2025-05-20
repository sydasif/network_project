# core/tasks.py
from nornir.core.task import Result, Task
from nornir_netmiko.tasks import netmiko_send_command


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
