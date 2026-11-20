import os
import json
from pathlib import Path
from typing import Any, Dict, List
from loguru import logger
from config import settings

class Database:
    def __init__(self):
        self.conn_params = {
            "host": settings.DB_HOST,
            "port": settings.DB_PORT,
            "dbname": settings.DB_NAME,
            "user": settings.DB_USER,
            "password": settings.DB_PASSWORD,
        }
        self.local_data_dir = Path(__file__).resolve().parent.parent / "data"
        self.local_data_dir.mkdir(parents=True, exist_ok=True)
        self.local_store_file = self.local_data_dir / "properties_store.json"
        self.log_file = self.local_data_dir / "crawl_logs.json"

    def is_postgres_available(self) -> bool:
        try:
            import psycopg2
            conn = psycopg2.connect(**self.conn_params, connect_timeout=2)
            conn.close()
            return True
        except Exception:
            return False

    def get_connection(self):
        import psycopg2
        return psycopg2.connect(**self.conn_params)

    def init_db(self, schema_file: Path | None = None) -> bool:
        """Initializes tables and triggers in PostgreSQL"""
        if self.is_postgres_available():
            if schema_file is None:
                schema_file = Path(__file__).resolve().parent.parent / "sql" / "schema.sql"

            if not schema_file.exists():
                logger.error(f"Schema file not found at: {schema_file}")
                return False

            sql = schema_file.read_text(encoding="utf-8")
            try:
                import psycopg2
                with psycopg2.connect(**self.conn_params) as conn:
                    with conn.cursor() as cur:
                        cur.execute(sql)
                    conn.commit()
                logger.success("PostgreSQL schema successfully initialized.")
                return True
            except Exception as e:
                logger.error(f"Error initializing PostgreSQL database: {e}")
                return False
        else:
            logger.warning("PostgreSQL server not detected on localhost:5432. Local JSON/CSV storage initialized at data/properties_store.json.")
            if not self.local_store_file.exists():
                self.local_store_file.write_text("{}", encoding="utf-8")
            if not self.log_file.exists():
                self.log_file.write_text("[]", encoding="utf-8")
            return True

    def upsert_properties(self, properties: List[Dict[str, Any]]) -> tuple[int, int]:
        if not properties:
            return 0, 0

        if self.is_postgres_available():
            return self._upsert_postgres(properties)
        else:
            return self._upsert_file_store(properties)

    def _upsert_postgres(self, properties: List[Dict[str, Any]]) -> tuple[int, int]:
        import psycopg2
        from psycopg2.extras import execute_values

        upsert_query = """
            INSERT INTO properties (
                source, external_id, title, property_type, listing_status,
                price, price_per_sqft, lease_rate, tax_assessed_value,
                beds, baths, sqft, lot_size_acres, year_built,
                address, city, county, state, zip_code, latitude, longitude,
                parcel_id, owner_name, legal_description, zoning,
                url, broker_name, raw_data, last_seen_at
            ) VALUES %s
            ON CONFLICT (source, external_id) DO UPDATE SET
                title = COALESCE(EXCLUDED.title, properties.title),
                property_type = COALESCE(EXCLUDED.property_type, properties.property_type),
                listing_status = COALESCE(EXCLUDED.listing_status, properties.listing_status),
                price = COALESCE(EXCLUDED.price, properties.price),
                price_per_sqft = COALESCE(EXCLUDED.price_per_sqft, properties.price_per_sqft),
                lease_rate = COALESCE(EXCLUDED.lease_rate, properties.lease_rate),
                tax_assessed_value = COALESCE(EXCLUDED.tax_assessed_value, properties.tax_assessed_value),
                beds = COALESCE(EXCLUDED.beds, properties.beds),
                baths = COALESCE(EXCLUDED.baths, properties.baths),
                sqft = COALESCE(EXCLUDED.sqft, properties.sqft),
                lot_size_acres = COALESCE(EXCLUDED.lot_size_acres, properties.lot_size_acres),
                year_built = COALESCE(EXCLUDED.year_built, properties.year_built),
                address = COALESCE(EXCLUDED.address, properties.address),
                city = COALESCE(EXCLUDED.city, properties.city),
                county = COALESCE(EXCLUDED.county, properties.county),
                zip_code = COALESCE(EXCLUDED.zip_code, properties.zip_code),
                latitude = COALESCE(EXCLUDED.latitude, properties.latitude),
                longitude = COALESCE(EXCLUDED.longitude, properties.longitude),
                parcel_id = COALESCE(EXCLUDED.parcel_id, properties.parcel_id),
                owner_name = COALESCE(EXCLUDED.owner_name, properties.owner_name),
                legal_description = COALESCE(EXCLUDED.legal_description, properties.legal_description),
                url = COALESCE(EXCLUDED.url, properties.url),
                broker_name = COALESCE(EXCLUDED.broker_name, properties.broker_name),
                raw_data = EXCLUDED.raw_data,
                last_seen_at = NOW()
            RETURNING (xmax = 0) AS is_inserted;
        """
        records = []
        for p in properties:
            records.append((
                p.get("source"),
                str(p.get("external_id")),
                p.get("title"),
                p.get("property_type"),
                p.get("listing_status", "active"),
                p.get("price"),
                p.get("price_per_sqft"),
                p.get("lease_rate"),
                p.get("tax_assessed_value"),
                p.get("beds"),
                p.get("baths"),
                p.get("sqft"),
                p.get("lot_size_acres"),
                p.get("year_built"),
                p.get("address"),
                p.get("city"),
                p.get("county"),
                p.get("state", "TX"),
                p.get("zip_code"),
                p.get("latitude"),
                p.get("longitude"),
                p.get("parcel_id"),
                p.get("owner_name"),
                p.get("legal_description"),
                p.get("zoning"),
                p.get("url"),
                p.get("broker_name"),
                json.dumps(p.get("raw_data", {})),
            ))

        try:
            with psycopg2.connect(**self.conn_params) as conn:
                with conn.cursor() as cur:
                    results = execute_values(
                        cur,
                        upsert_query,
                        records,
                        template="(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb, NOW())",
                        fetch=True
                    )
                    conn.commit()
                    inserted = sum(1 for r in results if r[0] is True)
                    updated = sum(1 for r in results if r[0] is False)
                    return inserted, updated
        except Exception as e:
            logger.error(f"Error during Postgres upsert: {e}")
            return 0, 0

    def _upsert_file_store(self, properties: List[Dict[str, Any]]) -> tuple[int, int]:
        store = {}
        if self.local_store_file.exists():
            try:
                store = json.loads(self.local_store_file.read_text(encoding="utf-8"))
            except Exception:
                store = {}

        inserted = 0
        updated = 0

        for p in properties:
            key = f"{p.get('source')}:{p.get('external_id')}"
            if key in store:
                updated += 1
                store[key].update(p)
            else:
                inserted += 1
                store[key] = p

        self.local_store_file.write_text(json.dumps(store, indent=2), encoding="utf-8")
        return inserted, updated

    def start_crawl_log(self, source: str, target_area: str) -> int:
        if self.is_postgres_available():
            import psycopg2
            try:
                with psycopg2.connect(**self.conn_params) as conn:
                    with conn.cursor() as cur:
                        cur.execute("INSERT INTO crawl_logs (source, target_area, status) VALUES (%s, %s, 'running') RETURNING id;", (source, target_area))
                        log_id = cur.fetchone()[0]
                        conn.commit()
                        return log_id
            except Exception:
                return -1
        else:
            return 1

    def finish_crawl_log(self, log_id: int, scraped: int, inserted: int, updated: int, status: str = "success", error: str | None = None):
        if self.is_postgres_available() and log_id != -1:
            import psycopg2
            try:
                with psycopg2.connect(**self.conn_params) as conn:
                    with conn.cursor() as cur:
                        cur.execute("""
                            UPDATE crawl_logs
                            SET items_scraped = %s, items_inserted = %s, items_updated = %s,
                                status = %s, error_message = %s, finished_at = NOW()
                            WHERE id = %s
                        """, (scraped, inserted, updated, status, error, log_id))
                        conn.commit()
            except Exception:
                pass
        else:
            pass

db = Database()
