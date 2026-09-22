@echo off
setlocal enabledelayedexpansion
title Sentinel-AutoGen-Hunter + OpenClaw Windows Setup
color 0A

echo ===============================================================================
echo   [SHIELD] Sentinel-AutoGen-Hunter: Windows 1-Click Setup & Launcher
echo   Autonomous Zero-Trust Threat Hunting Swarm + OpenClaw Multi-Channel Gateway
echo   Architect: Raghav Khandal (@raghavkhandal72-coder)
echo ===============================================================================
echo.

:: 1. Verify Python availability
where python >nul 2>nul
if %errorlevel% neq 0 (
    where py >nul 2>nul
    if %errorlevel% neq 0 (
        color 0C
        echo [ERROR] Python 3.10+ is required but not found on your system.
        echo.
        echo You can install Python in 30 seconds using Windows Package Manager:
        echo    winget install Python.Python.3.11
        echo.
        echo Or download the official installer from: https://www.python.org/downloads/
        echo (IMPORTANT: Make sure to check "Add Python to PATH" during installation)
        echo.
        pause
        exit /b 1
    )
    set "PYTHON_EXE=py -3"
) else (
    set "PYTHON_EXE=python"
)

for /f "tokens=*" %%v in ('%PYTHON_EXE% --version 2^>^&1') do set "PY_VER=%%v"
echo [*] Detected Python: %PY_VER%
echo.

:: 2. Determine App Working Directory
if exist "companion.py" if exist "requirements.txt" (
    set "APP_DIR=%CD%"
    echo [*] Running from existing source tree: !APP_DIR!
) else (
    set "APP_DIR=%USERPROFILE%\Sentinel-AutoGen-Hunter"
    echo [*] Setting up target application directory: !APP_DIR!
    if not exist "!APP_DIR!" mkdir "!APP_DIR!"

    if not exist "!APP_DIR!\companion.py" (
        where git >nul 2>nul
        if %errorlevel% equ 0 (
            echo [*] Cloning Sentinel-AutoGen-Hunter repository from GitHub...
            git clone --depth 1 https://github.com/raghavkhandal72-coder/sentinel-autogen-hunter.git "!APP_DIR!"
        ) else (
            echo [*] Git not detected. Downloading source bundle via PowerShell...
            powershell -NoProfile -ExecutionPolicy Bypass -Command ^
                "Write-Host 'Downloading zip archive...'; " ^
                "$zip = Join-Path $env:TEMP 'sentinel-main.zip'; " ^
                "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; " ^
                "Invoke-WebRequest -Uri 'https://github.com/raghavkhandal72-coder/sentinel-autogen-hunter/archive/refs/heads/main.zip' -OutFile $zip; " ^
                "Write-Host 'Extracting archive...'; " ^
                "$tempDir = Join-Path $env:TEMP 'sentinel-extract'; " ^
                "if (Test-Path $tempDir) { Remove-Item $tempDir -Recurse -Force }; " ^
                "Expand-Archive -Path $zip -DestinationPath $tempDir -Force; " ^
                "Copy-Item -Path \"$tempDir\sentinel-autogen-hunter-main\*\" -Destination '!APP_DIR!' -Recurse -Force; " ^
                "Remove-Item $zip -Force; Remove-Item $tempDir -Recurse -Force; " ^
                "Write-Host 'Source bundle installed successfully!'"
        )
    )
)

cd /d "!APP_DIR!"
if not exist "companion.py" (
    color 0C
    echo [ERROR] Failed to acquire repository files into: !APP_DIR!
    pause
    exit /b 1
)

:: 3. Setup Virtual Environment
if not exist ".venv" (
    echo [*] Creating isolated virtual environment (.venv)...
    %PYTHON_EXE% -m venv .venv
)

echo [*] Activating virtual environment...
call .venv\Scripts\activate.bat

:: 4. Install Dependencies
echo [*] Installing production dependencies and OpenClaw engine...
python -m pip install --upgrade pip -q
pip install -r requirements.txt -q
pip install -e . -q

:: 5. Create Desktop Shortcut for 1-Click Launch
echo [*] Creating Desktop shortcut...
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "$desktop = [Environment]::GetFolderPath('Desktop'); " ^
    "$s = (New-Object -ComObject WScript.Shell).CreateShortcut((Join-Path $desktop 'Sentinel Companion.lnk')); " ^
    "$s.TargetPath = (Resolve-Path '.venv\Scripts\pythonw.exe').Path; " ^
    "$s.Arguments = 'companion.py'; " ^
    "$s.WorkingDirectory = (Get-Location).Path; " ^
    "$s.Description = 'Sentinel-AutoGen-Hunter + OpenClaw Windows Companion'; " ^
    "$s.Save(); " ^
    "Write-Host 'Desktop shortcut created successfully!'"

echo.
echo ===============================================================================
echo   [SUCCESS] Sentinel-AutoGen-Hunter setup complete!
echo   Launching Sentinel Windows Companion Desktop Application...
echo ===============================================================================
echo.

:: 6. Launch Desktop Companion (using pythonw to run cleanly in background without console window)
start "" ".venv\Scripts\pythonw.exe" companion.py

timeout /t 3 >nul
exit /b 0
