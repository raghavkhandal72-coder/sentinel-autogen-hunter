"""Tests for Cyber SOC Operations Dashboard UI."""

import asyncio

from agents.orchestrator import serve_dashboard_ui, serve_install_ui


def test_dashboard_endpoint_serves_html():
    response = asyncio.run(serve_dashboard_ui())
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    content = response.body.decode("utf-8")
    assert "SENTINEL" in content
    assert "Universal Multi-SIEM Sigma Transpiler" in content
    assert "Canary Honeytoken Deception" in content
    assert "Human-in-the-Loop" in content
    assert "MITRE ATT&CK Real-Time Heatmap" in content


def test_install_endpoint_serves_html():
    response = asyncio.run(serve_install_ui())
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    content = response.body.decode("utf-8")
    assert "Install Sentinel-AutoGen-Hunter" in content
    assert "Desktop Apps" in content
    assert "One-Liner" in content
    assert "install.ps1" in content
    assert "install.sh" in content
