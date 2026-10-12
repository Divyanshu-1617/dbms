@echo off
title Bike Rental System - Automated Test Suite
cd /d "%~dp0"
call .\venv\Scripts\activate
pytest -o pythonpath=backend backend\tests\ -v
pause
