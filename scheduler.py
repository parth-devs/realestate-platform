import time
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from loguru import logger
from config import settings
from main import run_pipeline

def scheduled_job():
    logger.info("⏰ Triggering Scheduled Texas Real Estate Ingestion Job...")
    try:
        run_pipeline(
            sources=["zillow", "loopnet", "texas_cad"],
            cities=settings.TARGET_CITIES
        )
    except Exception as e:
        logger.error(f"Scheduled job encountered an error: {e}")

if __name__ == "__main__":
    scheduler = BlockingScheduler()

    # Schedule: Run every 6 hours (00:00, 06:00, 12:00, 18:00)
    # You can customize this cron expression to whatever you need!
    scheduler.add_job(
        scheduled_job,
        trigger=CronTrigger(hour="0,6,12,18", minute="0"),
        id="texas_realestate_job",
        name="Texas Real Estate Data Collector",
        replace_existing=True
    )

    logger.info("=" * 60)
    logger.info("Real Estate Automation Scheduler is Active (Local Windows & Testing).")
    logger.info("Job scheduled to run at: 00:00, 06:00, 12:00, 18:00 every day.")
    logger.info("Press Ctrl+C to stop.")
    logger.info("=" * 60)

    # Run once immediately on start for testing
    logger.info("Executing initial crawl on start...")
    scheduled_job()

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped by user.")
