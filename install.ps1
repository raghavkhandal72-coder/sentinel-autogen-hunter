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

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "================================================================================" -ForegroundColor DarkGray
Write-Host "🛡️  Sentinel-AutoGen-Hunter + OpenClaw Gateway Installer (Windows)" -ForegroundColor Cyan
Write-Host "    Version: 1.4.0 | Architect: Raghav Khandal (@raghavkhandal72-coder)" -ForegroundColor DarkCyan
Write-Host "================================================================================" -ForegroundColor DarkGray
Write-Host ""

# 1. Check Python
$pythonCmd = $null
if (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonCmd = "python"
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
    $pythonCmd = "py -3"
}

if (-not $pythonCmd) {
    Write-Host "❌ Error: Python 3.10+ is required but not found on your PATH." -ForegroundColor Red
    Write-Host ">> You can install Python via Windows Package Manager:" -ForegroundColor Yellow
    Write-Host "   winget install Python.Python.3.11" -ForegroundColor White
    Write-Host ""
    Exit 1
}

$pyVer = & $pythonCmd --version 2>&1
Write-Host "✔ Python Detected: $pyVer" -ForegroundColor Green

# 2. Acquire Repository (git clone or download zip)
$repoDir = "sentinel-autogen-hunter"
if (-not (Test-Path "pyproject.toml")) {
    if (Get-Command git -ErrorAction SilentlyContinue) {
        Write-Host ">> Cloning Sentinel-AutoGen-Hunter from GitHub..." -ForegroundColor DarkCyan
        git clone https://github.com/raghavkhandal72-coder/sentinel-autogen-hunter.git
        Set-Location $repoDir
    } else {
        Write-Host ">> Git not detected. Downloading source release bundle..." -ForegroundColor DarkCyan
        $zipUrl = "https://github.com/raghavkhandal72-coder/sentinel-autogen-hunter/archive/refs/heads/main.zip"
        $zipFile = "sentinel-main.zip"
        Invoke-WebRequest -Uri $zipUrl -OutFile $zipFile
        Expand-Archive -Path $zipFile -DestinationPath "." -Force
        Remove-Item $zipFile
        Set-Location "sentinel-autogen-hunter-main"
    }
}

# 3. Setup Virtual Environment
Write-Host ">> Initializing isolated virtual environment (.venv)..." -ForegroundColor DarkCyan
if (-not (Test-Path ".venv")) {
    & $pythonCmd -m venv .venv
}

$venvPython = ".\.venv\Scripts\python.exe"
$venvPip = ".\.venv\Scripts\pip.exe"

# 4. Install Dependencies
Write-Host ">> Installing production dependencies & OpenClaw engine..." -ForegroundColor DarkCyan
& $venvPip install --upgrade pip -q
if (Test-Path "requirements.txt") {
    & $venvPip install -r requirements.txt -q
}
& $venvPip install -e . -q

# 5. Run Verification Self-Test
Write-Host ">> Running Zero-Trust Verification Test Suite (97 Tests)..." -ForegroundColor DarkCyan
& $venvPython -m pytest tests/ -q
if ($LASTEXITCODE -eq 0) {
    Write-Host "✔ All 97 Tests Verified & Passing Cleanly!" -ForegroundColor Green
} else {
    Write-Host "⚠️ Tests completed with non-zero exit code, continuing setup..." -ForegroundColor Yellow
}

# 6. Create Desktop Shortcut for Sentinel Windows Companion
try {
    $desktopPath = [System.Environment]::GetFolderPath([System.Environment+SpecialFolder]::Desktop)
    $shortcutPath = Join-Path $desktopPath "Sentinel Companion.lnk"
    $wscriptShell = New-Object -ComObject WScript.Shell
    $shortcut = $wscriptShell.CreateShortcut($shortcutPath)
    $shortcut.TargetPath = (Resolve-Path $venvPython).Path
    $shortcut.Arguments = "companion.py"
    $shortcut.WorkingDirectory = (Get-Location).Path
    $shortcut.Description = "Sentinel-AutoGen-Hunter + OpenClaw Windows Companion"
    $shortcut.Save()
    Write-Host "✔ Desktop Shortcut created: 'Sentinel Companion'" -ForegroundColor Green
} catch {
    # Non-fatal if shortcut cannot be written
}

Write-Host ""
Write-Host "================================================================================" -ForegroundColor DarkGray
Write-Host "🎉 Installation Complete! Sentinel-AutoGen-Hunter is ready to hunt." -ForegroundColor Green
Write-Host ""
Write-Host "Quick Launch Commands:" -ForegroundColor Yellow
Write-Host "  .\.venv\Scripts\activate" -ForegroundColor White
Write-Host "  python companion.py             # Launch Windows Companion Desktop App" -ForegroundColor White
Write-Host "  python -m cli.main openclaw-chat # Talk with OpenClaw Agent in Terminal" -ForegroundColor White
Write-Host "  python -m cli.main openclaw-gateway # Start OpenClaw Multi-Channel Gateway" -ForegroundColor White
Write-Host "  python -m cli.main dashboard    # Launch Cyber SOC UI (http://localhost:8000/dashboard)" -ForegroundColor White
Write-Host "  python -m cli.main tui          # Launch Cyberpunk Terminal Radar" -ForegroundColor White
Write-Host "================================================================================" -ForegroundColor DarkGray
Write-Host ""

if (-not $NoLaunch) {
    Write-Host "[*] Launching Sentinel Windows Companion Desktop App..." -ForegroundColor Cyan
    & $venvPython companion.py
}
