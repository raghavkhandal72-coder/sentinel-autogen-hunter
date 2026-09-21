# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Zero-Trust Security Philosophy

Sentinel-AutoGen-Hunter is designed under strict Zero-Trust architectural principles:
1. **Least Privilege Runtime**: Containers execute under unprivileged users (`ai_user`, UID 10001).
2. **Network Isolation**: Direct inter-container communication is restricted to dedicated bridge networks.
3. **Command Sanitization**: AI-generated firewall suggestions are never executed dynamically with shell privileges. They are validated against strict IP/CIDR regex patterns and queued into an append-only FIFO log consumed by a dedicated host-level enforcer.
4. **Rollback Requirement**: Every proactive remediation directive must generate an idempotent rollback command to prevent production network isolation or false positives.

## Reporting a Vulnerability

If you discover a security vulnerability within this project, please send an email to security@sentinel-autogen.local or open a private advisory on GitHub.

Please include:
- Description of the vulnerability.
- Steps to reproduce or proof-of-concept.
- Potential impact under enterprise deployment.

All valid reports will be acknowledged within 24 hours and patched within 72 hours.
