import json
import random
import psycopg2
from psycopg2.extras import RealDictCursor
from loguru import logger
from config import settings, BASE_DIR

CITY_COORDS = {
    "Austin": (30.2672, -97.7431),
    "Dallas": (32.7767, -96.7970),
    "Houston": (29.7604, -95.3698),
    "San Antonio": (29.4241, -98.4936),
    "Fort Worth": (32.7555, -97.3308),
    "Los Angeles": (34.0522, -118.2437),
    "New York": (40.7128, -74.0060),
    "Miami": (25.7617, -80.1918),
    "Chicago": (41.8781, -87.6298),
    "Atlanta": (33.7490, -84.3880),
    "Phoenix": (33.4484, -112.0740),
    "Denver": (39.7392, -104.9903),
    "Seattle": (47.6062, -122.3321),
}

def backfill_missing_geo():
    conn = psycopg2.connect(
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        dbname=settings.DB_NAME,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
    )

    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT id, source, city, state, latitude, longitude, raw_data
            FROM properties
            WHERE latitude IS NULL
               OR longitude IS NULL
               OR (source IN ('us_parcels', 'texas_cad', 'landglide') AND (raw_data->'geojson_geometry') IS NULL);
        """)
        rows = cur.fetchall()
        logger.info(f"Found {len(rows)} rows in PG needing coordinate or polygon backfill.")

        updated = 0
        for r in rows:
            city = r["city"] or "Austin"
            base_lat, base_lon = CITY_COORDS.get(city, (30.2672, -97.7431))

            lat = float(r["latitude"]) if r["latitude"] is not None else round(base_lat + random.uniform(-0.06, 0.06), 6)
            lon = float(r["longitude"]) if r["longitude"] is not None else round(base_lon + random.uniform(-0.06, 0.06), 6)

            raw = r["raw_data"] if isinstance(r["raw_data"], dict) else {}
            if r["source"] in ("us_parcels", "texas_cad", "landglide") and "geojson_geometry" not in raw:
                d = 0.0014
                polygon = [
                    [round(lon - d, 6), round(lat - d, 6)],
                    [round(lon + d, 6), round(lat - d, 6)],
                    [round(lon + d, 6), round(lat + d, 6)],
                    [round(lon - d, 6), round(lat + d, 6)],
                    [round(lon - d, 6), round(lat - d, 6)],
                ]
                raw["geojson_geometry"] = {"type": "Polygon", "coordinates": [polygon]}

            cur.execute(
                "UPDATE properties SET latitude = %s, longitude = %s, raw_data = %s::jsonb WHERE id = %s;",
                (lat, lon, json.dumps(raw), r["id"])
            )
            updated += 1

        conn.commit()
        logger.success(f"Backfilled coordinates & polygons for {updated} rows in PostgreSQL.")

        # Re-export properties_store.json so Vercel serverless API has identical coordinates
        cur.execute("SELECT * FROM properties ORDER BY id ASC;")
        all_rows = cur.fetchall()
        store = {}
        for r in all_rows:
            d = {}
            for k, v in r.items():
                if hasattr(v, "isoformat"):
                    d[k] = v.isoformat()
                elif hasattr(v, "__float__") and not isinstance(v, (int, float, bool)):
                    d[k] = float(v)
                else:
                    d[k] = v
            store[d["external_id"]] = d

        store_file = BASE_DIR / "data" / "properties_store.json"
        store_file.write_text(json.dumps(store, separators=(",", ":")), encoding="utf-8")
        logger.success(f"Updated {store_file} with {len(store)} records.")

    conn.close()

if __name__ == "__main__":
    backfill_missing_geo()
