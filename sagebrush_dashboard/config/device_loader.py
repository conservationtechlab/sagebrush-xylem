import yaml
from pathlib import Path

# Map YAML group names → icon files
ICON_MAP = {
    # Networking
    "lora_gateways": "assets/icons/lora_gateway.png",
    "nanobeams": "assets/icons/nanobeam.png",

    # Sensors
    "SageCam": "assets/icons/sagecam.png",
    "SageMic": "assets/icons/sagemic.png",
    "TempSensors": "assets/icons/temperature.png",
}

DEFAULT_ICON = "assets/icons/zoo.jpg"


def load_device_config(path="config/devices.yaml"):
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"{path} not found")

    with open(path, "r") as f:
        return yaml.safe_load(f)


def get_enabled_devices_with_icons(cfg):
    enabled_devices = []

    # Networking
    for group_name, devices in cfg.get("networking", {}).items():
        for device in devices:
            if device.get("enabled", True):
                device_copy = device.copy()
                device_copy["group"] = group_name
                device_copy["icon_url"] = ICON_MAP.get(group_name, DEFAULT_ICON)
                enabled_devices.append(device_copy)

    # Sensors
    for group_name, devices in cfg.get("sensors", {}).items():
        for device in devices:
            if device.get("enabled", True):
                device_copy = device.copy()
                device_copy["group"] = group_name
                device_copy["icon_url"] = ICON_MAP.get(group_name, DEFAULT_ICON)
                enabled_devices.append(device_copy)

    return enabled_devices
