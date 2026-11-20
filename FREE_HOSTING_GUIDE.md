# 100% Free Cloud Hosting Guide (No Credit Card Required)

This guide shows you how to host your entire Real Estate Intelligence Platform (**Cloud Database**, **FastAPI Backend**, **Web UI**, and **Automated 6-Hour Cron Scraping**) for **\$0.00 / month forever** without paying for an AWS EC2 instance.

---

## 3-Pillar Architecture (All 100% Free Tiers)

```
┌─────────────────────────────────┐      ┌─────────────────────────────────┐
│     1. Free PostgreSQL Cloud    │◄─────┤    2. Free Web API & Dashboard  │
│          (Neon.tech)            │      │          (Render.com)           │
│   • Serverless Postgres 16      │      │   • FastAPI + Web UI on HTTPS   │
│   • Free 0.5 GB Storage         │      │   • Custom domain / onrender.com│
└─────────────────────────────────┘      └─────────────────────────────────┘
                 ▲
                 │ (Updates DB every 6 hours)
┌────────────────┴────────────────┐
│   3. Free Automated Cron Job    │
│      (GitHub Actions Cron)      │
│   • Runs main.py every 6 hrs    │
│   • 2,000 free runner mins/mo   │
└─────────────────────────────────┘
```

---

## Step 1: Get Free Cloud PostgreSQL (Neon.tech) — 1 Minute

1. Go to **[https://neon.tech](https://neon.tech)** and click **Sign Up** (Sign in with your GitHub or Google account - NO credit card needed).
2. Click **Create Project**:
   - Project Name: `realestate-us`
   - Region: Choose nearest (e.g. `US East (Ohio)`).
3. Under **Connection Details**, Neon gives you your connection string:
   ```text
   postgresql://username:password@ep-xyz.us-east-2.aws.neon.tech/neondb?sslmode=require
   ```
4. Copy these 5 values from it:
   - `DB_HOST` = `ep-xyz.us-east-2.aws.neon.tech`
   - `DB_PORT` = `5432`
   - `DB_NAME` = `neondb`
   - `DB_USER` = your username
   - `DB_PASSWORD` = your password

---

## Step 2: Push Your Project to GitHub (Free)

1. Open PowerShell in `C:\Real Estate` and initialize git:
   ```powershell
   git init
   git add .
   git commit -m "Initial enterprise real estate platform"
   ```
2. Create a new repository on **[https://github.com/new](https://github.com/new)** named `realestate-platform`.
3. Push your code:
   ```powershell
   git remote add origin https://github.com/YOUR_USERNAME/realestate-platform.git
   git branch -M main
   git push -u origin main
   ```

---

## Step 3: Deploy Free Web API & UI (Render.com) — 2 Minutes

1. Go to **[https://render.com](https://render.com)** and sign in with GitHub.
2. Click **New +** ➔ **Web Service**.
3. Select your `realestate-platform` GitHub repository.
4. Settings:
   - **Name**: `realestate-api`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt fastapi uvicorn`
   - **Start Command**: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: `Free`
5. Scroll down to **Environment Variables** and add your Neon credentials:
   - `DB_HOST`: your Neon host
   - `DB_PORT`: `5432`
   - `DB_NAME`: `neondb`
   - `DB_USER`: your Neon user
   - `DB_PASSWORD`: your Neon password
6. Click **Deploy Web Service**!
   - In 2 minutes, Render gives you a public live HTTPS URL:
     👉 `https://realestate-api-xxxx.onrender.com/` (Your live Web UI!)
     👉 `https://realestate-api-xxxx.onrender.com/docs` (Your live Swagger API docs!)

---

## Step 4: Configure Free 6-Hour Automated Cron (GitHub Actions)

We already created the workflow file at `.github/workflows/scheduled_crawl.yml`.

1. In your GitHub repository, click **Settings** ➔ **Secrets and variables** ➔ **Actions**.
2. Click **New repository secret** and add your 5 Neon DB credentials:
   - `DB_HOST`
   - `DB_PORT`
   - `DB_NAME`
   - `DB_USER`
   - `DB_PASSWORD`
3. Done! GitHub Actions will now automatically:
   - Wake up every 6 hours (`00:00, 06:00, 12:00, 18:00 UTC`).
   - Run `main.py --scope nationwide` on GitHub's free cloud runners.
   - Ingest fresh Zillow, LoopNet, and LandGlide data into your Neon PostgreSQL database.
   - Cost: **\$0.00 / month forever**.
