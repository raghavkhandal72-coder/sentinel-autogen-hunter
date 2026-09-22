#!/usr/bin/env bash
# ==============================================================================
# Sentinel-AutoGen-Hunter macOS & Linux 1-Liner Installer
# Powered by OpenClaw Multi-Channel Gateway & Zero-Trust Defense Suite
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/raghavkhandal72-coder/sentinel-autogen-hunter/main/install.sh | bash
# ==============================================================================

set -e

echo ""
echo "================================================================================"
echo "🛡️  Sentinel-AutoGen-Hunter + OpenClaw Gateway Installer (Unix/macOS/Linux)"
echo "    Version: 1.4.0 | Architect: Raghav Khandal (@raghavkhandal72-coder)"
echo "================================================================================"
echo ""

# 1. Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3.10+ is required but not installed."
    echo ">> Please install Python 3 using your package manager (e.g., brew install python, apt install python3 python3-venv)"
    exit 1
fi

echo "✔ Python detected: $(python3 --version)"

# 2. Acquire Repository
REPO_DIR="sentinel-autogen-hunter"
if [ ! -f "pyproject.toml" ]; then
    if command -v git &> /dev/null; then
        echo ">> Cloning Sentinel-AutoGen-Hunter from GitHub..."
        git clone https://github.com/raghavkhandal72-coder/sentinel-autogen-hunter.git
        cd "$REPO_DIR"
    else
        echo ">> Git not detected. Downloading source release bundle..."
        curl -fsSL https://github.com/raghavkhandal72-coder/sentinel-autogen-hunter/archive/refs/heads/main.tar.gz | tar -xz
        cd sentinel-autogen-hunter-main
    fi
fi

# 3. Virtual Environment
echo ">> Initializing isolated virtual environment (.venv)..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

source .venv/bin/activate

# 4. Dependencies
echo ">> Installing production dependencies & OpenClaw engine..."
pip install --upgrade pip -q
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt -q
fi
pip install -e . -q

# 5. Verification Suite
echo ">> Running Zero-Trust Verification Test Suite (97 Tests)..."
python -m pytest tests/ -q || echo "⚠️ Tests finished with non-zero exit code, continuing setup..."

echo ""
echo "================================================================================"
echo "🎉 Installation Complete! Sentinel-AutoGen-Hunter is ready to hunt."
echo ""
echo "Quick Commands:"
echo "  source .venv/bin/activate"
echo "  python companion.py             # Launch Companion Desktop App (GUI)"
echo "  python -m cli.main openclaw-chat # Talk with OpenClaw Agent in Terminal"
echo "  python -m cli.main openclaw-gateway # Start OpenClaw Multi-Channel Gateway"
echo "  python -m cli.main dashboard    # Launch Cyber SOC UI (http://localhost:8000/dashboard)"
echo "  python -m cli.main tui          # Launch Cyberpunk Terminal Radar"
echo "================================================================================"
echo ""
