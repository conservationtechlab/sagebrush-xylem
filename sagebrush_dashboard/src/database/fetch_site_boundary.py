import json
import psycopg2
from pathlib import Path

BASE_DIR = Path(__file__).parent

def get_site_boundary_feature(site_code: str) -> dict | None:
    """Return GeoJSON Feature for the site's boundary polygon."""
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

    q = """
    SELECT ST_AsGeoJSON(ST_SetSRID(geom, 4326)) AS geom_geojson
    FROM public.site
    WHERE site_code = %s
    LIMIT 1;
    """

    cur = conn.cursor()
    cur.execute(q, (site_code,))
    row = cur.fetchone()
    cur.close()
    conn.close()

    if not row or not row[0]:
        return None

    geom = json.loads(row[0])

    return {
        "type": "Feature",
        "properties": {"site_code": site_code},
        "geometry": geom,
    }
