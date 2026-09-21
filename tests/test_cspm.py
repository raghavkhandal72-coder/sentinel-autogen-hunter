"""Unit tests for SQL-Based Cloud Security Posture Management (CSPM)."""

import pytest

from agents.cspm_engine import CSPMEngineAgent
from agents.tools.cspm_sql import CloudPostureDatabase, get_cspm_db


def test_cspm_database_initialization():
    """Verify CSPM database seeds default assets accurately."""
    db = CloudPostureDatabase(":memory:")
    summary = db.get_posture_summary()

    assert summary["total_assets_monitored"] >= 10
    assert summary["compliant_assets"] >= 5
    assert summary["non_compliant_assets"] >= 5
    assert 0 <= summary["cloud_posture_score"] <= 100


def test_cspm_sql_query_execution():
    """Verify executing ANSI SQL queries against cloud assets."""
    db = get_cspm_db()
    results = db.execute_query(
        "SELECT id, asset_type, region FROM cloud_assets WHERE compliance_status = 'non_compliant'"
    )
    assert len(results) >= 5
    assert all("id" in row and "asset_type" in row for row in results)


def test_cspm_query_prevent_mutation():
    """Verify non-read-only queries (DROP, DELETE, UPDATE) are strictly blocked."""
    db = get_cspm_db()
    with pytest.raises(ValueError, match="Only read-only SELECT queries are permitted"):
        db.execute_query("DELETE FROM cloud_assets")

    with pytest.raises(ValueError, match="Only read-only SELECT queries are permitted"):
        db.execute_query("DROP TABLE cloud_assets")


def test_cspm_engine_agent_analysis():
    """Verify CSPMEngineAgent translates prompt to SQL and evaluates posture."""
    agent = CSPMEngineAgent()
    result = agent.analyze(
        {"query_prompt": "Show me all unencrypted public assets in the eastus region"}
    )

    assert result["success"] is True
    assert "sql_executed" in result
    assert "global_posture_summary" in result
    assert result["records_found"] >= 1
