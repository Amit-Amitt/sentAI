from typing import Any, Dict
import structlog

logger = structlog.get_logger(
    "sentinel_api.ai.agents.recommendation_agent.runbook_matcher"
)


class RunbookMatcher:
    """Matches incident root cause types with corresponding operational runbooks."""

    def match_runbook(self, root_cause: str) -> Dict[str, Any]:
        """Looks up runbooks by failure profile keywords, returning wikis or templates."""
        logger.info(f"Matching runbooks for root cause: {root_cause}")
        rc_upper = root_cause.upper()

        if "DEPLOY" in rc_upper:
            return {
                "runbook_id": "RB-DEP-102",
                "runbook_name": "Kubernetes Rolling Update and Rollback Playbook",
                "runbook_url": "https://wiki.internal.net/sre/runbooks/RB-DEP-102",
                "match_type": "EXACT",
            }
        elif "DATABASE" in rc_upper or "DB" in rc_upper:
            return {
                "runbook_id": "RB-DB-001",
                "runbook_name": (
                    "Database Connection Exhaustion Troubleshooting Guide"
                ),
                "runbook_url": "https://wiki.internal.net/sre/runbooks/RB-DB-001",
                "match_type": "EXACT",
            }
        elif "MEMORY" in rc_upper or "LEAK" in rc_upper or "OOM" in rc_upper:
            return {
                "runbook_id": "RB-MEM-043",
                "runbook_name": "OOM Killer / Heap Space Leak Triage Playbook",
                "runbook_url": "https://wiki.internal.net/sre/runbooks/RB-MEM-043",
                "match_type": "EXACT",
            }

        return {
            "runbook_id": "RB-GEN-999",
            "runbook_name": "Generic Incident Mitigation Guide",
            "runbook_url": "https://wiki.internal.net/sre/runbooks/RB-GEN-999",
            "match_type": "SUGGESTED_CREATION",
            "notes": (
                "No specific runbook match. Suggest creating a new runbook for"
                " this root cause profile."
            ),
        }
