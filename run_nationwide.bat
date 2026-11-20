@echo off
cd /d "%~dp0"
echo ===================================================
echo Starting Nationwide US Real Estate Scraper...
echo Collecting Zillow, LoopNet, and LandGlide nationwide!
echo ===================================================
".venv\Scripts\python.exe" crawl_nationwide.py
echo ===================================================
echo Done! Check pgAdmin to see updated tables!
echo ===================================================
pause
