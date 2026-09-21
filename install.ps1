# ==============================================================================
# Sentinel-AutoGen-Hunter Windows PowerShell Installer
# ==============================================================================

Write-Host ""
Write-Host "🛡️  Installing Sentinel-AutoGen-Hunter (Windows)..." -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor DarkGray

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Error: Python 3 is required but not installed or not on PATH." -ForegroundColor Red
    Exit 1
}

Write-Host "✔ Python detected: $(python --version)" -ForegroundColor Green

if (-not (Test-Path "pyproject.toml")) {
    Write-Host ">> Cloning repository from GitHub..." -ForegroundColor DarkCyan
    git clone https://github.com/raghavkhandal72-coder/sentinel-autogen-hunter.git
    Set-Location sentinel-autogen-hunter
}

Write-Host ">> Creating virtual environment (.venv)..." -ForegroundColor DarkCyan
python -m venv .venv
& .\.venv\Scripts\Activate.ps1

Write-Host ">> Installing dependencies..." -ForegroundColor DarkCyan
pip install --upgrade pip -q
pip install -r requirements.txt -q

Write-Host ">> Running verification suite (67 tests)..." -ForegroundColor DarkCyan
python -m pytest tests/ -q

Write-Host ""
Write-Host "================================================================================" -ForegroundColor DarkGray
Write-Host "🎉 Installation Complete! Sentinel-AutoGen-Hunter is ready." -ForegroundColor Green
Write-Host ""
Write-Host "Quick Commands:" -ForegroundColor Yellow
Write-Host "  .\.venv\Scripts\activate"
Write-Host "  python -m cli.main tui        # Launch Cyberpunk Terminal Radar"
Write-Host "  python -m cli.main dashboard  # Launch Web SOC UI (http://localhost:8000/dashboard)"
Write-Host "================================================================================" -ForegroundColor DarkGray
Write-Host ""
