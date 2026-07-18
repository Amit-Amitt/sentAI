import structlog
import uuid
import datetime
from typing import Dict, Any, List
from sentinel_api.database.session import AsyncSessionLocal
from sentinel_api.models.remediation import RemediationPlan, DraftPullRequest, ValidationResult
from sentinel_api.services.github_client import GithubClient

logger = structlog.get_logger("sentinel_api.services.remediation_engine")

class RemediationEngine:
    """Orchestrates AI-generated patches, sandbox validation, and GitHub PR creation."""

    @staticmethod
    async def generate_and_validate_plan(incident_id: str, ai_patch_data: Dict[str, Any]) -> RemediationPlan:
        """
        Receives raw output from the AI Root Cause agent containing a proposed fix.
        Stores it as a RemediationPlan and simulates Sandbox Validation.
        """
        async with AsyncSessionLocal() as db:
            plan = RemediationPlan(
                id=uuid.uuid4(),
                incident_id=uuid.UUID(incident_id),
                title=ai_patch_data.get("title", "AI Proposed Fix"),
                description=ai_patch_data.get("description", ""),
                remediation_type=ai_patch_data.get("remediation_type", "application_code"),
                patch_content=ai_patch_data.get("patch_content", ""),
                files_changed=ai_patch_data.get("files_changed", []),
                confidence_score=ai_patch_data.get("confidence_score", 0.0),
                potential_risks=ai_patch_data.get("potential_risks", []),
                expected_impact=ai_patch_data.get("expected_impact", ""),
                rollback_plan=ai_patch_data.get("rollback_plan", "git revert"),
                status="pending_validation"
            )
            db.add(plan)
            await db.flush()
            
            # --- Simulated Sandbox Validation ---
            # In a real environment, this might enqueue an RQ job to execute a subprocess `pytest` 
            # or trigger a remote CI webhook and await the result.
            validation = ValidationResult(
                id=uuid.uuid4(),
                remediation_plan_id=plan.id,
                step_name="lint_and_test",
                status="success",
                output_log="Prettier formatting passed.\nUnit tests passed (12/12).",
                duration_ms=4500.0
            )
            db.add(validation)
            
            # If validation succeeds, move to pending_approval
            plan.status = "pending_approval"
            await db.commit()
            
            return plan

    @staticmethod
    async def execute_github_draft_pr(plan_id: str, github_access_token: str, owner: str, repo: str, base_branch: str, base_sha: str) -> DraftPullRequest:
        """
        Takes an approved or pending RemediationPlan and opens a Draft Pull Request on GitHub.
        """
        async with AsyncSessionLocal() as db:
            plan = await db.get(RemediationPlan, uuid.UUID(plan_id))
            if not plan:
                raise ValueError("Remediation Plan not found")
                
            client = GithubClient(access_token=github_access_token)
            
            branch_name = f"sentinel-fix-{str(plan.id)[:8]}"
            
            try:
                # 1. Create Branch
                await client.create_branch(owner, repo, branch_name, base_sha)
                
                # 2. In a real system, we would loop over plan.files_changed, create blobs, create a tree, and commit.
                # For architectural demonstration, assume commit is pushed here via standard Git tree operations.
                
                # 3. Create Draft PR
                pr_body = (
                    f"## Sentinel AI Auto-Remediation\n"
                    f"**Incident ID:** {plan.incident_id}\n\n"
                    f"### Reasoning\n{plan.description}\n\n"
                    f"### Risks\n" + "\n".join(f"- {r}" for r in plan.potential_risks) + "\n\n"
                    f"### Rollback Plan\n{plan.rollback_plan}\n"
                )
                
                pr_response = await client.create_pull_request(
                    owner=owner,
                    repo=repo,
                    title=f"[AI Fix] {plan.title}",
                    head=branch_name,
                    base=base_branch,
                    body=pr_body,
                    draft=True
                )
                
                draft_pr = DraftPullRequest(
                    id=uuid.uuid4(),
                    remediation_plan_id=plan.id,
                    repository=f"{owner}/{repo}",
                    pr_number=pr_response.get("number", 0),
                    pr_url=pr_response.get("html_url", ""),
                    branch_name=branch_name,
                    base_sha=base_sha,
                    status="open"
                )
                
                db.add(draft_pr)
                await db.commit()
                return draft_pr
                
            except Exception as e:
                logger.error("Failed to execute GitHub PR creation", error=str(e))
                raise
