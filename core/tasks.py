from nornir_netmiko.tasks import netmiko_send_command, netmiko_save_config

def show_ip_interface_brief(task):
    return task.run(task=netmiko_send_command, command_string="show ip interface brief")

def save_running_config(task):
    return task.run(task=netmiko_save_config)
