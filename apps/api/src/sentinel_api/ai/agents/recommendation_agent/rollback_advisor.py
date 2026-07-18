from typing import Any, Dict, List
import structlog

logger = structlog.get_logger(
    "sentinel_api.ai.agents.recommendation_agent.rollback_advisor"
)


class RollbackAdvisor:
    """Generates commands, warnings, and manual steps for rolling back changes."""

    def get_rollback_advice(
        self, root_cause: str, affected_services: List[str]
    ) -> Dict[str, Any]:
        """Formulates specific rollback instructions based on root cause type."""
        logger.info("Advising on rollback strategies")
        svc = affected_services[0] if affected_services else "service"

        if "DEPLOY" in root_cause.upper():
            return {
                "rollback_command": (
                    f"helm rollback {svc}-release $(helm history"
                    f" {svc}-release | grep -v revision | tail -n 2 | head -n"
                    f" 1 | awk '{{print $1}}')"
                ),
                "difficulty": "Medium",
                "verification_steps": [
                    f"Check helm deployment history: helm history {svc}-release",
                    f"Verify Pod status: kubectl get pods -l app={svc}",
                    f"Monitor canary error rate for {svc} on the API Gateway",
                ],
            }
        elif "DATABASE" in root_cause.upper() or "DB" in root_cause.upper():
            return {
                "rollback_command": (
                    "migrate -path database/migrations -database $DB_URL down 1"
                ),
                "difficulty": "High",
                "verification_steps": [
                    (
                        "Verify current database migration version in"
                        " schema_migrations table"
                    ),
                    "Verify active database connection counts do not spike",
                    "Verify read/write replica sync lag is close to zero",
                ],
            }

        return {
            "rollback_command": f"kubectl rollout undo deployment/{svc}",
            "difficulty": "Low",
            "verification_steps": [
                (
                    f"Verify deployment revision was reverted: kubectl rollout"
                    f" history deployment/{svc}"
                ),
                f"Verify pod statuses are Running: kubectl get pods -l app={svc}",
            ],
        }
