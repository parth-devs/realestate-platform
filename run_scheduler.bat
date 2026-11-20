@echo off
cd /d "%~dp0"
echo ===================================================
echo Starting Real Estate Automation Scheduler...
echo Runs every 6 hours automatically. Press Ctrl+C to stop.
echo ===================================================
".venv\Scripts\python.exe" scheduler.py
pause
