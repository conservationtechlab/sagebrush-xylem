import json
import psycopg2
from pathlib import Path

BASE_DIR = Path(__file__).parent

# ----------------------------
# CONFIG
# ----------------------------
FILTERS = {
    "active_only": True,
    "exclude_sites": {"otay"},
    "require_coords": True,
}

CATEGORY_RULES = {
    "Temperature Sensors": {
        "prefixes": ["ridge_gateway_temp", "boa_hills_temp"],
        "treat_long_alnum_as_temp": True,
        "min_alnum_len": 10,
    },
    "scrubmic": {
        "exact_ids": {"LAB_DETECTO"},
    },
    "SageMic": {
        "exact_ids": {"BIRDNET"},
    },
}


def normalize_id(s: str) -> str:
    return (s or "").strip().upper()


def get_devices():
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

    where_clauses = []

    if FILTERS["require_coords"]:
        where_clauses.append("lat IS NOT NULL AND lon IS NOT NULL")

    if FILTERS["active_only"]:
        where_clauses.append("end_date IS NULL")

    if FILTERS["exclude_sites"]:
        excluded = ", ".join([f"'{s.lower()}'" for s in FILTERS["exclude_sites"]])
        where_clauses.append(f"LOWER(site) NOT IN ({excluded})")

    where_sql = ""
    if where_clauses:
        where_sql = "WHERE " + " AND ".join(where_clauses)

    query = f"""
    SELECT device_id, lat, lon
    FROM public.deployment
    {where_sql};
    """

    cur = conn.cursor()
    cur.execute(query)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    devices = []
    for device_id, lat, lon in rows:
        devices.append({
            "device_id": normalize_id(device_id),
            "lat": float(lat) if lat is not None else None,
            "lon": float(lon) if lon is not None else None,
        })

    return devices


def categorize_devices(devices):
    layers = {name: [] for name in CATEGORY_RULES.keys()}

    for d in devices:
        did = d["device_id"]
        matched = False

        temp = CATEGORY_RULES["Temperature Sensors"]

        # Temperature Sensors
        if any(did.startswith(p.upper()) for p in temp["prefixes"]):
            layers["Temperature Sensors"].append(d)
            matched = True
        elif temp["treat_long_alnum_as_temp"] and did.isalnum() and len(did) >= temp["min_alnum_len"]:
            layers["Temperature Sensors"].append(d)
            matched = True

        # scrubmic
        if not matched and did in {x.upper() for x in CATEGORY_RULES["scrubmic"]["exact_ids"]}:
            layers["scrubmic"].append(d)
            matched = True

        # SageMic exact match
        if not matched and did in {x.upper() for x in CATEGORY_RULES["SageMic"]["exact_ids"]}:
            layers["SageMic"].append(d)
            matched = True

        # DEFAULT EVERYTHING ELSE → SAGEMIC
        if not matched:
            layers["SageMic"].append(d)

    return layers


if __name__ == "__main__":
    devices = get_devices()
    layers = categorize_devices(devices)

    print("\nCategorized Device Layers:\n")

    for category, items in layers.items():
        print(f"{category}:")
        for device in items:
            print(f"  - {device['device_id']}")
        print()


