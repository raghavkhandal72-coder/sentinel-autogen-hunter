# ==============================================================================
# Sentinel-AutoGen-Hunter Windows Quickstart Script
# ==============================================================================

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " Initializing Sentinel-AutoGen-Hunter Workspace           " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Check Python installation
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Error "Python 3.10+ is required but not found in PATH."
    exit 1
}
Write-Host "[✓] Detected Python: $pythonVersion" -ForegroundColor Green

# 2. Copy .env if not exists
if (-not (Test-Path ".env")) {
    Write-Host "[+] Creating local .env configuration from .env.example..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
}

# 3. Create actions directory
if (-not (Test-Path "actions")) {
    New-Item -ItemType Directory -Path "actions" -Force | Out-Null
}

Write-Host "`nEnvironment is prepared." -ForegroundColor Green
Write-Host "To execute tests:" -ForegroundColor White
Write-Host "  python -m pytest tests/ -v`n" -ForegroundColor Yellow
Write-Host "To run the AI Orchestrator locally:" -ForegroundColor White
Write-Host "  python -m uvicorn agents.orchestrator:app --reload --port 8000`n" -ForegroundColor Yellow
