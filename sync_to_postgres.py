import json
from pathlib import Path
from loguru import logger
from database.db import db

def sync_data():
    store_file = Path(__file__).resolve().parent / "data" / "properties_store.json"
    if not store_file.exists():
        logger.error(f"Data file not found at {store_file}")
        return

    data = json.loads(store_file.read_text(encoding="utf-8"))
    records = list(data.values())
    logger.info(f"Loaded {len(records)} properties from local store.")

    logger.info("Initializing PostgreSQL schema tables & triggers...")
    if not db.init_db():
        logger.error("Could not initialize PostgreSQL schema. Check database credentials.")
        return

    logger.info(f"Uploading {len(records)} records into PostgreSQL 'properties' table...")
    inserted, updated = db._upsert_postgres(records)
    logger.success(f"Sync complete! Inserted: {inserted} | Updated: {updated}")

if __name__ == "__main__":
    sync_data()
