#!/usr/bin/env bash
# ==============================================================================
# Script to install dependencies and configure Crontab on EC2 (Ubuntu)
# ==============================================================================

echo "Setting up Python environment and Cron Job on EC2..."

# 1. Update system packages
sudo apt update && sudo apt install -y python3 python3-pip python3-venv postgresql-client

# 2. Make runner executable
chmod +x ./run_crawl.sh

# 3. Add Cron Job to run every 6 hours (0:00, 6:00, 12:00, 18:00)
# Check if cron job is already added
CRON_CMD="0 0,6,12,18 * * * /home/ubuntu/realestate/run_crawl.sh"

(crontab -l 2>/dev/null | grep -Fv "/home/ubuntu/realestate/run_crawl.sh" ; echo "$CRON_CMD") | crontab -

echo "Cron job registered successfully! Check active jobs with: crontab -l"
