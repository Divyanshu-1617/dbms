@echo off
title Bike Rental System - Full Platform Launcher
echo ========================================================
echo Launching Peer-to-Peer Tourist Bike Rental System
echo 1. Starting FastAPI Backend Server (Port 8000)
echo 2. Starting React Dashboard Server (Port 5173)
echo ========================================================
start "Bike Rental - Backend API" cmd /k "cd /d %~dp0 && call .\venv\Scripts\activate && uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload"
timeout /t 2 /nobreak >nul
start "Bike Rental - Frontend Dashboard" cmd /k "cd /d %~dp0frontend && npm run dev"
echo Both servers have been launched!
echo Backend Swagger Docs: http://127.0.0.1:8000/docs
echo Frontend Dashboard:   http://localhost:5173
pause
