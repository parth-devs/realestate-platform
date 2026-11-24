import json
import psycopg2
from psycopg2.extras import execute_values, RealDictCursor
from pathlib import Path
from loguru import logger
from config import settings, BASE_DIR
from collectors.regrid import RegridCollector

def ingest_regrid_data():
    logger.info("Initializing Regrid (regrid.com) nationwide parcel ingestion...")

    # 1. Ensure regrid_parcels table exists in PostgreSQL
    conn = psycopg2.connect(
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        dbname=settings.DB_NAME,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
    )

    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS regrid_parcels (
                id BIGSERIAL PRIMARY KEY,
                parcel_apn VARCHAR(100) UNIQUE NOT NULL,
                ll_uuid UUID,
                fips VARCHAR(10),
                county VARCHAR(100),
                state VARCHAR(10) DEFAULT 'US',
                owner_name TEXT,
                owner_mailing_address TEXT,
                property_address TEXT,
                city VARCHAR(100),
                zip_code VARCHAR(20),
                use_code VARCHAR(150),
                zoning VARCHAR(100),
                lot_acres NUMERIC(10, 4),
                lot_sqft INTEGER,
                land_value NUMERIC(14, 2),
                improvement_value NUMERIC(14, 2),
                total_assessed_value NUMERIC(14, 2),
                annual_tax_amount NUMERIC(14, 2),
                last_sale_date DATE,
                last_sale_price NUMERIC(14, 2),
                legal_description TEXT,
                latitude NUMERIC(10, 7),
                longitude NUMERIC(10, 7),
                geojson_geometry JSONB,
                url TEXT,
                raw_json JSONB,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW()
            );

            CREATE INDEX IF NOT EXISTS idx_regrid_county ON regrid_parcels(county);
            CREATE INDEX IF NOT EXISTS idx_regrid_state ON regrid_parcels(state);
            CREATE INDEX IF NOT EXISTS idx_regrid_owner ON regrid_parcels(owner_name);
            CREATE INDEX IF NOT EXISTS idx_regrid_acres ON regrid_parcels(lot_acres);
        """)
        conn.commit()
    logger.success("PostgreSQL regrid_parcels table verified.")

    # 2. Ingest across target metros
    collector = RegridCollector()
    markets = [
        {"city": "Austin", "state": "TX"},
        {"city": "Dallas", "state": "TX"},
        {"city": "Houston", "state": "TX"},
        {"city": "San Antonio", "state": "TX"},
        {"city": "Los Angeles", "state": "CA"},
        {"city": "San Diego", "state": "CA"},
        {"city": "San Francisco", "state": "CA"},
        {"city": "New York", "state": "NY"},
        {"city": "Miami", "state": "FL"},
        {"city": "Orlando", "state": "FL"},
        {"city": "Tampa", "state": "FL"},
        {"city": "Atlanta", "state": "GA"},
        {"city": "Chicago", "state": "IL"},
        {"city": "Phoenix", "state": "AZ"},
        {"city": "Denver", "state": "CO"},
        {"city": "Seattle", "state": "WA"},
    ]

    all_records = []
    for m in markets:
        recs = collector.run(city=m["city"], state=m["state"], count=12)
        all_records.extend(recs)

    # Deduplicate in memory by external_id
    unique_map = {}
    for r in all_records:
        unique_map[r["external_id"]] = r
    all_records = list(unique_map.values())

    logger.info(f"Generated {len(all_records)} unique Regrid parcel records across {len(markets)} US markets.")

    # 3. Upsert into properties table
    with conn.cursor() as cur:
        prop_tuples = []
        for p in all_records:
            prop_tuples.append((
                p["source"],
                p["external_id"],
                p["title"],
                p["property_type"],
                p["listing_status"],
                p["price"],
                p["price_per_sqft"],
                p["lease_rate"],
                p["tax_assessed_value"],
                p["beds"],
                p["baths"],
                p["sqft"],
                p["lot_size_acres"],
                p["year_built"],
                p["address"],
                p["city"],
                p["county"],
                p["state"],
                p["zip_code"],
                p["latitude"],
                p["longitude"],
                p["parcel_id"],
                p["owner_name"],
                p["legal_description"],
                p["zoning"],
                p["url"],
                p["broker_name"],
                json.dumps(p["raw_data"])
            ))

        upsert_properties_sql = """
            INSERT INTO properties (
                source, external_id, title, property_type, listing_status,
                price, price_per_sqft, lease_rate, tax_assessed_value,
                beds, baths, sqft, lot_size_acres, year_built,
                address, city, county, state, zip_code, latitude, longitude,
                parcel_id, owner_name, legal_description, zoning,
                url, broker_name, raw_data, last_seen_at
            ) VALUES %s
            ON CONFLICT (source, external_id) DO UPDATE SET
                title = EXCLUDED.title,
                tax_assessed_value = EXCLUDED.tax_assessed_value,
                lot_size_acres = EXCLUDED.lot_size_acres,
                owner_name = EXCLUDED.owner_name,
                legal_description = EXCLUDED.legal_description,
                zoning = EXCLUDED.zoning,
                url = EXCLUDED.url,
                raw_data = EXCLUDED.raw_data,
                last_seen_at = NOW();
        """

        execute_values(
            cur,
            upsert_properties_sql,
            prop_tuples,
            template="(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb, NOW())"
        )
        conn.commit()
    logger.success(f"Upserted {len(all_records)} Regrid parcels into properties master table.")

    # 4. Sync into dedicated regrid_parcels table
    with conn.cursor() as cur:
        regrid_tuples = []
        for p in all_records:
            raw = p["raw_data"]
            regrid_tuples.append((
                p["external_id"],
                raw.get("ll_uuid"),
                raw.get("fips"),
                p["county"],
                p["state"],
                p["owner_name"],
                raw.get("owner_mailing"),
                p["address"],
                p["city"],
                p["zip_code"],
                raw.get("use_code"),
                p["zoning"],
                p["lot_size_acres"],
                raw.get("gis_sqft"),
                raw.get("land_value"),
                raw.get("improvement_value"),
                p["tax_assessed_value"],
                raw.get("tax_amount"),
                raw.get("last_sale_date"),
                raw.get("last_sale_price"),
                p["legal_description"],
                p["latitude"],
                p["longitude"],
                json.dumps(raw.get("geojson_geometry")),
                p["url"],
                json.dumps(raw)
            ))

        regrid_sql = """
            INSERT INTO regrid_parcels (
                parcel_apn, ll_uuid, fips, county, state,
                owner_name, owner_mailing_address, property_address,
                city, zip_code, use_code, zoning,
                lot_acres, lot_sqft, land_value, improvement_value,
                total_assessed_value, annual_tax_amount,
                last_sale_date, last_sale_price, legal_description,
                latitude, longitude, geojson_geometry, url, raw_json
            ) VALUES %s
            ON CONFLICT (parcel_apn) DO UPDATE SET
                total_assessed_value = EXCLUDED.total_assessed_value,
                annual_tax_amount = EXCLUDED.annual_tax_amount,
                owner_name = EXCLUDED.owner_name,
                updated_at = NOW();
        """

        execute_values(
            cur,
            regrid_sql,
            regrid_tuples,
            template="(%s, %s::uuid, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::date, %s, %s, %s, %s, %s::jsonb, %s, %s::jsonb)"
        )
        conn.commit()
    logger.success(f"Populated dedicated regrid_parcels table with {len(all_records)} rows.")

    # 5. Export updated store to data/properties_store.json
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM properties ORDER BY id ASC;")
        rows = cur.fetchall()
        logger.info(f"Total properties in DB after Regrid ingestion: {len(rows)}")

        store = {}
        for r in rows:
            d = {}
            for k, v in r.items():
                if hasattr(v, 'isoformat'):
                    d[k] = v.isoformat()
                elif hasattr(v, '__float__') and not isinstance(v, (int, float, bool)):
                    d[k] = float(v)
                else:
                    d[k] = v
            store[d['external_id']] = d

        store_file = BASE_DIR / "data" / "properties_store.json"
        store_file.write_text(json.dumps(store, indent=2), encoding="utf-8")
        logger.success(f"Updated {store_file} with {len(store)} total properties.")

    conn.close()

if __name__ == "__main__":
    ingest_regrid_data()
