# Texas Real Estate Data Pipeline & Automation Engine

An automated Python & PostgreSQL data ingestion system targeting Texas real estate across **Zillow** (residential), **LoopNet** (commercial), and **LandGlide / County Appraisal Districts (CAD)** (land, parcel boundaries, ownership, and tax values).

---

## 1. System Architecture: WHAT, WHY & HOW

### A. What Data Is Collected?
| Source | Property Scope | Key Data Fields Extracted |
| :--- | :--- | :--- |
| **Zillow** | Residential (Single Family, Townhomes, Condos, For Sale/Rent) | ZPID, Street Address, City, County, ZIP, List Price, Price/SqFt, Beds, Baths, Living Area (SqFt), Lat/Long Coordinates, Brokerage, Listing URL. |
| **LoopNet** | Commercial (Office, Industrial, Retail, Multi-family, Commercial Land) | LoopNet ID, Title, Property Type, List Price or Lease Rate ($/SF/YR), Total Building SF, Lot Acreage, Submarket/City, Broker Name, Listing URL. |
| **LandGlide / Texas CAD** | Land, Acreage, Parcels & Ownership | Assessor Parcel Number (APN), Registered Owner Name, Legal Description, Land Area (Acres & SqFt), County Assessed Tax Value, Zoning, GIS Coordinates. |

> **Special Texas Note**: Texas is a **non-disclosure state** (actual final sold prices are not recorded in public deeds). The data pipeline captures **Listing Asking Prices** from Zillow/LoopNet and **Tax Assessed Market Values** from County Appraisal District (CAD) open GIS records (the same open data feeds LandGlide uses).

---

### B. Why These Sources & Anti-Bot Considerations
1. **Zillow & LoopNet anti-scraping**: Both websites use bot detection (DataDome / PerimeterX / Cloudflare). The code includes polite request delays, randomized desktop browser headers, session reuse, and automatic exponential backoff retries. For high-volume EC2 scraping, routing through a rotating residential proxy or ScraperAPI is supported out-of-the-box via the `.env` configuration.
2. **LandGlide**: LandGlide is a mobile paid front-end application built on top of public **County Appraisal District (CAD)** GIS parcel records. Scraping the mobile app directly requires bypassing device certificate pinning and violates app store terms. Our pipeline directly and legally ingests from Texas Open Data & County CAD GIS endpoints, giving you clean parcel boundaries, owner names, APNs, and acreage for free with zero CAPTCHAs.

---

### C. How Does Data Update & Deduplicate (Upsert)?
The pipeline uses PostgreSQL **UPSERT (`ON CONFLICT (source, external_id) DO UPDATE ...`)**:
1. When a property is scraped for the first time: It is **inserted** as a new row.
2. When the property is seen again on subsequent runs:
   - Its `last_seen_at` and `updated_at` timestamps are updated.
   - If the price has changed, the database **PostgreSQL Trigger (`trg_track_price_change`)** automatically archives the change into the `price_history` table (recording `previous_price`, `new_price`, and timestamp).
   - Any updated specs (e.g., status changes to pending/sold, or price cuts) are updated in-place without duplicating rows.

---

## 2. Directory Structure

```text
C:\Real Estate\
├── config.py                 # Central configuration & environment loader
├── docker-compose.yml        # Instant PostgreSQL + pgAdmin for local development
├── requirements.txt          # Python dependencies
├── .env.example              # Template for database & scraping settings
├── sql/
│   └── schema.sql            # PostgreSQL schema, triggers, and audit tables
├── database/
│   └── db.py                 # PostgreSQL connection pool & bulk upsert engine
├── collectors/
│   ├── base.py               # Base scraper class with retries & polite delays
│   ├── zillow.py             # Zillow residential parser
│   ├── loopnet.py            # LoopNet commercial parser
│   └── texas_parcels.py      # Texas Land & Parcel parser (LandGlide CAD equivalent)
├── main.py                   # CLI tool to run collectors on demand
├── scheduler.py              # Automated scheduler for local Windows testing (APScheduler)
├── run_crawl.sh              # Bash execution wrapper for Linux EC2
├── ec2_cron_setup.sh         # Crontab setup script for Linux EC2
└── logs/                     # Rotation logs directory
```

---

## 3. Quickstart: Running Locally on Windows

### Step 1: Install Python Dependencies
Using Python 3.10+ (or the `uv` package manager installed on your machine):
```powershell
# Using uv (fastest):
uv pip install -r requirements.txt

# Or using standard python:
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

### Step 2: Start PostgreSQL Database
If you have Docker Desktop installed, run:
```powershell
docker compose up -d
```
* PostgreSQL will run on port `5432` (User: `postgres`, Password: `postgres`, DB: `realestate_texas`).
* pgAdmin web GUI will run on `http://localhost:5050` (Email: `admin@admin.com`, Password: `admin`).

*(If you already have a local PostgreSQL or cloud RDS instance, just copy `.env.example` to `.env` and enter your database credentials).*

### Step 3: Initialize the Database Schema
```powershell
python main.py --init-db
```

### Step 4: Run a Manual Collection Test
```powershell
# Scrape all 3 sources for Austin, TX
python main.py --cities Austin --sources zillow loopnet texas_cad
```

### Step 5: Test the Cron Scheduler Locally on Windows
```powershell
python scheduler.py
```
*(Runs an immediate crawl, then executes every 6 hours automatically)*.

---

## 4. Deploying to AWS EC2 (Linux / Ubuntu)

1. Clone or copy your project folder to your EC2 instance (e.g., `/home/ubuntu/realestate`).
2. SSH into your EC2 instance:
   ```bash
   ssh -i your-key.pem ubuntu@your-ec2-ip
   ```
3. Set up the virtual environment:
   ```bash
   cd /home/ubuntu/realestate
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
4. Copy and configure your `.env`:
   ```bash
   cp .env.example .env
   nano .env
   ```
5. Initialize the database schema:
   ```bash
   python3 main.py --init-db
   ```
6. Run the automated crontab setup:
   ```bash
   chmod +x ec2_cron_setup.sh run_crawl.sh
   ./ec2_cron_setup.sh
   ```
7. Verify active cron jobs:
   ```bash
   crontab -l
   ```
   *(This will run `run_crawl.sh` every 6 hours and append logs to `logs/cron_execution.log`)*.
