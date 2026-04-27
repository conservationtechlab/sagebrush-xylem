import json
import psycopg2
from pathlib import Path
from typing import Dict, Any

BASE_DIR = Path(__file__).parent


def normalize_id(s: str) -> str:
    return (s or "").strip().upper()


def get_sensor_snapshot_at(target_timestamp) -> Dict[str, Dict[str, Any]]:
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
    SELECT DISTINCT ON (UPPER(TRIM(device_id)))
        device_name,
        device_id,
        recorded_at,
        humidity,
        bat_v,
        temperature,
        latitude,
        longitude
    FROM public.v_field_sensor_lat_long
    WHERE recorded_at <= %s
    ORDER BY UPPER(TRIM(device_id)), recorded_at DESC;
    """

    cur = conn.cursor()
    cur.execute(query, (target_timestamp,))
    rows = cur.fetchall()
    cur.close()
    conn.close()

    data: Dict[str, Dict[str, Any]] = {}

    for row in rows:
        device_name, device_id, recorded_at, humidity, bat_v, temperature, latitude, longitude = row

        norm_id = normalize_id(device_id)

        data[norm_id] = {
            "device_name": device_name,
            "device_id": norm_id,
            "recorded_at": str(recorded_at) if recorded_at is not None else None,
            "humidity": float(humidity) if humidity is not None else None,
            "bat_v": float(bat_v) if bat_v is not None else None,
            "temperature": float(temperature) if temperature is not None else None,
            "latitude": float(latitude) if latitude is not None else None,
            "longitude": float(longitude) if longitude is not None else None,
        }

    return data


if __name__ == "__main__":
    from datetime import datetime

    print("starting snapshot test...")
    snapshot = get_sensor_snapshot_at(datetime.now())
    print(f"loaded {len(snapshot)} devices")

    for k, v in list(snapshot.items())[:5]:
        print(k, v)
