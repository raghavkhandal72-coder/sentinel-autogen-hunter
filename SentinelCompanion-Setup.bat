@echo off
title Sentinel-AutoGen-Hunter + OpenClaw Windows Companion
color 0A

echo ===============================================================================
echo   [SHIELD] Sentinel-AutoGen-Hunter: Windows Companion Desktop Launcher
echo   Autonomous Zero-Trust Threat Hunting Swarm + OpenClaw Multi-Channel Gateway
echo ===============================================================================
echo.

where python >nul 2>nul
if %errorlevel% neq 0 (
    color 0C
    echo [ERROR] Python is not found on your system PATH.
    echo Please install Python 3.10+ from python.org or via winget:
    echo    winget install Python.Python.3.11
    echo.
    pause
    exit /b 1
)

if not exist ".venv" (
    echo [*] Initializing virtual environment (.venv)...
    python -m venv .venv
)

echo [*] Activating virtual environment...
call .venv\Scripts\activate.bat

echo [*] Checking dependencies...
pip install -r requirements.txt -q
pip install -e . -q

echo.
echo [*] Launching Sentinel Windows Companion Desktop Application...
python companion.py

if %errorlevel% neq 0 (
    echo.
    echo [!] Companion closed or encountered an error.
    pause
)
