from datetime import datetime, timedelta
from statistics import mean
from typing import Any, Dict, List, Tuple


def flatten_items(cfg_dict: Dict[str, Any]) -> List[Dict[str, Any]]:
    flat: List[Dict[str, Any]] = []
    for category_key in ("networking", "sensors"):
        groups = cfg_dict.get(category_key, {}) or {}
        for subgroup, items in groups.items():
            for item in (items or []):
                flat.append({
                    "category": category_key,
                    "subgroup": str(subgroup),
                    "id": str(item.get("id", "")),
                    "name": str(item.get("name", item.get("id", ""))),
                    "lat": item.get("lat"),
                    "lon": item.get("lon"),
                    "icon": item.get("icon"),
                    "enabled": bool(item.get("enabled", True)),
                })
    return flat


def make_time_range():
    end = datetime.now()
    start = end - timedelta(days=1)
    times = []
    t = start
    while t <= end:
        times.append(t)
        t += timedelta(minutes=30)
    return times


def fmt(dt: datetime) -> str:
    return dt.strftime('%d %B %Y, %I:%M %p')


def compute_center(items):
    coords = [(i["lat"], i["lon"]) for i in items if i["lat"] and i["lon"]]
    if coords:
        return mean(a for a, _ in coords), mean(b for _, b in coords)
    return 33.095, -116.995
