from typing import Any, Dict
import structlog

logger = structlog.get_logger(
    "sentinel_api.ai.agents.recommendation_agent.playbook_selector"
)


class PlaybookSelector:
    """Retrieves operational steps for targeted recovery workflows."""

    def select_playbook(self, root_cause_type: str) -> Dict[str, Any]:
        """Maps root cause failure classifications to playbook lists."""
        logger.info(f"Selecting playbook for type: {root_cause_type}")

        if root_cause_type == "BAD_DEPLOYMENT":
            return {
                "playbook_id": "PB-DEPLOY-01",
                "steps": [
                    "1. Confirm release owner approvals.",
                    "2. Check target Kubernetes cluster context.",
                    "3. Initiate helm rollback or rollout undo.",
                    "4. Monitor pod availability rollout status.",
                ],
            }
        elif root_cause_type == "DATABASE_OVERLOAD":
            return {
                "playbook_id": "PB-DB-02",
                "steps": [
                    "1. Check primary DB CPU load.",
                    "2. Identify slow queries blocking connection pools.",
                    "3. Scale up DB connection capacity or read replicas.",
                    "4. Purge stale app caches to relieve query pressure.",
                ],
            }

        return {
            "playbook_id": "PB-GEN-99",
            "steps": [
                "1. Gather incident logs and metrics.",
                "2. Page domain engineering teams.",
                "3. Observe canary health post-restart.",
            ],
        }
