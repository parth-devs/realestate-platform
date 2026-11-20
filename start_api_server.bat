@echo off
cd /d "%~dp0"
echo ========================================================
echo Starting Custom US Real Estate REST API Server (FastAPI)
echo Running on: http://localhost:8080
echo Interactive API Swagger Docs: http://localhost:8080/docs
echo ========================================================
".venv\Scripts\python.exe" -m uvicorn api.main:app --host 0.0.0.0 --port 8080 --reload
pause
