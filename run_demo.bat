@echo off
title Bike Rental System - Viva Scenario Demonstrator
cd /d "%~dp0"
call .\venv\Scripts\activate
python backend\scripts\run_scenarios.py
pause
