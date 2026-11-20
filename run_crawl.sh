#!/usr/bin/env bash
# ==============================================================================
# Linux EC2 Crontab & System Runner for Texas Real Estate Scraper
# ==============================================================================

set -e

# Project Directory on EC2
PROJECT_DIR="/home/ubuntu/realestate"
VENV_PYTHON="$PROJECT_DIR/venv/bin/python"
LOG_FILE="$PROJECT_DIR/logs/cron_execution.log"

# Create logs directory if it does not exist
mkdir -p "$PROJECT_DIR/logs"

echo "======================================================" >> "$LOG_FILE"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting EC2 Scheduled Crawl" >> "$LOG_FILE"

# Run data pipeline
cd "$PROJECT_DIR"
"$VENV_PYTHON" main.py >> "$LOG_FILE" 2>&1

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Finished EC2 Scheduled Crawl" >> "$LOG_FILE"
