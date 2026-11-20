import argparse
import sys
from loguru import logger
from config import settings
from database.db import db
from collectors.zillow import ZillowCollector
from collectors.loopnet import LoopNetCollector
from collectors.us_parcels import USParcelCollector

logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>",
    level="INFO"
)
logger.add("logs/scraper_{time:YYYY-MM-DD}.log", rotation="20 MB", retention="14 days")

def run_pipeline(sources: list[str], markets: list[dict]):
    logger.info("🚀 Starting Nationwide US Real Estate Ingestion Pipeline...")
    logger.info(f"Target Markets: {len(markets)} US Metros/Cities")
    logger.info(f"Target Sources: {sources}")

    collector_map = {
        "zillow": ZillowCollector(),
        "loopnet": LoopNetCollector(),
        "landglide": USParcelCollector(),
        "texas_cad": USParcelCollector(),
        "us_parcels": USParcelCollector(),
    }

    total_scraped = 0
    total_inserted = 0
    total_updated = 0

    for m in markets:
        city = m.get("city")
        state = m.get("state", "TX")

        for source_name in sources:
            collector = collector_map.get(source_name.lower())
            if not collector:
                continue

            target_label = f"{city}, {state}"
            log_id = db.start_crawl_log(source=source_name, target_area=target_label)

            try:
                records = collector.run(city=city, state=state)
                scraped_count = len(records)
                total_scraped += scraped_count

                inserted, updated = db.upsert_properties(records)
                total_inserted += inserted
                total_updated += updated

                db.finish_crawl_log(
                    log_id=log_id,
                    scraped=scraped_count,
                    inserted=inserted,
                    updated=updated,
                    status="success"
                )
                logger.success(
                    f"[{source_name.upper()} - {target_label}] Scraped: {scraped_count} | Inserted: {inserted} | Updated: {updated}"
                )
            except Exception as e:
                logger.error(f"[{source_name.upper()} - {target_label}] Error: {e}")
                db.finish_crawl_log(
                    log_id=log_id,
                    scraped=0,
                    inserted=0,
                    updated=0,
                    status="failed",
                    error=str(e)
                )

    logger.info("=" * 60)
    logger.info(f"Nationwide Crawl Completed! Total Scraped: {total_scraped} | Inserted: {total_inserted} | Updated: {total_updated}")
    logger.info("=" * 60)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Nationwide Real Estate Data Collector")
    parser.add_argument("--init-db", action="store_true", help="Initialize schema tables")
    parser.add_argument("--scope", choices=["metros", "nationwide", "custom"], default="metros", help="Crawl scope")
    parser.add_argument("--sources", nargs="+", default=["zillow", "loopnet", "us_parcels"], help="Data sources")
    parser.add_argument("--city", type=str, help="Single city (e.g. Miami)")
    parser.add_argument("--state", type=str, default="FL", help="Single state (e.g. FL)")

    args = parser.parse_args()

    if args.init_db:
        db.init_db()
        sys.exit(0)

    if args.city:
        markets = [{"city": args.city, "state": args.state}]
    else:
        markets = settings.get_target_markets()

    run_pipeline(sources=args.sources, markets=markets)
