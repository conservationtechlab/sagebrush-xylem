import json
import psycopg2
from pathlib import Path

BASE_DIR = Path(__file__).parent


def normalize_id(s: str) -> str:
    return (s or "").strip().upper()


def get_latest_sensor_data():
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
    SELECT
        device_name,
        device_id,
        recorded_at,
        humidity,
        bat_v,
        temperature,
        latitude,
        longitude
    FROM public.v_field_sensor_lat_long_last_dt;
    """

    cur = conn.cursor()
    cur.execute(query)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    data = {}

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
    latest = get_latest_sensor_data()
    for k, v in latest.items():
        print(k, v)
