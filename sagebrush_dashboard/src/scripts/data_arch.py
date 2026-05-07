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


def make_time_range(hours=24, step_minutes=30):
    end = datetime.now()
    start = end - timedelta(hours=hours)
    times = []
    current = start
    while current <= end:
        times.append(current)
        current += timedelta(minutes=step_minutes)
    return times


def fmt(dt: datetime) -> str:
    return dt.strftime('%m/%d/%Y %I:%M %p')


def compute_center(items):
    coords = [(i["lat"], i["lon"]) for i in items if i["lat"] and i["lon"]]
    if coords:
        return mean(a for a, _ in coords), mean(b for _, b in coords)
    return 33.095, -116.995


def aggregate_acoustic_timeseries(
    raw_rows: List[Dict[str, Any]],
    time_buckets: List[datetime],
) -> Dict[str, List]:
    """
    Given a list of acoustic detection rows (each with 'start_time' datetime and 'species'),
    and a list of datetime buckets (from make_time_range), return per-bucket counts.

    Also accepts sensor rows keyed in raw_rows as 'temperature' / 'humidity' for overlay.

    Returns:
        {
            'times': List[datetime],
            'counts': List[int],          # bird call count per bucket
            'avg_temp': List[float|None], # avg temperature per bucket
            'avg_humidity': List[float|None],
        }
    """
    if not time_buckets or len(time_buckets) < 2:
        return {'times': [], 'counts': [], 'avg_temp': [], 'avg_humidity': []}

    bucket_size = time_buckets[1] - time_buckets[0]

    counts: List[int] = [0] * len(time_buckets)
    temps: List[List[float]] = [[] for _ in time_buckets]
    humids: List[List[float]] = [[] for _ in time_buckets]

    for row in raw_rows:
        # Acoustic detections
        start_time = row.get('start_time') or row.get('recorded_at')
        if isinstance(start_time, str):
            try:
                start_time = datetime.fromisoformat(start_time)
            except Exception:
                start_time = None

        if start_time and row.get('species'):
            # Find the closest bucket
            idx = int((start_time - time_buckets[0]).total_seconds() / bucket_size.total_seconds())
            if 0 <= idx < len(time_buckets):
                counts[idx] += 1

        # Sensor overlays (temperature / humidity)
        temp = row.get('temperature')
        humidity = row.get('humidity')
        rec_at = row.get('sensor_recorded_at') or row.get('recorded_at')

        if isinstance(rec_at, str):
            try:
                rec_at = datetime.fromisoformat(rec_at)
            except Exception:
                rec_at = None

        if rec_at:
            idx = int((rec_at - time_buckets[0]).total_seconds() / bucket_size.total_seconds())
            if 0 <= idx < len(time_buckets):
                if temp is not None:
                    try:
                        temps[idx].append(float(temp))
                    except Exception:
                        pass
                if humidity is not None:
                    try:
                        humids[idx].append(float(humidity))
                    except Exception:
                        pass

    avg_temp = [round(mean(t), 1) if t else None for t in temps]
    avg_humidity = [round(mean(h), 1) if h else None for h in humids]

    return {
        'times': time_buckets,
        'counts': counts,
        'avg_temp': avg_temp,
        'avg_humidity': avg_humidity,
    }
