"""Tests for MITRE ATT&CK Matrix Navigator & Coverage Mapper."""

from agents.mitre_mapper import (
    export_mitre_navigator_layer,
    get_mitre_coverage_matrix,
    render_ascii_matrix,
)


def test_mitre_coverage_matrix():
    cov = get_mitre_coverage_matrix()
    assert cov["total_techniques_mapped"] >= 20
    assert cov["covered_tactics_count"] >= 10
    assert cov["tactical_coverage_score"] > 80.0
    assert "initial-access" in cov["tactics"]
    assert "execution" in cov["tactics"]
    assert "privilege-escalation" in cov["tactics"]


def test_export_mitre_navigator_layer():
    layer = export_mitre_navigator_layer()
    assert layer["versions"]["navigator"] == "4.5"
    assert layer["domain"] == "enterprise-attack"
    assert len(layer["techniques"]) >= 20
    for tech in layer["techniques"]:
        assert "techniqueID" in tech
        assert "score" in tech
        assert tech["score"] in [60, 100]


def test_render_ascii_matrix():
    matrix_str = render_ascii_matrix()
    assert "[+] SENTINEL-AUTOGEN-HUNTER : MITRE ATT&CK MATRIX COVERAGE" in matrix_str
    assert "INITIAL-ACCESS" in matrix_str
    assert "PRIVILEGE-ESCALATION" in matrix_str
    assert "Active Techniques Mapped" in matrix_str
