"""Cloud Security Posture Management (CSPM) Agent powered by SQL asset analytics."""

from typing import Any

from .base_agent import BaseAgent
from .tools.cspm_sql import get_cspm_db

CSPM_SYSTEM_PROMPT = """You are a Principal Cloud Security Posture Management (CSPM) Architect.
You convert security inquiries and compliance requirements into ANSI SQL queries executed against the cloud asset database.

DATABASE SCHEMA (table: cloud_assets):
- id (TEXT, primary key, asset name/arn)
- asset_type (TEXT, e.g. 'compute_vm', 'storage_bucket', 'k8s_pod', 'iam_role', 'network_security_group')
- cloud_provider (TEXT, e.g. 'azure', 'k8s', 'aws')
- region (TEXT, e.g. 'eastus', 'westeurope')
- is_public_facing (INTEGER: 0 or 1)
- is_encrypted (INTEGER: 0 or 1)
- mfa_enforced (INTEGER: 0 or 1)
- has_excessive_privilege (INTEGER: 0 or 1)
- compliance_status (TEXT: 'compliant' or 'non_compliant')

INSTRUCTIONS:
1. Formulate a clean read-only SELECT SQL query matching the user's security inquiry.
2. Formulate a 1-sentence risk explanation.
3. You must respond ONLY with a valid JSON object matching the schema below.

REQUIRED JSON SCHEMA:
{
  "sql_query": string,
  "risk_hypothesis": string,
  "target_cis_control": string
}
"""


class CSPMEngineAgent(BaseAgent):
    """Executes SQL-based posture evaluations to detect cloud asset drift and misconfigurations."""

    def __init__(self, model: str = "gpt-4o"):
        super().__init__(name="CSPMEngineAgent", model=model)
        self.db = get_cspm_db()

    def analyze(self, data: dict[str, Any]) -> dict[str, Any]:
        """Analyzes cloud asset posture via explicit SQL query or natural-language query prompt."""
        explicit_sql = data.get("sql_query")
        prompt_text = data.get("query_prompt", "Find all public unencrypted assets")

        if explicit_sql:
            sql_to_run = explicit_sql
            hypothesis = "Direct SecOps ANSI SQL Execution"
            cis_control = "Custom Posture Audit"
        else:
            llm_result = self._call_llm(CSPM_SYSTEM_PROMPT, prompt_text)
            sql_to_run = llm_result.get(
                "sql_query",
                "SELECT * FROM cloud_assets WHERE is_public_facing = 1 AND is_encrypted = 0",
            )
            hypothesis = llm_result.get(
                "risk_hypothesis", "Detecting exposed unencrypted infrastructure"
            )
            cis_control = llm_result.get(
                "target_cis_control", "CIS Cloud Control 3.1 - Data Protection"
            )

        try:
            records: list[dict[str, Any]] = self.db.execute_query(sql_to_run)
            success = True
            error_message = None
        except Exception as exc:
            records = []
            success = False
            error_message = str(exc)

        summary = self.db.get_posture_summary()

        return {
            "success": success,
            "sql_executed": sql_to_run,
            "risk_hypothesis": hypothesis,
            "cis_control": cis_control,
            "records_found": len(records),
            "violating_assets": records,
            "global_posture_summary": summary,
            "error": error_message,
        }
