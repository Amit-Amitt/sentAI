from typing import Any, Dict, List
import structlog

from sentinel_api.ai.agents.deployment_agent.schemas import DeploymentEvent

logger = structlog.get_logger("sentinel_api.ai.agents.deployment_agent.release_analyzer")


class ReleaseAnalyzer:
    """Evaluates release sizes, breaking changes, and migration risks."""

    def analyze_releases(
        self, events: List[DeploymentEvent]
    ) -> Dict[str, Dict[str, Any]]:
        """Calculates a risk score for each deployment based on metadata."""
        logger.info("Analyzing release profiles and metadata")
        risks = {}

        for ev in events:
            details = ev.details

            commits = details.get("commits") or []
            if isinstance(commits, str):
                commits = [commits]

            has_breaking = (
                details.get("breaking")
                or details.get("is_breaking")
                or any("breaking" in str(c).lower() for c in commits)
                or "breaking" in str(details.get("notes") or "").lower()
            )

            has_migration = (
                ev.change_type == "DB"
                or details.get("migration")
                or details.get("has_migration")
                or any("migration" in str(c).lower() for c in commits)
            )

            commits_count = int(details.get("commits_count") or len(commits) or 1)
            files_changed = int(details.get("files_changed") or 0)

            size_label = "Small"
            if commits_count > 10 or files_changed > 20:
                size_label = "Large"
            elif commits_count > 3 or files_changed > 5:
                size_label = "Medium"

            risk_score = 0.1
            reasons = []
            if has_breaking:
                risk_score += 0.5
                reasons.append("Contains breaking changes")
            if has_migration:
                risk_score += 0.3
                reasons.append("Includes database migrations")
            if size_label == "Large":
                risk_score += 0.2
                reasons.append("Large deployment size")
            elif size_label == "Medium":
                risk_score += 0.1
                reasons.append("Medium deployment size")

            risk_score = min(1.0, risk_score)

            risks[ev.deployment_id] = {
                "deployment_id": ev.deployment_id,
                "has_breaking": bool(has_breaking),
                "has_migration": bool(has_migration),
                "size": size_label,
                "risk_score": round(risk_score, 2),
                "reasons": reasons,
            }

        return risks
