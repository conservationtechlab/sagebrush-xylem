import json
import psycopg2
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

BASE_DIR = Path(__file__).parent


def normalize_id(s: str) -> str:
    return (s or "").strip().upper()


def _get_conn():
    with open(BASE_DIR / "db_credentials.json") as f:
        creds = json.load(f)
    return psycopg2.connect(
        host=creds["host"],
        port=creds["port"],
        dbname=creds["database"],
        user=creds["user"],
        password=creds["password"],
        sslmode="prefer",
    )


def get_acoustic_snapshot_at(target_timestamp) -> Dict[str, Dict[str, Any]]:
    """
    Return the most recent acoustic detection per device, at or before target_timestamp.
    """
    conn = _get_conn()

    query = """
    SELECT DISTINCT ON (UPPER(TRIM(d.device_id)))
        d.device_id,
        e.start_time,
        o.class_id,
        o.confidence,
        e.filepath
    FROM public.occurrence o
    JOIN public.event e ON o.event_id = e.event_id
    JOIN public.deployment d ON e.deployment_id = d.deployment_id
    WHERE e.start_time <= %s
    ORDER BY UPPER(TRIM(d.device_id)), e.start_time DESC;
    """

    cur = conn.cursor()
    cur.execute(query, (target_timestamp,))
    rows = cur.fetchall()
    cur.close()
    conn.close()

    data: Dict[str, Dict[str, Any]] = {}

    for device_id, start_time, class_id, confidence, filepath in rows:
        norm_id = normalize_id(device_id)
        data[norm_id] = {
            "device_id": norm_id,
            "recorded_at": str(start_time) if start_time is not None else None,
            "species": class_id,
            "confidence": float(confidence) if confidence is not None else None,
            "filepath": filepath,
        }

    return data


def get_acoustic_time_series(
    start_timestamp,
    end_timestamp,
) -> List[Dict[str, Any]]:
    """
    Return all acoustic detections between start_timestamp and end_timestamp.
    Each row contains: device_id, start_time, species, confidence.

    Used to populate the Bird Call Timeline chart in the sidebar.
    """
    conn = _get_conn()

    query = """
    SELECT
        d.device_id,
        e.start_time,
        o.class_id,
        o.confidence
    FROM public.occurrence o
    JOIN public.event e ON o.event_id = e.event_id
    JOIN public.deployment d ON e.deployment_id = d.deployment_id
    WHERE e.start_time >= %s
      AND e.start_time <= %s
      AND o.class_id IS NOT NULL
    ORDER BY e.start_time ASC;
    """

    cur = conn.cursor()
    cur.execute(query, (start_timestamp, end_timestamp))
    rows = cur.fetchall()
    cur.close()
    conn.close()

    result: List[Dict[str, Any]] = []

    for device_id, start_time, class_id, confidence in rows:
        result.append({
            "device_id": normalize_id(device_id),
            "start_time": start_time,  # keep as datetime for aggregation
            "species": class_id,
            "confidence": float(confidence) if confidence is not None else None,
        })

    print(f"[acoustic_ts] loaded {len(result)} detections from {start_timestamp} to {end_timestamp}")
    return result


if __name__ == "__main__":
    from datetime import timedelta

    now = datetime.now()
    snap = get_acoustic_snapshot_at(now)
    print(f"Snapshot: {len(snap)} rows")
    for k, v in list(snap.items())[:3]:
        print(k, v)

    print()
    ts = get_acoustic_time_series(now - timedelta(days=7), now)
    print(f"Time series: {len(ts)} detections")
    for r in ts[:3]:
        print(r)
