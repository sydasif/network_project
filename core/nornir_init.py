import logging
from pathlib import Path
import os
import yaml
from nornir import InitNornir
from nornir.core.inventory import Defaults, Host, Inventory
from nornir.core.plugins.connections import ConnectionPluginRegister
from nornir_netmiko.connections import Netmiko

logger = logging.getLogger(__name__)


def load_inventory_from_yaml(file_path="hosts.yaml"):
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
    """Initialize Nornir with proper configuration and logging."""
    # Register Netmiko plugin
    ConnectionPluginRegister.register("netmiko", Netmiko)

    # Get the base directory of the project
    BASE_DIR = Path(__file__).resolve().parent.parent

    # Set NET_TEXTFSM environment variable for template loading
    templates_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "ntc-templates", "templates"
    )
    if os.path.exists(templates_path):
        os.environ["NET_TEXTFSM"] = templates_path
    else:
        logger.info("Using default NET_TEXTFSM path from ntc_templates package")

    nr = InitNornir(
        inventory={
            "plugin": "SimpleInventory",
            "options": {
                "host_file": str(BASE_DIR / "hosts.yaml"),
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

    logger.info(f"Initialized Nornir with {len(nr.inventory.hosts)} hosts")
    return nr
