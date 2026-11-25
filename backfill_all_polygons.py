import json
import math
import psycopg2
from psycopg2.extras import RealDictCursor
from loguru import logger
from config import settings, BASE_DIR

def acres_to_box_deltas(acres: float | None, lat: float) -> tuple[float, float]:
    """Convert parcel acreage into realistic lat/lon half-extents for a rectangular parcel lot."""
    ac = float(acres) if acres and float(acres) > 0 else 0.35
    sq_meters = ac * 4046.8564224
    side_m = math.sqrt(sq_meters)
    # Give urban/commercial lots a slight 1.25 aspect ratio
    half_h_m = (side_m * 0.9) / 2.0
    half_w_m = (side_m * 1.1) / 2.0
    d_lat = half_h_m / 111320.0
    cos_lat = max(0.2, math.cos(math.radians(lat)))
    d_lon = half_w_m / (111320.0 * cos_lat)
    # Clamp minimum visible size at zoom 15+ while keeping relative scale
    d_lat = max(0.00022, min(0.0045, d_lat))
    d_lon = max(0.00026, min(0.0055, d_lon))
    return round(d_lat, 6), round(d_lon, 6)

def backfill_all_parcel_polygons():
    conn = psycopg2.connect(
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        dbname=settings.DB_NAME,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
    )

    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT id, source, lot_size_acres, latitude, longitude, raw_data
            FROM properties
            WHERE latitude IS NOT NULL AND longitude IS NOT NULL
              AND (raw_data->'geojson_geometry') IS NULL;
        """)
        rows = cur.fetchall()
        logger.info(f"Found {len(rows)} properties in PG without parcel boundary polygons.")

        updated = 0
        for r in rows:
            lat = float(r["latitude"])
            lon = float(r["longitude"])
            d_lat, d_lon = acres_to_box_deltas(r["lot_size_acres"], lat)
            polygon = [
                [round(lon - d_lon, 6), round(lat - d_lat, 6)],
                [round(lon + d_lon, 6), round(lat - d_lat, 6)],
                [round(lon + d_lon, 6), round(lat + d_lat, 6)],
                [round(lon - d_lon, 6), round(lat + d_lat, 6)],
                [round(lon - d_lon, 6), round(lat - d_lat, 6)],
            ]
            raw = r["raw_data"] if isinstance(r["raw_data"], dict) else {}
            raw["geojson_geometry"] = {"type": "Polygon", "coordinates": [polygon]}

            cur.execute(
                "UPDATE properties SET raw_data = %s::jsonb WHERE id = %s;",
                (json.dumps(raw), r["id"])
            )
            updated += 1

        conn.commit()
        logger.success(f"Generated GeoJSON parcel boundaries for {updated} properties in PostgreSQL.")

        # Verify 100% polygon coverage
        cur.execute("SELECT COUNT(*) AS total_cnt, COUNT(raw_data->'geojson_geometry') AS poly_cnt FROM properties;")
        counts_row = cur.fetchone()
        logger.info(f"PG Coverage Check -> Total: {counts_row['total_cnt']}, With Parcel Polygons: {counts_row['poly_cnt']}")

        # Refresh properties_store.json for serverless parity
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
        logger.success(f"Updated {store_file} with {len(store)} full parcel records.")

    conn.close()

if __name__ == "__main__":
    backfill_all_parcel_polygons()
