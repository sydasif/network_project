from pathlib import Path

import yaml
from nornir import InitNornir
from nornir.core.inventory import Defaults, Host, Inventory
from nornir.core.plugins.connections import ConnectionPluginRegister
from nornir_netmiko.connections import Netmiko


def load_inventory_from_yaml(file_path="device_config.yaml"):
    with open(file_path) as f:
        raw_inventory = yaml.safe_load(f)

    hosts = {
        name: Host(
            name=name,
            hostname=data["hostname"],
            platform=data["platform"],
            username=data["username"],
            password=data["password"],
            connection_options={
                "netmiko": {
                    "extras": {
                        "secret": data.get("enable_password", ""),
                    }
                }
            },
        )
        for name, data in raw_inventory.items()
    }

    return Inventory(hosts=hosts, groups={}, defaults=Defaults())


def init_nornir():
    # Register Netmiko plugin
    ConnectionPluginRegister.register("netmiko", Netmiko)

    # Get the base directory of the project
    BASE_DIR = Path(__file__).resolve().parent.parent

    return InitNornir(
        inventory={
            "plugin": "SimpleInventory",
            "options": {
                "host_file": str(BASE_DIR / "device_config.yaml"),
                "group_file": str(BASE_DIR / "groups.yaml"),
            },
        },
        runner={
            "plugin": "threaded",
            "options": {
                "num_workers": 10,
            },
        },
    )
