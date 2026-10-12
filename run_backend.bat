@echo off
title Bike Rental System - FastAPI Backend
echo ========================================================
echo Starting Bike Rental Management System Backend API...
echo API Docs will be available at: http://127.0.0.1:8000/docs
echo ========================================================
cd /d "%~dp0"
call .\venv\Scripts\activate
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
pause
