"""Unit tests for the Shift-Left IaC Pre-Deployment Security Scanner."""

from agents.iac_scanner import IaCScannerAgent
from agents.tools.iac_analyzer import analyze_iac_content


def test_k8s_manifest_violations_detected():
    """Verify scanner catches critical Kubernetes misconfigurations."""
    insecure_k8s = """
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: vulnerable-app
    spec:
      template:
        spec:
          hostNetwork: true
          containers:
          - name: app
            image: nginx
            securityContext:
              privileged: true
              runAsUser: 0
              allowPrivilegeEscalation: true
    """
    report = analyze_iac_content(insecure_k8s, "insecure_deployment.yaml")
    assert report["passed"] is False
    assert report["summary"]["critical"] >= 2  # privileged + hostNetwork
    assert report["summary"]["high"] >= 1  # runAsUser 0 / allowPrivilegeEscalation
    assert report["compliance_score"] < 50


def test_k8s_manifest_hardened_passed():
    """Verify compliant Kubernetes deployment passes validation."""
    hardened_k8s = """
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: secure-app
    spec:
      template:
        spec:
          securityContext:
            runAsNonRoot: true
            runAsUser: 10001
          containers:
          - name: app
            image: app:v1.0
            securityContext:
              privileged: false
              allowPrivilegeEscalation: false
              readOnlyRootFilesystem: true
            resources:
              limits:
                cpu: "500m"
                memory: "256Mi"
    """
    report = analyze_iac_content(hardened_k8s, "hardened_deployment.yaml")
    assert report["passed"] is True
    assert report["summary"]["critical"] == 0
    assert report["compliance_score"] >= 80


def test_terraform_open_ingress_detected():
    """Verify scanner catches public 0.0.0.0/0 ingress on sensitive ports."""
    insecure_tf = """
    resource "aws_security_group" "allow_all" {
      name = "allow_all"
      ingress {
        from_port   = 22
        to_port     = 22
        protocol    = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
      }
    }
    """
    report = analyze_iac_content(insecure_tf, "main.tf")
    assert report["passed"] is False
    assert any(f["rule_id"] == "TF-001" for f in report["findings"])


def test_iac_scanner_agent_remediation():
    """Verify IaCScannerAgent formats automated patch recommendation."""
    agent = IaCScannerAgent()
    data = {
        "filename": "pod.yaml",
        "content": "apiVersion: v1\nkind: Pod\nspec:\n  containers:\n  - name: test\n    securityContext:\n      privileged: true\n",
    }
    result = agent.analyze(data)
    assert result["status"] == "BLOCKED_BY_POLICY"
    assert "agent_remediation" in result
    assert "suggested_patch" in result["agent_remediation"]
