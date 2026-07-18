from typing import Any, Dict
import structlog

from sentinel_api.app.reporting.schemas import RecoveryPlanSection

logger = structlog.get_logger("sentinel_api.app.reporting.recovery_formatter")


class RecoveryFormatter:
    """Formats checklists, validation commands, and monitoring plans for recovery."""

    def format_recovery_plan(
        self, recommendation_output: Dict[str, Any]
    ) -> RecoveryPlanSection:
        """Structures pre-checks, mitigation orders, and watch metrics."""
        logger.info("Formatting incident recovery plan details")

        checklist = []
        actions = recommendation_output.get("recommended_actions") or []
        for act in actions:
            act_dict = act if isinstance(act, dict) else act.model_dump()
            checklist.append(
                f"[{act_dict.get('execution_order')}] {act_dict.get('title')}:"
                f" {act_dict.get('description')}"
            )

        val_checks = recommendation_output.get("validation_checklist") or []
        val_steps = []
        for chk in val_checks:
            chk_dict = chk if isinstance(chk, dict) else chk.model_dump()
            val_steps.append(chk_dict)

        mon_plan = recommendation_output.get("recovery_monitoring_plan") or {}
        mon_plan_dict = (
            mon_plan if isinstance(mon_plan, dict) else mon_plan.model_dump()
        )

        return RecoveryPlanSection(
            recovery_checklist=checklist,
            validation_steps=val_steps,
            monitoring_plan=mon_plan_dict,
        )
