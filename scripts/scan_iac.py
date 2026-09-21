"""Pre-deployment Shift-Left IaC Security Scanner script.

Audits Kubernetes manifests and Terraform templates, enforcing CIS benchmarks
before deployment in CI/CD pipelines.
"""
import os
import sys

# Ensure repository root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agents.tools.iac_analyzer import analyze_iac_content

FILES_TO_AUDIT = [
    ("k8s/deployment.yaml", "deployment.yaml"),
    ("terraform/main.tf", "main.tf"),
]


def main():
    print("=" * 60)
    print(" Sentinel-AutoGen-Hunter: Shift-Left IaC Pre-Deployment Scan")
    print("=" * 60)

    any_failed = False
    for path, filename in FILES_TO_AUDIT:
        if not os.path.exists(path):
            print(f"[-] Skipping {path} (file not found)")
            continue

        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        report = analyze_iac_content(content, filename)
        status_str = "[PASSED]" if report["passed"] else "[FAILED]"
        print(f"\nAudit: {path} -> {status_str} (Compliance Score: {report['compliance_score']}/100)")
        print(f"Summary: {report['summary']}")

        if not report["passed"]:
            any_failed = True
            for finding in report["findings"]:
                print(f"  [!] {finding['severity']}: {finding['title']} ({finding['rule_id']})")
                print(f"      Remediation: {finding['remediation']}")

    print("\n" + "=" * 60)
    if any_failed:
        print("[!] IaC Policy Gate: Violations detected. Deployment blocked.")
        sys.exit(1)
    else:
        print("[PASS] IaC Policy Gate: All manifests are CIS compliant. Safe to deploy.")
        sys.exit(0)


if __name__ == "__main__":
    main()
