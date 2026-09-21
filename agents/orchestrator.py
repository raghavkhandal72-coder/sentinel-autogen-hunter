"""FastAPI Threat Orchestrator exposing real-time telemetry endpoints and Prometheus SOC metrics."""

import logging

import uvicorn
from fastapi import BackgroundTasks, FastAPI, status
from pydantic import BaseModel, Field

from .autogen_swarm import AutoGenThreatSwarm

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - [%(name)s] - %(levelname)s - %(message)s"
)
logger = logging.getLogger("ThreatOrchestrator")

# ==============================================================================
# Prometheus SOC Metrics Definition (with Graceful Fallback)
# ==============================================================================
try:
    from prometheus_client import Counter, Gauge, make_asgi_app

    HAS_PROMETHEUS = True
except ImportError:
    HAS_PROMETHEUS = False

    class MetricMock:
        def __init__(self, name, description, labels=None):
            self.name = name
            self.description = description
            self.labels_keys = labels or []
            self.value = 0.0

        def inc(self, amount=1.0):
            self.value += amount

        def set(self, val):
            self.value = float(val)

        def labels(self, **kwargs):
            return self

    Counter = MetricMock
    Gauge = MetricMock

THREATS_DETECTED = Counter(
    "ai_threats_detected_total",
    "Total confirmed malicious threats classified by AI",
    labels=["threat_type", "risk_level"],
)
AI_CONFIDENCE = Gauge(
    "ai_threat_confidence_score",
    "Confidence score of the most recent autonomous threat evaluation",
)
LOGIN_ATTEMPTS = Counter(
    "ssh_login_attempts_total", "Total incoming authentication attempts monitored"
)
REMEDIATIONS_QUEUED = Counter(
    "threat_remediations_queued_total",
    "Total autonomous host firewall rules dispatched to DOCKER-USER chain",
    labels=["status"],
)

# Initialize FastAPI application
app = FastAPI(
    title="Sentinel-AutoGen-Hunter Orchestrator",
    description="Enterprise Multi-Agent Cloud-Native Threat Hunting Engine",
    version="1.0.0",
)

# Mount Prometheus metrics endpoint
if HAS_PROMETHEUS:
    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)
else:
    from fastapi.responses import PlainTextResponse

    @app.get("/metrics", response_class=PlainTextResponse)
    async def simulated_metrics():
        return (
            f"# HELP ai_threats_detected_total Total confirmed malicious threats\n"
            f"# TYPE ai_threats_detected_total counter\n"
            f"ai_threats_detected_total {THREATS_DETECTED.value}\n"
            f"# HELP ai_threat_confidence_score Confidence score\n"
            f"# TYPE ai_threat_confidence_score gauge\n"
            f"ai_threat_confidence_score {AI_CONFIDENCE.value}\n"
            f"# HELP ssh_login_attempts_total Total incoming attempts\n"
            f"# TYPE ssh_login_attempts_total counter\n"
            f"ssh_login_attempts_total {LOGIN_ATTEMPTS.value}\n"
        )


# Initialize multi-agent swarm
swarm = AutoGenThreatSwarm()


# ==============================================================================
# Pydantic Schemas
# ==============================================================================
class TelemetryPayload(BaseModel):
    service: str = Field(default="sshd", description="Target service generating log")
    event_type: str = Field(..., description="Classification of telemetry event")
    target_user: str | None = Field(default="root", description="Target account user")
    source_ip: str = Field(..., description="Originating IPv4 or IPv6 address")
    source_port: str | None = Field(
        default="22", description="Originating network port"
    )
    raw_log: str = Field(..., description="Raw log line captured by sensor")


