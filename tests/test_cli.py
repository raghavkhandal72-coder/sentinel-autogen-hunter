"""Tests for Sentinel-AutoGen-Hunter CLI and TUI components."""

import subprocess
import sys

from agents.sigma_engine import synthesize_universal_matrix
from cli.tui import print_mitre_table, print_radar_metrics, print_status_bar


def test_tui_rendering_functions(capsys):
    print_status_bar()
    out = capsys.readouterr().out
    assert "ZERO-TRUST" in out
    assert "SWARM" in out

    print_radar_metrics()
    out = capsys.readouterr().out
    assert "THREATS INTERCEPTED" in out

    print_mitre_table()
    out = capsys.readouterr().out
    assert "MITRE ATT&CK" in out


def test_cli_sigma_synthesis():
    res = synthesize_universal_matrix({
        "threat_type": "port_scan",
        "attacker_ip": "192.0.2.1",
        "target_asset": "corp-lb",
    })
    assert "sigma_yaml" in res["detection_rules"]
    assert "192.0.2.1" in res["detection_rules"]["sigma_yaml"]


def test_cli_execution_help():
    result = subprocess.run(
        [sys.executable, "-m", "cli.main", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "sentinel-hunter" in result.stdout
    assert "tui" in result.stdout
    assert "dashboard" in result.stdout
