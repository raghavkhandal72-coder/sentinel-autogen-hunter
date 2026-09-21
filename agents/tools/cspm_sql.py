"""SQL-Based Cloud Security Posture Management (CSPM) database & query engine.

Transforms multi-cloud infrastructure assets (Azure, Kubernetes, AWS) into
queryable SQL relational tables, enabling AI agents to detect posture drift,
excessive privileges, and compliance violations via ANSI SQL.
"""

import logging
import sqlite3
from typing import Any

logger = logging.getLogger("CSPMSqlEngine")

DEFAULT_ASSETS = [
    # Compliant assets
    (
        "vm-prod-orchestrator-01",
        "compute_vm",
        "azure",
        "eastus",
        0,
        1,
        1,
        0,
        "compliant",
    ),
    ("k8s-pod-sentinel-agent", "k8s_pod", "k8s", "eastus", 0, 1, 1, 0, "compliant"),
    (
        "st-threat-telemetry-vault",
        "storage_bucket",
        "azure",
        "eastus",
        0,
        1,
        1,
        0,
        "compliant",
    ),
    (
        "iam-role-least-privilege-secops",
        "iam_role",
        "azure",
        "global",
        0,
        0,
        1,
        0,
        "compliant",
    ),
    (
        "nsg-production-dmz-strict",
        "network_security_group",
        "azure",
        "eastus",
        0,
        1,
        1,
        0,
        "compliant",
    ),
    # Non-compliant / Drifted assets (Security Violations)
    (
        "vm-legacy-bastion-unpatched",
        "compute_vm",
        "azure",
        "westus",
        1,
        0,
        0,
        1,
        "non_compliant",
    ),
    (
        "st-unencrypted-backup-blob",
        "storage_bucket",
        "azure",
        "eastus",
        1,
        0,
        0,
        0,
        "non_compliant",
    ),
    (
        "k8s-pod-root-debug-shell",
        "k8s_pod",
        "k8s",
        "eastus",
        1,
        0,
        0,
        1,
        "non_compliant",
    ),
    (
        "iam-role-global-admin-no-mfa",
        "iam_role",
        "azure",
        "global",
        0,
        0,
        0,
        1,
        "non_compliant",
    ),
    (
        "nsg-any-any-open-ingress",
        "network_security_group",
        "azure",
        "westeurope",
        1,
        0,
        0,
        1,
        "non_compliant",
    ),
]


class CloudPostureDatabase:
    """Manages an in-memory or persistent SQLite asset inventory for continuous CSPM."""

    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self):
        """Creates the cloud asset graph schema and seeds benchmark data."""
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS cloud_assets (
                    id TEXT PRIMARY KEY,
                    asset_type TEXT NOT NULL,
                    cloud_provider TEXT NOT NULL,
                    region TEXT NOT NULL,
                    is_public_facing INTEGER NOT NULL,
                    is_encrypted INTEGER NOT NULL,
                    mfa_enforced INTEGER NOT NULL,
                    has_excessive_privilege INTEGER NOT NULL,
                    compliance_status TEXT NOT NULL
                )
            """)

            # Seed initial dataset if empty
            cursor = self.conn.execute("SELECT COUNT(*) FROM cloud_assets")
            if cursor.fetchone()[0] == 0:
                self.conn.executemany(
                    """
                    INSERT INTO cloud_assets (
                        id, asset_type, cloud_provider, region,
                        is_public_facing, is_encrypted, mfa_enforced,
                        has_excessive_privilege, compliance_status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    DEFAULT_ASSETS,
                )

    def execute_query(self, query: str) -> list[dict[str, Any]]:
        """Executes a read-only SQL posture query and returns serialized dictionaries."""
        # Enforce read-only querying to prevent database modification
        stripped = query.strip().upper()
        if not (stripped.startswith("SELECT") or stripped.startswith("WITH")):
            raise ValueError(
                "Only read-only SELECT queries are permitted on the CSPM posture database."
            )

        cursor = self.conn.execute(query)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def get_posture_summary(self) -> dict[str, Any]:
        """Calculates global Cloud Security Posture metrics and CIS benchmark score."""
        with self.conn:
            total_assets = self.conn.execute(
                "SELECT COUNT(*) FROM cloud_assets"
            ).fetchone()[0]
            compliant_assets = self.conn.execute(
                "SELECT COUNT(*) FROM cloud_assets WHERE compliance_status = 'compliant'"
            ).fetchone()[0]
            public_unencrypted = self.conn.execute(
                "SELECT COUNT(*) FROM cloud_assets WHERE is_public_facing = 1 AND is_encrypted = 0"
            ).fetchone()[0]
            admin_without_mfa = self.conn.execute(
                "SELECT COUNT(*) FROM cloud_assets WHERE has_excessive_privilege = 1 AND mfa_enforced = 0"
            ).fetchone()[0]

        posture_score = (
            round((compliant_assets / total_assets) * 100, 1)
            if total_assets > 0
            else 100.0
        )

        return {
            "total_assets_monitored": total_assets,
            "compliant_assets": compliant_assets,
            "non_compliant_assets": total_assets - compliant_assets,
            "cloud_posture_score": posture_score,
            "critical_risks": {
                "public_unencrypted_assets": public_unencrypted,
                "privileged_accounts_without_mfa": admin_without_mfa,
            },
        }


# Global singleton instance
_GLOBAL_CSPM_DB: CloudPostureDatabase | None = None


def get_cspm_db() -> CloudPostureDatabase:
    """Returns or initializes the global CSPM database."""
    global _GLOBAL_CSPM_DB
    if _GLOBAL_CSPM_DB is None:
        _GLOBAL_CSPM_DB = CloudPostureDatabase()
    return _GLOBAL_CSPM_DB
