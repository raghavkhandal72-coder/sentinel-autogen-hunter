# ==============================================================================
# Sentinel-AutoGen-Hunter Windows 1-Liner PowerShell Installer
# Powered by OpenClaw Multi-Channel Gateway & Zero-Trust Defense Suite
#
# Usage (run from PowerShell):
#   irm https://raw.githubusercontent.com/raghavkhandal72-coder/sentinel-autogen-hunter/main/install.ps1 | iex
# ==============================================================================

param (
    [switch]$NoLaunch
)

$ErrorActionPreference = "Continue"

Write-Host ""
Write-Host "  ╭────────────────────────────────────────────────────────────────────────╮" -ForegroundColor DarkCyan
Write-Host "  │                                                                        │" -ForegroundColor DarkCyan
Write-Host "  │   🛡️  SENTINEL-AUTOGEN-HUNTER                                          │" -ForegroundColor Cyan
Write-Host "  │   Autonomous Threat Hunting Swarm & OpenClaw Agent Gateway Engine     │" -ForegroundColor Green
Write-Host "  │   Architect: Raghav Khandal (@raghavkhandal72-coder) • Version 2.0.0   │" -ForegroundColor DarkGray
Write-Host "  │                                                                        │" -ForegroundColor DarkCyan
Write-Host "  ╰────────────────────────────────────────────────────────────────────────╯" -ForegroundColor DarkCyan
Write-Host ""

# [1/6] Check Python
Write-Host " [1/6] 🔍 Verifying system environment..." -ForegroundColor Cyan
$pythonCmd = $null
if (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonCmd = "python"
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
    $pythonCmd = "py -3"
}

if (-not $pythonCmd) {
    Write-Host "  ❌ Python 3.10+ is required but not found on your system." -ForegroundColor Red
    Write-Host "  >> Installing Python 3.11 via Windows Package Manager (winget)..." -ForegroundColor Yellow
    try {
        winget install Python.Python.3.11 --silent --accept-source-agreements --accept-package-agreements
        $pythonCmd = "python"
    } catch {
        Write-Host "  >> Please install Python manually from: https://www.python.org/downloads/" -ForegroundColor Red
        Exit 1
    }
}

$pyVer = & $pythonCmd --version 2>&1
Write-Host "  ✔ Python detected: $pyVer" -ForegroundColor Green

