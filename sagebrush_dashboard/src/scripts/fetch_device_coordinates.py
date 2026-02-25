import json
import psycopg2
from pathlib import Path

BASE_DIR = Path(__file__).parent

# Load DB credentials
with open(BASE_DIR / "db_credentials.json") as f:
    creds = json.load(f)

# Connect to PostgreSQL
conn = psycopg2.connect(
    host=creds["host"],
    port=creds["port"],
    dbname=creds["database"],
    user=creds["user"],
    password=creds["password"]
)

query = """
SELECT
    device_id,
    latitude,
    longitude
FROM v_field_sensor_lat_long_last_dt;
"""

cur = conn.cursor()
cur.execute(query)

devices = []
for device_id, lat, lon in cur.fetchall():
    devices.append({
        "device_id": device_id,
        "lat": lat,
        "lon": lon
    })

cur.close()
conn.close()

# Write output JSON
output_path = BASE_DIR / "devices.json"
with open(output_path, "w") as f:
    json.dump(devices, f, indent=2)

print(f"Wrote {len(devices)} devices to {output_path}")
