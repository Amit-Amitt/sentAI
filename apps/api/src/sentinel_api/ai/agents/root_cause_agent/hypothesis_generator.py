from typing import Any, Dict, List
import structlog

from sentinel_api.ai.agents.root_cause_agent.schemas import RootCauseHypothesis

logger = structlog.get_logger(
    "sentinel_api.ai.agents.root_cause_agent.hypothesis_generator"
)


class HypothesisGenerator:
    """Evaluates logs, metrics, deployments, and tickets to formulate potential root causes."""

    def generate_hypotheses(
        self,
        normalized_evidence: List[Dict[str, Any]],
        correlations: Dict[str, Any],
    ) -> List[RootCauseHypothesis]:
        """Scans evidence for SRE keywords, triggering matched hypothesis models."""
        logger.info("Generating candidate root cause hypotheses")
        hypotheses: List[RootCauseHypothesis] = []

        deployments = [
            e for e in normalized_evidence if e["agent"] == "DEPLOYMENT"
        ]
        logs = [e for e in normalized_evidence if e["agent"] == "LOG"]
        metrics = [e for e in normalized_evidence if e["agent"] == "METRICS"]

        # 1. Bad Deployment Scenario
        if deployments:
            for dep in deployments:
                meta = dep["metadata"]
                svc = meta.get("service") or "unknown-service"
                ver = meta.get("version") or "unknown-version"

                desc = (
                    f"Recent deployment of {svc} ({ver}) correlates with the"
                    " incident timeline."
                )
                supporting = [
                    f"Deployment of {svc} ({ver}) at {dep['timestamp']}"
                ]

                matching_logs = [
                    l for l in logs if l["metadata"].get("service") == svc
                ]
                if matching_logs:
                    supporting.append(
                        f"Matching log errors found on {svc} post-deployment"
                    )

                matching_metrics = [
                    m for m in metrics if m["metadata"].get("service") == svc
                ]
                if matching_metrics:
                    supporting.append(
                        f"Metric anomalies detected on {svc} post-deployment"
                    )

                hypotheses.append(
                    RootCauseHypothesis(
                        id=f"h-dep-{svc}",
                        root_cause_type="BAD_DEPLOYMENT",
                        title=f"Bad Deployment of {svc}",
                        description=desc,
                        confidence=0.85
                        if matching_logs or matching_metrics
                        else 0.60,
                        supporting_evidence=supporting,
                        score=0.0,
                        timeline_consistency=1.0,
                    )
                )

        # 2. Database Overload Scenario
        db_keywords = [
            "db",
            "database",
            "postgres",
            "sql",
            "redis",
            "mongodb",
            "connection pool",
            "migration",
        ]
        db_evidence = [
            e
            for e in normalized_evidence
            if any(k in e["description"].lower() for k in db_keywords)
        ]
        if db_evidence:
            supporting = [
                f"Database-related issue: {e['description']} reported by"
                f" {e['agent']}"
                for e in db_evidence
            ]
            hypotheses.append(
                RootCauseHypothesis(
                    id="h-db-overload",
                    root_cause_type="DATABASE_OVERLOAD",
                    title="Database Overload / Connection Pool Exhaustion",
                    description=(
                        "Database performance degradation or connection pool"
                        " exhaustion preventing successful queries."
                    ),
                    confidence=0.80 if len(db_evidence) > 1 else 0.50,
                    supporting_evidence=supporting,
                    score=0.0,
                    timeline_consistency=1.0,
                )
            )

        # 3. Memory Leak Scenario
        mem_keywords = ["memory", "heap", "oom", "out of memory", "leak", "gc"]
        mem_evidence = [
            e
            for e in normalized_evidence
            if any(k in e["description"].lower() for k in mem_keywords)
        ]
        if mem_evidence:
            supporting = [
                f"Memory anomaly: {e['description']} reported by {e['agent']}"
                for e in mem_evidence
            ]
            hypotheses.append(
                RootCauseHypothesis(
                    id="h-mem-leak",
                    root_cause_type="MEMORY_LEAK",
                    title="Application Memory Leak / OOM Kill",
                    description=(
                        "High memory consumption leading to garbage collection"
                        " pauses or process termination."
                    ),
                    confidence=0.75,
                    supporting_evidence=supporting,
                    score=0.0,
                    timeline_consistency=1.0,
                )
            )

        # 4. Authentication Failure Scenario
        auth_keywords = [
            "auth",
            "login",
            "password",
            "token",
            "session",
            "mfa",
            "unauthorized",
        ]
        auth_evidence = [
            e
            for e in normalized_evidence
            if any(k in e["description"].lower() for k in auth_keywords)
        ]
        if auth_evidence:
            supporting = [
                f"Auth failure: {e['description']} reported by {e['agent']}"
                for e in auth_evidence
            ]
            hypotheses.append(
                RootCauseHypothesis(
                    id="h-auth-fail",
                    root_cause_type="AUTHENTICATION_FAILURE",
                    title="Authentication Service Failure",
                    description=(
                        "Authentication/MFA services failing to authenticate"
                        " user credentials or validate tokens."
                    ),
                    confidence=0.80 if len(auth_evidence) > 1 else 0.50,
                    supporting_evidence=supporting,
                    score=0.0,
                    timeline_consistency=1.0,
                )
            )

        if not hypotheses:
            hypotheses.append(
                RootCauseHypothesis(
                    id="h-unknown",
                    root_cause_type="UNKNOWN_INFRA_ISSUE",
                    title="Unknown Infrastructure Performance Issue",
                    description=(
                        "Unclassified incident showing performance"
                        " degradation or logs increase."
                    ),
                    confidence=0.40,
                    supporting_evidence=[
                        "Generic signal alerts received from monitoring systems"
                    ],
                    score=0.0,
                    timeline_consistency=0.5,
                )
            )

        return hypotheses
