import json
import psycopg2
from pathlib import Path
from typing import Dict, Any

BASE_DIR = Path(__file__).parent


def normalize_id(s: str) -> str:
    return (s or "").strip().upper()


def get_acoustic_snapshot_at(target_timestamp) -> Dict[str, Dict[str, Any]]:
    with open(BASE_DIR / "db_credentials.json") as f:
        creds = json.load(f)

    conn = psycopg2.connect(
        host=creds["host"],
        port=creds["port"],
        dbname=creds["database"],
        user=creds["user"],
        password=creds["password"],
        sslmode="prefer",
    )

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


if __name__ == "__main__":
    from datetime import datetime

    snap = get_acoustic_snapshot_at(datetime.now())
    print(f"loaded {len(snap)} acoustic rows")
    for k, v in list(snap.items())[:5]:
        print(k, v)
