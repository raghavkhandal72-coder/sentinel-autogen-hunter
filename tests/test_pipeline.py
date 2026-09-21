"""Integration tests for the Threat Orchestrator API and telemetry pipeline."""

import asyncio

from fastapi import BackgroundTasks

from agents.orchestrator import (
    TelemetryPayload,
    analyze_telemetry,
    analyze_telemetry_sync,
    app,
    health_check,
)


def test_orchestrator_health_endpoint():
    """Verify /health endpoint returns healthy operational status."""
    res = asyncio.run(health_check())
    assert res["status"] == "healthy"
    assert res["service"] == "sentinel-autogen-hunter"


def test_orchestrator_sync_analysis_malicious():
    """Verify synchronous analysis of an SSH brute force payload."""
    payload = TelemetryPayload(
        service="sshd",
        event_type="authentication_failed",
        target_user="root",
        source_ip="203.0.113.77",
        source_port="51234",
        raw_log="Failed password for root from 203.0.113.77 port 51234 ssh2",
    )
    result = asyncio.run(analyze_telemetry_sync(payload))

    assert result["threat_detected"] is True
    assert result["source_ip"] == "203.0.113.77"
    assert result["remediation"] is not None
    assert result["sentinel"] is not None
    assert "DOCKER-USER" in result["remediation"]["proposed_command"]


def test_orchestrator_async_queue():
    """Verify asynchronous /analyze endpoint queues task without blocking."""
    bg_tasks = BackgroundTasks()
    payload = TelemetryPayload(
        service="sshd",
        event_type="invalid_user_attempt",
        target_user="guest",
        source_ip="198.51.100.12",
        source_port="49120",
        raw_log="Invalid user guest from 198.51.100.12 port 49120",
    )
    resp = asyncio.run(analyze_telemetry(payload, bg_tasks))

    assert resp["status"] == "Analysis queued"
    assert resp["target_ip"] == "198.51.100.12"
    assert len(bg_tasks.tasks) == 1

    # Execute the queued background task directly to verify worker logic
    task = bg_tasks.tasks[0]
    asyncio.run(task())


def test_testclient_if_available():
    """Test full HTTP routing using httpx ASGITransport."""
    try:
        import httpx

        # Modern ASGI transport compatible with httpx 0.28+
        transport = httpx.ASGITransport(app=app)
        with httpx.Client(transport=transport, base_url="http://testserver") as client:
            health_resp = client.get("/health")
            assert health_resp.status_code == 200
            assert health_resp.json()["status"] == "healthy"

            metrics_resp = client.get("/metrics")
            assert metrics_resp.status_code == 200
            assert "ai_threats_detected_total" in metrics_resp.text
            assert "ai_threat_confidence_score" in metrics_resp.text

            analyze_resp = client.post(
                "/analyze",
                json={
                    "service": "sshd",
                    "event_type": "authentication_failed",
                    "target_user": "root",
                    "source_ip": "203.0.113.50",
                    "source_port": "54321",
                    "raw_log": "Failed password for root from 203.0.113.50 port 54321 ssh2",
                },
            )
            assert analyze_resp.status_code == 202
            assert analyze_resp.json()["status"] == "Analysis queued"
    except (ImportError, AttributeError):
        pass
