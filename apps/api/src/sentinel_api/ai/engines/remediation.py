import structlog
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from sentinel_api.ai.config import ModelConfig
from sentinel_api.ai.registry.manager import ProviderManager

logger = structlog.get_logger("sentinel_api.ai.engines.remediation")


class CodePatchOutput(BaseModel):
    explanation: str = Field(description="Explanation of what the code patch fixes.")
    changed_files: List[str] = Field(description="List of files that will be modified.")
    diff: str = Field(description="The actual code diff in unified diff format.")
    risk_level: str = Field(description="Risk level of applying this patch (Low, Medium, High).")
    testing_notes: str = Field(description="Notes on how to test the patch.")


class PullRequestDraftOutput(BaseModel):
    branch_name: str = Field(description="Suggested git branch name.")
    commit_message: str = Field(description="Commit message.")
    title: str = Field(description="Pull request title.")
    description: str = Field(description="Pull request description body.")
    review_summary: str = Field(description="Summary for reviewers.")


class RollbackPlanOutput(BaseModel):
    commands: List[str] = Field(description="List of bash/infrastructure commands to rollback the change.")
    checklist: List[str] = Field(description="Checklist for verifying successful rollback.")
    estimated_downtime_minutes: int = Field(description="Estimated downtime in minutes.")
    recovery_time_objective_minutes: int = Field(description="RTO in minutes.")


class RiskAnalysisOutput(BaseModel):
    confidence_score: int = Field(description="Confidence score (0-100) of the fix.")
    risk_level: str = Field(description="Risk level (Low, Medium, High).")
    breaking_changes: bool = Field(description="Whether the fix contains breaking changes.")
    potential_side_effects: List[str] = Field(description="List of potential side effects.")
    verification_steps: List[str] = Field(description="Steps to verify the fix works safely in production.")


class RunbookOutput(BaseModel):
    executive_summary: str = Field(description="High-level summary of the incident and recovery.")
    technical_summary: str = Field(description="Technical summary of the incident and root cause.")
    recovery_steps: List[str] = Field(description="Step-by-step recovery plan.")
    manual_steps: List[str] = Field(description="Steps that must be performed manually.")
    automation_steps: List[str] = Field(description="Steps that can be automated.")
    lessons_learned: List[str] = Field(description="Lessons learned from this incident.")
    future_prevention: List[str] = Field(description="Steps to prevent future occurrences.")


class RemediationPlanOutput(BaseModel):
    fix_strategy: List[str] = Field(description="High-level implementation steps and strategy.")
    infrastructure_commands: List[str] = Field(description="Infrastructure, K8s, or Docker commands to apply.")
    code_patch: CodePatchOutput
    github_pr_draft: PullRequestDraftOutput
    rollback_plan: RollbackPlanOutput
    risk_analysis: RiskAnalysisOutput
    runbook: RunbookOutput


class AutonomousRemediationEngine:
    """Independent AI Engine to generate detailed remediation plans and PR drafts."""
    
    def __init__(self):
        self.provider = ProviderManager.get_provider("openai")
        self.config = ModelConfig(provider="openai", model_name="gpt-4o", max_tokens=4000)
        
    async def generate_plan(self, incident_summary: str, root_cause: Any, agent_outputs: Dict[str, Any]) -> RemediationPlanOutput:
        """Generates a complete remediation plan based on incident context."""
        
        prompt = f"""
You are a Principal AI Systems Architect and Site Reliability Engineer.
An incident has just been analyzed. You must generate a production-ready Autonomous Remediation Plan.

INCIDENT SUMMARY:
{incident_summary}

ROOT CAUSE ANALYSIS:
{root_cause}

TELEMETRY & LOGS:
{agent_outputs}

Generate a comprehensive, structured JSON response that includes:
- Fix Strategy and Infrastructure Commands
- A production-quality Code Patch (support Node, Python, Java, K8s YAML, etc)
- A GitHub Pull Request Draft
- A Rollback Plan
- Risk Analysis
- A complete Runbook for the incident
"""
        
        logger.info("Generating autonomous remediation plan...")
        
        # In a real environment, we'd pass `RemediationPlanOutput`.
        # We will use structured generation via the provider.
        parsed_output = await self.provider.generate_structured(
            prompt=prompt,
            response_model=RemediationPlanOutput,
            config=self.config
        )
        
        return parsed_output
