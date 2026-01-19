import yaml
from pathlib import Path


def load_device_config(path="config/devices.yaml"):
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"{path} not found")

    with open(path, "r") as f:
        return yaml.safe_load(f)


def get_enabled_sensor_ids(cfg):
    sensors = cfg.get("sensors", {})
    enabled_ids = []

    for group in sensors.values():
        for sensor in group:
            if sensor.get("enabled", True):
                enabled_ids.append(sensor["id"])

    return enabled_ids
