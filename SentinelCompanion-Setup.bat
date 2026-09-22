@echo off
setlocal enabledelayedexpansion
title Sentinel-AutoGen-Hunter + OpenClaw Windows Setup
color 0A

echo ===============================================================================
echo   [SHIELD] Sentinel-AutoGen-Hunter: Windows 1-Click Setup & Launcher
echo   Autonomous Zero-Trust Threat Hunting Swarm + OpenClaw Multi-Channel Gateway
echo   Architect: Raghav Khandal (@raghavkhandal72-coder) • Version 2.0.0
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
        echo Installing Python via Windows Package Manager (winget)...
        winget install Python.Python.3.11 --silent --accept-source-agreements --accept-package-agreements
        where python >nul 2>nul
        if %errorlevel% neq 0 (
            echo.
            echo Please install Python manually from: https://www.python.org/downloads/
            echo (IMPORTANT: Make sure to check "Add Python to PATH")
            pause
            exit /b 1
        )
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
    echo [*] Using local source directory: !APP_DIR!
) else (
    set "APP_DIR=%USERPROFILE%\Sentinel-AutoGen-Hunter"
    echo [*] Setting up target application directory: !APP_DIR!
    if not exist "!APP_DIR!" mkdir "!APP_DIR!"

    if not exist "!APP_DIR!\companion.py" (
        where git >nul 2>nul
        if %errorlevel% equ 0 (
            echo [*] Fetching latest release from GitHub...
            git clone --depth 1 https://github.com/raghavkhandal72-coder/sentinel-autogen-hunter.git "!APP_DIR!"
        ) else (
            echo [*] Downloading release bundle from GitHub...
            powershell -NoProfile -ExecutionPolicy Bypass -Command ^
                "$zip = Join-Path $env:TEMP 'sentinel-main.zip'; " ^
                "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; " ^
                "Invoke-WebRequest -Uri 'https://github.com/raghavkhandal72-coder/sentinel-autogen-hunter/archive/refs/heads/main.zip' -OutFile $zip; " ^
                "$tempDir = Join-Path $env:TEMP 'sentinel-extract'; " ^
                "if (Test-Path $tempDir) { Remove-Item $tempDir -Recurse -Force }; " ^
                "Expand-Archive -Path $zip -DestinationPath $tempDir -Force; " ^
                "Copy-Item -Path \"$tempDir\sentinel-autogen-hunter-main\*\" -Destination '!APP_DIR!' -Recurse -Force; " ^
                "Remove-Item $zip -Force; Remove-Item $tempDir -Recurse -Force"
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
    echo [*] Initializing isolated runtime (.venv)...
    %PYTHON_EXE% -m venv .venv
)

:: 4. Install Dependencies
echo [*] Installing production dependencies and OpenClaw engine...
.\.venv\Scripts\python.exe -m pip install --upgrade pip -q --no-warn-script-location --disable-pip-version-check
.\.venv\Scripts\python.exe -m pip install -r requirements.txt -q --no-warn-script-location --disable-pip-version-check
.\.venv\Scripts\python.exe -m pip install -e . -q --no-warn-script-location --disable-pip-version-check

:: 5. Create Global CLI 'sentinel' and Desktop Shortcuts
echo [*] Registering global 'sentinel' command and desktop shortcuts...
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "$targetDir = '!APP_DIR!'; " ^
    "$pyw = Join-Path $targetDir '.venv\Scripts\pythonw.exe'; " ^
    "$cmdPath = Join-Path $targetDir 'sentinel.cmd'; " ^
    "$cmdContent = '@echo off`nset \"SENTINEL_ROOT=%~dp0\"`nif \"%1\"==\"\" ( start \"\" \"%SENTINEL_ROOT%\.venv\Scripts\pythonw.exe\" \"%SENTINEL_ROOT%\companion.py\" & exit /b 0 )`nif \"%1\"==\"gui\" ( start \"\" \"%SENTINEL_ROOT%\.venv\Scripts\pythonw.exe\" \"%SENTINEL_ROOT%\companion.py\" & exit /b 0 )`nif \"%1\"==\"companion\" ( start \"\" \"%SENTINEL_ROOT%\.venv\Scripts\pythonw.exe\" \"%SENTINEL_ROOT%\companion.py\" & exit /b 0 )`n\"%SENTINEL_ROOT%\.venv\Scripts\python.exe\" -m cli.main %*'; " ^
    "Set-Content -Path $cmdPath -Value $cmdContent -Encoding ASCII; " ^
    "try { $p = [Environment]::GetEnvironmentVariable('Path', 'User'); if ($p -notlike \"*$targetDir*\") { [Environment]::SetEnvironmentVariable('Path', \"$p;$targetDir\", 'User') } } catch {}; " ^
    "$desktops = @([Environment]::GetFolderPath('Desktop'), (Join-Path $env:USERPROFILE 'Desktop'), (Join-Path (Join-Path $env:USERPROFILE 'OneDrive') 'Desktop')) | Where-Object { Test-Path $_ } | Select-Object -Unique; " ^
    "$shell = New-Object -ComObject WScript.Shell; " ^
    "foreach ($d in $desktops) { $lnk = Join-Path $d 'Sentinel Companion.lnk'; $s = $shell.CreateShortcut($lnk); $s.TargetPath = $pyw; $s.Arguments = 'companion.py'; $s.WorkingDirectory = $targetDir; $s.Save(); }; " ^
    "$prog = [Environment]::GetFolderPath('Programs'); if (Test-Path $prog) { $s = $shell.CreateShortcut((Join-Path $prog 'Sentinel Companion.lnk')); $s.TargetPath = $pyw; $s.Arguments = 'companion.py'; $s.WorkingDirectory = $targetDir; $s.Save() }"

echo.
echo ===============================================================================
echo   [SUCCESS] Sentinel-AutoGen-Hunter setup complete!
echo   Launching Sentinel Windows Companion Desktop Application...
echo ===============================================================================
echo.

:: 6. Launch Desktop Companion (using pythonw to run cleanly in background)
start "" ".venv\Scripts\pythonw.exe" companion.py

timeout /t 2 >nul
exit /b 0
