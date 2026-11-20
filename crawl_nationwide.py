import time
from loguru import logger
from main import run_pipeline
from populate_all_tables import sync_dedicated_tables_from_db

NATIONWIDE_METROS = [
    {"city": "New York", "state": "NY"},
    {"city": "Los Angeles", "state": "CA"},
    {"city": "Chicago", "state": "IL"},
    {"city": "Miami", "state": "FL"},
    {"city": "Atlanta", "state": "GA"},
    {"city": "Dallas", "state": "TX"},
    {"city": "Denver", "state": "CO"},
    {"city": "Phoenix", "state": "AZ"},
    {"city": "Seattle", "state": "WA"}
]

def execute_nationwide():
    logger.info("🇺🇸 Starting Nationwide Crawl across major US Markets...")
    run_pipeline(
        sources=["zillow", "loopnet", "us_parcels"],
        markets=NATIONWIDE_METROS
    )
    logger.info("Syncing newly scraped US properties into dedicated PostgreSQL tables...")
    sync_dedicated_tables_from_db()
    logger.success("🇺🇸 Nationwide Ingestion & Database Sync Completed Successfully!")

if __name__ == "__main__":
    execute_nationwide()