def run_pipeline_task(payload_dict: dict):
    """Background task worker processing the AutoGen hunt workflow."""
    try:
        result = swarm.execute_hunt_pipeline(payload_dict)
        confidence = float(result.get("confidence_score", 0.0))
        AI_CONFIDENCE.set(confidence)

        if result.get("threat_detected"):
            analysis = result.get("analysis", {})
            remediation = result.get("remediation", {})

            threat_type = analysis.get("threat_type", "unknown")
            risk_level = (
                remediation.get("risk_level", "high") if remediation else "high"
            )

            THREATS_DETECTED.labels(
                threat_type=threat_type, risk_level=risk_level
            ).inc()

            if remediation and remediation.get("enforcement_queued"):
                REMEDIATIONS_QUEUED.labels(status="queued").inc()
            else:
                REMEDIATIONS_QUEUED.labels(status="rejected_or_unneeded").inc()
    except Exception as exc:
        logger.exception(f"Error processing background hunt pipeline: {exc}")


@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """Healthcheck endpoint for Kubernetes liveness/readiness probes."""
    return {
        "status": "healthy",
        "service": "sentinel-autogen-hunter",
        "engine": "Microsoft AutoGen + Sentinel",
        "mode": swarm.analyzer.mode,
    }


@app.post("/analyze", status_code=status.HTTP_202_ACCEPTED)
async def analyze_telemetry(
    payload: TelemetryPayload, background_tasks: BackgroundTasks
):
    """Receives parsed network telemetry and offloads multi-agent analysis to background queue."""
    LOGIN_ATTEMPTS.inc()
    payload_dict = payload.model_dump()
    background_tasks.add_task(run_pipeline_task, payload_dict)

    return {
        "status": "Analysis queued",
        "target_ip": payload.source_ip,
        "event_type": payload.event_type,
    }


@app.post("/analyze/sync", status_code=status.HTTP_200_OK)
async def analyze_telemetry_sync(payload: TelemetryPayload):
    """Synchronous endpoint primarily used for deterministic integration testing."""
    LOGIN_ATTEMPTS.inc()
    payload_dict = payload.model_dump()
    result = swarm.execute_hunt_pipeline(payload_dict)

    confidence = float(result.get("confidence_score", 0.0))
    AI_CONFIDENCE.set(confidence)
    if result.get("threat_detected"):
        analysis = result.get("analysis", {})
        remediation = result.get("remediation", {})
        threat_type = analysis.get("threat_type", "unknown")
        risk_level = remediation.get("risk_level", "high") if remediation else "high"
        THREATS_DETECTED.labels(threat_type=threat_type, risk_level=risk_level).inc()

    return result


# ==============================================================================
# Feature 1: Shift-Left DevSecOps IaC Scanner Endpoint
# ==============================================================================
class IaCScanRequest(BaseModel):
    content: str = Field(..., description="Raw Kubernetes YAML or Terraform HCL text")
    filename: str = Field(default="manifest.yaml", description="Manifest file name")


@app.post("/scan/iac", status_code=status.HTTP_200_OK)
async def scan_iac_manifest_endpoint(request: IaCScanRequest):
    """Pre-deployment static security scan for Kubernetes manifests and Terraform templates."""
    from .iac_scanner import IaCScannerAgent

    scanner = IaCScannerAgent()
    return scanner.analyze({"content": request.content, "filename": request.filename})


# ==============================================================================
# Feature 2: SQL-Based Cloud Security Posture Management (CSPM) Endpoints
# ==============================================================================
class CSPMQueryRequest(BaseModel):
    sql_query: str | None = Field(
        default=None, description="Direct read-only ANSI SQL query"
    )
    query_prompt: str | None = Field(
        default=None, description="Natural language security inquiry"
    )


@app.post("/cspm/query", status_code=status.HTTP_200_OK)
async def query_cspm_endpoint(request: CSPMQueryRequest):
    """Executes an ANSI SQL or natural-language posture evaluation against cloud assets."""
    from .cspm_engine import CSPMEngineAgent

    engine = CSPMEngineAgent()
    return engine.analyze(
        {"sql_query": request.sql_query, "query_prompt": request.query_prompt}
    )


@app.get("/cspm/posture", status_code=status.HTTP_200_OK)
async def get_cspm_posture_endpoint():
    """Returns high-level Cloud Security Posture metrics and CIS benchmark compliance score."""
    from .tools.cspm_sql import get_cspm_db

    return get_cspm_db().get_posture_summary()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
