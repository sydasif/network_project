# core/tasks.py
from nornir.core.task import Result, Task


def show_ip(task: Task) -> Result:
    output = task.run(task=task.run, name="Show IP", command="show ip interface brief")
    return Result(host=task.host, result=output[0].result)


def save_config(task: Task) -> Result:
    output = task.run(
        task=task.run, name="Save Config", command="copy running-config startup-config"
    )
    return Result(host=task.host, result=output[0].result)
