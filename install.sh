#!/usr/bin/env bash
# ==============================================================================
# Sentinel-AutoGen-Hunter Cross-Platform One-Line Installer
# ==============================================================================

set -e

echo ""
echo "🛡️  Installing Sentinel-AutoGen-Hunter (Autonomous Threat Hunter)..."
echo "================================================================================"

if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is required but not installed."
    exit 1
fi

echo "✔ Python detected: $(python3 --version)"

# Clone if not already in directory
if [ ! -f "pyproject.toml" ]; then
    echo ">> Cloning repository from GitHub..."
    git clone https://github.com/raghavkhandal72-coder/sentinel-autogen-hunter.git
    cd sentinel-autogen-hunter
fi

echo ">> Creating isolated virtual environment (.venv)..."
python3 -m venv .venv
source .venv/bin/activate

echo ">> Installing dependencies..."
pip install --upgrade pip -q
pip install -r requirements.txt -q

echo ">> Running self-test suite (67 tests)..."
python -m pytest tests/ -q

echo ""
echo "================================================================================"
echo "🎉 Installation Complete! Sentinel-AutoGen-Hunter is ready."
echo ""
echo "Quick Commands:"
echo "  source .venv/bin/activate"
echo "  python -m cli.main tui        # Launch Cyberpunk Terminal Radar"
echo "  python -m cli.main dashboard  # Launch Web SOC UI (http://localhost:8000/dashboard)"
echo "================================================================================"
echo ""
