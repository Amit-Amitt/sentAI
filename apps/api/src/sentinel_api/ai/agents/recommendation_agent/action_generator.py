from typing import Any, Dict, List
import structlog

from sentinel_api.ai.agents.recommendation_agent.schemas import (
    RecommendedAction,
)

logger = structlog.get_logger(
    "sentinel_api.ai.agents.recommendation_agent.action_generator"
)


class ActionGenerator:
    """Generates specific recovery actions tailored to the diagnosed root cause."""

    def generate_actions(
        self, root_cause: str, affected_services: List[str]
    ) -> List[RecommendedAction]:
        """Translates root cause types into recovery step listings."""
        logger.info(f"Generating recovery actions for root cause: {root_cause}")
        actions: List[RecommendedAction] = []

        rc_upper = root_cause.upper()
        svc = affected_services[0] if affected_services else "affected-service"

        if "DEPLOY" in rc_upper:
            actions.append(
                RecommendedAction(
                    id="act-rollback",
                    action_type="ROLLBACK",
                    title=f"Rollback {svc} Deployment",
                    description=(
                        f"Initiate rollback of {svc} to the last known stable"
                        f" deployment version."
                    ),
                    priority="Critical",
                    urgency="Critical",
                    execution_order=1,
                    estimated_impact=(
                        "Will eliminate the regression introduced in the bad"
                        " version."
                    ),
                    risk_level="Medium",
                    side_effects=[
                        "Brief traffic interruption during deployment transition"
                    ],
                )
            )
            actions.append(
                RecommendedAction(
                    id="act-review-config",
                    action_type="REVIEW_CONFIG",
                    title=f"Review {svc} Config",
                    description=(
                        f"Inspect environmental variables and secrets deployed"
                        f" in the bad version of {svc}."
                    ),
                    priority="High",
                    urgency="Medium",
                    execution_order=2,
                    estimated_impact=(
                        "Prevents repeating configuration errors in the future."
                    ),
                    risk_level="Low",
                    side_effects=[],
                )
            )

        elif "DATABASE" in rc_upper or "DB" in rc_upper:
            actions.append(
                RecommendedAction(
                    id="act-db-scale",
                    action_type="SCALE",
                    title="Increase Database Connections Limit",
                    description=(
                        "Temporarily scale DB connection pool size or spin up"
                        " read replica for database."
                    ),
                    priority="Critical",
                    urgency="Critical",
                    execution_order=1,
                    estimated_impact=(
                        "Relieves query queuing and database starvation issues."
                    ),
                    risk_level="High",
                    side_effects=[
                        "May lead to transient DB lock spikes during"
                        " configuration reload"
                    ],
                )
            )
            actions.append(
                RecommendedAction(
                    id="act-clear-cache",
                    action_type="CLEAR_CACHE",
                    title="Clear Application Caches",
                    description=(
                        "Clear stale entries in Redis or in-memory caches to"
                        " enforce clean DB fetch."
                    ),
                    priority="Medium",
                    urgency="Medium",
                    execution_order=2,
                    estimated_impact=(
                        "Reduces cache inconsistency and improves lookup speed."
                    ),
                    risk_level="Low",
                    side_effects=[],
                )
            )

        elif "MEMORY" in rc_upper or "LEAK" in rc_upper or "OOM" in rc_upper:
            actions.append(
                RecommendedAction(
                    id="act-restart",
                    action_type="RESTART",
                    title=f"Restart {svc} Container Instances",
                    description=(
                        f"Perform rolling restart of {svc} container instances"
                        f" to clear memory heap."
                    ),
                    priority="Critical",
                    urgency="Critical",
                    execution_order=1,
                    estimated_impact=(
                        "Instantly recovers free memory space, mitigating OOM"
                        " loop."
                    ),
                    risk_level="Low",
                    side_effects=["Brief service response tail latency increase"],
                )
            )
            actions.append(
                RecommendedAction(
                    id="act-scale-resources",
                    action_type="SCALE",
                    title=f"Increase memory limits for {svc}",
                    description=(
                        f"Temporarily bump CPU/Memory reservations for the"
                        f" {svc} pod config."
                    ),
                    priority="High",
                    urgency="High",
                    execution_order=2,
                    estimated_impact=(
                        "Provides a memory buffer while investigating heap leak"
                        " root cause."
                    ),
                    risk_level="Medium",
                    side_effects=["Increases infrastructure cloud billing costs"],
                )
            )

        elif "AUTH" in rc_upper:
            actions.append(
                RecommendedAction(
                    id="act-verify-credentials",
                    action_type="VERIFY_CREDENTIALS",
                    title="Check Auth Key Vault credentials sync",
                    description=(
                        "Verify auth key store secrets and token configurations"
                        " in KeyVault/Vault."
                    ),
                    priority="Critical",
                    urgency="Critical",
                    execution_order=1,
                    estimated_impact=(
                        "Restores correct token validation across authentication"
                        " steps."
                    ),
                    risk_level="Low",
                    side_effects=[],
                )
            )

        actions.append(
            RecommendedAction(
                id="act-notify-team",
                action_type="NOTIFY",
                title=f"Notify {svc} Engineering Team",
                description=(
                    f"Alert the primary service owner team of {svc} to join"
                    f" the triage war-room."
                ),
                priority="High",
                urgency="High",
                execution_order=len(actions) + 1,
                estimated_impact=(
                    "Brings developer domain expertise to resolve details."
                ),
                risk_level="Low",
                side_effects=[],
            )
        )

        actions.append(
            RecommendedAction(
                id="act-monitor",
                action_type="MONITOR",
                title="Monitor Recovery Metrics",
                description=(
                    "Continuously monitor system error rates, API latencies,"
                    " and service logs."
                ),
                priority="Medium",
                urgency="Medium",
                execution_order=len(actions) + 1,
                estimated_impact="Confirms resolution has mitigated user-facing errors.",
                risk_level="Low",
                side_effects=[],
            )
        )

        return actions
