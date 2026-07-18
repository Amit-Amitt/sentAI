import time
from typing import Any, Dict, List
import structlog

from sentinel_api.ai.agents.root_cause_agent.confidence_engine import (
    ConfidenceEngine,
)
from sentinel_api.ai.agents.root_cause_agent.conflict_resolver import (
    ConflictResolver,
)
from sentinel_api.ai.agents.root_cause_agent.correlation_engine import (
    CorrelationEngine,
)
from sentinel_api.ai.agents.root_cause_agent.evidence_collector import (
    EvidenceCollector,
)
from sentinel_api.ai.agents.root_cause_agent.explanation_generator import (
    ExplanationGenerator,
)
from sentinel_api.ai.agents.root_cause_agent.hypothesis_generator import (
    HypothesisGenerator,
)
from sentinel_api.ai.agents.root_cause_agent.hypothesis_ranker import (
    HypothesisRanker,
)
from sentinel_api.ai.agents.root_cause_agent.schemas import (
    RootCauseAgentOutput,
)
from sentinel_api.ai.agents.root_cause_agent.timeline_analyzer import (
    TimelineAnalyzer,
)
from sentinel_api.ai.config import ModelConfig
from sentinel_api.ai.exceptions import AgentException
from sentinel_api.ai.runtime.agent import BaseAgent
from sentinel_api.ai.schemas.models import AgentRequest

logger = structlog.get_logger("sentinel_api.ai.agents.root_cause_agent.root_cause_agent")


class RootCauseAgent(BaseAgent):
    """Reasoning engine of Sentinel AI. Correlates sub-agent reports to find the root cause."""

    def __init__(self) -> None:
        super().__init__(name="Root Cause Agent")
        self.collector = EvidenceCollector()
        self.correlation_engine = CorrelationEngine()
        self.timeline_analyzer = TimelineAnalyzer()
        self.hypothesis_generator = HypothesisGenerator()
        self.conflict_resolver = ConflictResolver()
        self.ranker = HypothesisRanker()
        self.confidence_engine = ConfidenceEngine()
        self.explanation_generator = ExplanationGenerator()

    def validate(self, request: AgentRequest) -> None:
        """Validates that structured sub-agent results are present in signals/inputs."""
        super().validate(request)

        signals = request.incident_context.signals or {}
        inputs = request.inputs or {}

        has_sub_agent_output = any(
            k in signals or k in inputs
            for k in [
                "log_agent_output",
                "log_agent",
                "metrics_agent_output",
                "metrics_agent",
                "deployment_agent_output",
                "deployment_agent",
                "review_agent_output",
                "review_agent",
            ]
        )

        if not has_sub_agent_output:
            raise AgentException(
                "Root Cause Agent requires at least one upstream sub-agent"
                " diagnostic report."
            )

    async def _run(
        self, request: AgentRequest, config: ModelConfig
    ) -> Dict[str, Any]:
        """Orchestrates evidence collection, correlation, hypothesis ranking, and diagnosis generation."""
        start_time = time.perf_counter()

        signals = request.incident_context.signals or {}
        inputs = request.inputs or {}

        # 1. Collect & Normalize
        all_signals = {**signals, **inputs}
        normalized = self.collector.collect_and_normalize(all_signals)

        # 2. Timeline Analysis
        timeline = self.timeline_analyzer.build_cause_effect_timeline(
            normalized
        )

        # 3. Correlation Engine
        correlations = self.correlation_engine.find_correlations(normalized)

        # 4. Hypothesis Generation
        hypotheses = self.hypothesis_generator.generate_hypotheses(
            normalized, correlations
        )

        # 5. Conflict Resolution
        resolved = self.conflict_resolver.resolve_conflicts(
            hypotheses, normalized
        )

        # 6. Rank Hypotheses
        ranked = self.ranker.rank_hypotheses(resolved)

        # 7. Confidence score calculation
        conf_details = self.confidence_engine.calculate_confidence(
            ranked, normalized, all_signals
        )

        # 8. Explanation Generation
        summary = self.explanation_generator.generate_explanations(
            ranked, timeline
        )

        top_cause = ranked[0].title if ranked else "Unknown Infrastructure Issue"
        supporting_evidence = (
            ranked[0].supporting_evidence if ranked else ["No evidence matches"]
        )

        evidence_sources = list(set(ev["agent"] for ev in normalized))

        duration_ms = (time.perf_counter() - start_time) * 1000

        output = RootCauseAgentOutput(
            agent_name=self.name,
            execution_time_ms=duration_ms,
            status="SUCCESS" if ranked else "PARTIAL_SUCCESS",
            confidence=conf_details["overall_confidence"],
            root_cause=top_cause,
            supporting_evidence=supporting_evidence,
            alternative_hypotheses=ranked,
            reasoning=summary.executive_explanation,
            timeline_summary=timeline,
            evidence_sources=evidence_sources,
            metadata={
                "evidence_quality_score": conf_details[
                    "evidence_quality_score"
                ],
                "total_evidence_count": len(normalized),
                "hypotheses_count": len(ranked),
                "summary_narratives": summary.model_dump(),
            },
        )

        result_dict = output.model_dump()
        result_dict["reasoning_summary"] = summary.executive_explanation
        return result_dict