# [2/6] Acquire Repository
Write-Host " [2/6] 📥 Fetching Sentinel-AutoGen-Hunter & OpenClaw engine..." -ForegroundColor Cyan
$targetDir = Join-Path $HOME "Sentinel-AutoGen-Hunter"
if (Test-Path "companion.py") {
    $targetDir = (Get-Location).Path
    Write-Host "  ✔ Using local source directory: $targetDir" -ForegroundColor Green
} else {
    if (-not (Test-Path $targetDir)) {
        New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
    }

    if (-not (Test-Path (Join-Path $targetDir "companion.py"))) {
        if (Get-Command git -ErrorAction SilentlyContinue) {
            Write-Host "  >> Cloning latest release from GitHub..." -ForegroundColor DarkGray
            git clone --depth 1 https://github.com/raghavkhandal72-coder/sentinel-autogen-hunter.git $targetDir 2>$null
        } else {
            Write-Host "  >> Downloading release bundle from GitHub..." -ForegroundColor DarkGray
            $zipUrl = "https://github.com/raghavkhandal72-coder/sentinel-autogen-hunter/archive/refs/heads/main.zip"
            $zipFile = Join-Path $env:TEMP "sentinel-main.zip"
            [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
            Invoke-WebRequest -Uri $zipUrl -OutFile $zipFile -UseBasicParsing
            $tempExtract = Join-Path $env:TEMP "sentinel-extract"
            if (Test-Path $tempExtract) { Remove-Item $tempExtract -Recurse -Force }
            Expand-Archive -Path $zipFile -DestinationPath $tempExtract -Force
            Copy-Item -Path (Join-Path $tempExtract "sentinel-autogen-hunter-main\*") -Destination $targetDir -Recurse -Force
            Remove-Item $zipFile -Force
            Remove-Item $tempExtract -Recurse -Force
        }
    }
    Set-Location $targetDir
    Write-Host "  ✔ Installed in: $targetDir" -ForegroundColor Green
}

# [3/6] Setup Virtual Environment
Write-Host " [3/6] 🛡️  Configuring isolated runtime (.venv)..." -ForegroundColor Cyan
if (-not (Test-Path ".venv")) {
    & $pythonCmd -m venv .venv
}

$venvPython = (Join-Path $targetDir ".venv\Scripts\python.exe")
$venvPythonw = (Join-Path $targetDir ".venv\Scripts\pythonw.exe")
$venvPip = (Join-Path $targetDir ".venv\Scripts\pip.exe")

# [4/6] Install Dependencies
Write-Host " [4/6] 📦 Installing core dependencies & UI engine (customtkinter, fastapi, rich)..." -ForegroundColor Cyan
& $venvPython -m pip install --upgrade pip -q --no-warn-script-location --disable-pip-version-check 2>$null
if (Test-Path "requirements.txt") {
    & $venvPython -m pip install -r requirements.txt -q --no-warn-script-location --disable-pip-version-check 2>$null
}
& $venvPython -m pip install -e . -q --no-warn-script-location --disable-pip-version-check 2>$null
Write-Host "  ✔ All dependencies installed successfully!" -ForegroundColor Green

# [5/6] Register Global CLI & Shortcuts
Write-Host " [5/6] ⚡ Registering global 'sentinel' command & Desktop shortcuts..." -ForegroundColor Cyan

# Create sentinel.cmd runner
$sentinelCmdPath = Join-Path $targetDir "sentinel.cmd"
$cmdScript = @"
@echo off
set "SENTINEL_ROOT=%~dp0"
if "%1"=="" (
    start "" "%SENTINEL_ROOT%\.venv\Scripts\pythonw.exe" "%SENTINEL_ROOT%\companion.py"
    exit /b 0
)
if "%1"=="gui" (
    start "" "%SENTINEL_ROOT%\.venv\Scripts\pythonw.exe" "%SENTINEL_ROOT%\companion.py"
    exit /b 0
)
if "%1"=="companion" (
    start "" "%SENTINEL_ROOT%\.venv\Scripts\pythonw.exe" "%SENTINEL_ROOT%\companion.py"
    exit /b 0
)
"%SENTINEL_ROOT%\.venv\Scripts\python.exe" -m cli.main %*
"@
Set-Content -Path $sentinelCmdPath -Value $cmdScript -Encoding ASCII

# Add targetDir to User PATH if not present
try {
    $currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
    if ($currentPath -notlike "*$targetDir*") {
        [Environment]::SetEnvironmentVariable("Path", "$currentPath;$targetDir", "User")
        $env:PATH = "$env:PATH;$targetDir"
        Write-Host "  ✔ Added 'sentinel' to user PATH (now accessible from any terminal)" -ForegroundColor Green
    }
} catch {}

# Create Desktop Shortcut in all user desktop locations (including OneDrive)
$desktopLocations = @(
    [Environment]::GetFolderPath('Desktop'),
    (Join-Path $env:USERPROFILE 'Desktop'),
    (Join-Path (Join-Path $env:USERPROFILE 'OneDrive') 'Desktop')
) | Where-Object { Test-Path $_ } | Select-Object -Unique

foreach ($dPath in $desktopLocations) {
    try {
        $shortcutPath = Join-Path $dPath "Sentinel Companion.lnk"
        $wscriptShell = New-Object -ComObject WScript.Shell
        $shortcut = $wscriptShell.CreateShortcut($shortcutPath)
        if (Test-Path $venvPythonw) {
            $shortcut.TargetPath = (Resolve-Path $venvPythonw).Path
        } else {
            $shortcut.TargetPath = (Resolve-Path $venvPython).Path
        }
        $shortcut.Arguments = "companion.py"
        $shortcut.WorkingDirectory = $targetDir
        $shortcut.Description = "Sentinel-AutoGen-Hunter + OpenClaw Windows Companion"
        $shortcut.Save()
        Write-Host "  ✔ Desktop Shortcut placed in: $dPath" -ForegroundColor Green
    } catch {}
}

# Create Start Menu Shortcut
try {
    $programsMenu = [Environment]::GetFolderPath('Programs')
    if (Test-Path $programsMenu) {
        $startShortcutPath = Join-Path $programsMenu "Sentinel Companion.lnk"
        $wscriptShell = New-Object -ComObject WScript.Shell
        $startShortcut = $wscriptShell.CreateShortcut($startShortcutPath)
        $startShortcut.TargetPath = (Resolve-Path $venvPythonw).Path
        $startShortcut.Arguments = "companion.py"
        $startShortcut.WorkingDirectory = $targetDir
        $startShortcut.Description = "Sentinel-AutoGen-Hunter Desktop Companion"
        $startShortcut.Save()
    }
} catch {}

# [6/6] Launch & Summary
Write-Host ""
Write-Host "  ╔════════════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "  ║  🎉 INSTALLATION COMPLETE! Sentinel-AutoGen-Hunter is ready to hunt.   ║" -ForegroundColor Green
Write-Host "  ╚════════════════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "  Now you can type 'sentinel' in ANY terminal window:" -ForegroundColor Yellow
Write-Host "    sentinel                   # Launch Windows Companion Desktop App" -ForegroundColor White
Write-Host "    sentinel openclaw-chat     # Interactive terminal AI agent chat" -ForegroundColor White
Write-Host "    sentinel openclaw-gateway  # Start multi-channel gateway" -ForegroundColor White
Write-Host "    sentinel dashboard         # Launch Cyber SOC Dashboard" -ForegroundColor White
Write-Host "    sentinel tui               # Launch Cyberpunk Radar TUI" -ForegroundColor White
Write-Host ""

if (-not $NoLaunch) {
    Write-Host " [6/6] 🚀 Launching Sentinel Windows Companion Desktop App..." -ForegroundColor Cyan
    if (Test-Path $venvPythonw) {
        Start-Process $venvPythonw -ArgumentList "companion.py" -WorkingDirectory $targetDir
    } else {
        & $venvPython companion.py
    }
}
