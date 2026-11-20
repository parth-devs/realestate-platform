@echo off
cd /d "%~dp0"
echo ===================================================
echo Starting Texas Real Estate Scraper (Austin, TX)...
echo ===================================================
".venv\Scripts\python.exe" main.py --cities Austin --sources zillow loopnet texas_cad
echo ===================================================
echo Done! Output saved in outputs\ and data\
echo ===================================================
pause
