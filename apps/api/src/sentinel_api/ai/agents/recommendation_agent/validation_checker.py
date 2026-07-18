from typing import List
import structlog

from sentinel_api.ai.agents.recommendation_agent.schemas import (
    ValidationCheck,
)

logger = structlog.get_logger(
    "sentinel_api.ai.agents.recommendation_agent.validation_checker"
)


class ValidationChecker:
    """Generates verification checks to run before triggering any mitigation steps."""

    def generate_validation_checks(
        self, root_cause_type: str, affected_services: List[str]
    ) -> List[ValidationCheck]:
        """Formulates validation checks based on failure profile types."""
        logger.info("Generating pre-execution validation checks")
        checks: List[ValidationCheck] = []
        svc = affected_services[0] if affected_services else "service"

        if root_cause_type == "BAD_DEPLOYMENT":
            checks.append(
                ValidationCheck(
                    title=f"Verify current deployment version of {svc}",
                    command_suggestion=(
                        f"kubectl get deployment {svc} -o"
                        f" jsonpath='{{.spec.template.spec.containers[0].image}}'"
                    ),
                    success_criteria=(
                        "Matches the recently deployed bad image version tags."
                    ),
                )
            )
            checks.append(
                ValidationCheck(
                    title="Confirm Kubernetes cluster write permissions",
                    command_suggestion="kubectl auth can-i update deployments",
                    success_criteria="yes",
                )
            )
        elif root_cause_type == "DATABASE_OVERLOAD":
            checks.append(
                ValidationCheck(
                    title="Verify primary database CPU latency health",
                    command_suggestion=(
                        "aws rds describe-db-instances"
                        " --db-instance-identifier primary-db"
                    ),
                    success_criteria=(
                        "Status is 'available' and CPU utilization is under"
                        " load limits."
                    ),
                )
            )
            checks.append(
                ValidationCheck(
                    title="Verify current active pool connections count",
                    command_suggestion=(
                        "psql -c 'SELECT count(*) FROM pg_stat_activity;'"
                    ),
                    success_criteria=(
                        "Returns count lower than connection pool max limits."
                    ),
                )
            )
        else:
            checks.append(
                ValidationCheck(
                    title="Check infrastructure health status",
                    command_suggestion="kubectl get nodes",
                    success_criteria="All target nodes report Ready status.",
                )
            )

        checks.append(
            ValidationCheck(
                title=f"Confirm ownership team of {svc}",
                command_suggestion=(
                    f"curl -s"
                    f" https://backstage.internal.net/api/catalog/entities/component/{svc}"
                    f" | jq '.spec.owner'"
                ),
                success_criteria="Returns a valid engineering team name handle.",
            )
        )

        return checks
