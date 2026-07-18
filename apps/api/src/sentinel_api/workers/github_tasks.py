import uuid
import datetime
import structlog
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from sentinel_api.database.session import engine
from sentinel_api.models.github import GithubRepository, GithubCommit, GithubPullRequest, GithubDeployment
from sentinel_api.services.github_risk_analyzer import GithubRiskAnalyzer

logger = structlog.get_logger("sentinel_api.workers.github_tasks")

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def _process_github_webhook_async(event_type: str, payload: Dict[str, Any], project_id: str, workspace_id: str):
    """Processes incoming GitHub webhooks (Push, PR, Deployment)."""
    
    # In a full implementation, you would look up the GithubRepository by payload["repository"]["id"]
    # Here we mock the repository ID extraction for the sake of the architecture.
    repo_data = payload.get("repository", {})
    gh_repo_id = str(repo_data.get("id", ""))
    
    async with AsyncSessionLocal() as db:
        # 1. Ensure Repository exists
        stmt = select(GithubRepository).where(GithubRepository.github_repo_id == gh_repo_id)
        result = await db.execute(stmt)
        repo = result.scalar_one_or_none()
        
        if not repo and gh_repo_id:
            # Create it
            repo = GithubRepository(
                id=uuid.uuid4(),
                project_id=uuid.UUID(project_id),
                workspace_id=uuid.UUID(workspace_id),
                github_repo_id=gh_repo_id,
                owner=repo_data.get("owner", {}).get("login", ""),
                name=repo_data.get("name", ""),
                full_name=repo_data.get("full_name", ""),
                default_branch=repo_data.get("default_branch", "main"),
                is_private=repo_data.get("private", False),
                language=repo_data.get("language")
            )
            db.add(repo)
            await db.flush()

        if not repo:
            logger.error("Could not find or create repository for webhook", gh_repo_id=gh_repo_id)
            return

        # 2. Process based on event_type
        if event_type == "push":
            commits_data = payload.get("commits", [])
            for commit_data in commits_data:
                # Calculate risk
                files_added = commit_data.get("added", [])
                files_modified = commit_data.get("modified", [])
                files_removed = commit_data.get("removed", [])
                all_files = files_added + files_modified + files_removed
                
                commit = GithubCommit(
                    id=uuid.uuid4(),
                    repository_id=repo.id,
                    sha=commit_data.get("id", ""),
                    message=commit_data.get("message", ""),
                    author_name=commit_data.get("author", {}).get("name", ""),
                    author_email=commit_data.get("author", {}).get("email", ""),
                    author_login=commit_data.get("author", {}).get("username", ""),
                    timestamp=datetime.datetime.fromisoformat(commit_data.get("timestamp", datetime.datetime.utcnow().isoformat()).replace("Z", "+00:00")),
                    files_changed=all_files
                )
                db.add(commit)

        elif event_type == "pull_request":
            pr_data = payload.get("pull_request", {})
            pr_number = pr_data.get("number")
            
            stmt = select(GithubPullRequest).where(
                GithubPullRequest.repository_id == repo.id,
                GithubPullRequest.pr_number == pr_number
            )
            result = await db.execute(stmt)
            existing_pr = result.scalar_one_or_none()
            
            created_at_str = pr_data.get("created_at")
            merged_at_str = pr_data.get("merged_at")
            closed_at_str = pr_data.get("closed_at")
            
            if existing_pr:
                existing_pr.state = pr_data.get("state", "open")
                existing_pr.is_merged = pr_data.get("merged", False)
                existing_pr.merge_commit_sha = pr_data.get("merge_commit_sha")
                existing_pr.merged_at = datetime.datetime.fromisoformat(merged_at_str.replace("Z", "+00:00")) if merged_at_str else None
                existing_pr.closed_at = datetime.datetime.fromisoformat(closed_at_str.replace("Z", "+00:00")) if closed_at_str else None
            else:
                new_pr = GithubPullRequest(
                    id=uuid.uuid4(),
                    repository_id=repo.id,
                    pr_number=pr_number,
                    title=pr_data.get("title", ""),
                    state=pr_data.get("state", "open"),
                    is_merged=pr_data.get("merged", False),
                    author_login=pr_data.get("user", {}).get("login", ""),
                    merge_commit_sha=pr_data.get("merge_commit_sha"),
                    created_at=datetime.datetime.fromisoformat(created_at_str.replace("Z", "+00:00")) if created_at_str else datetime.datetime.utcnow(),
                    merged_at=datetime.datetime.fromisoformat(merged_at_str.replace("Z", "+00:00")) if merged_at_str else None,
                    closed_at=datetime.datetime.fromisoformat(closed_at_str.replace("Z", "+00:00")) if closed_at_str else None
                )
                db.add(new_pr)

        elif event_type == "deployment_status":
            dep_data = payload.get("deployment", {})
            status_data = payload.get("deployment_status", {})
            dep_id = str(dep_data.get("id"))
            
            stmt = select(GithubDeployment).where(
                GithubDeployment.repository_id == repo.id,
                GithubDeployment.deployment_id == dep_id
            )
            result = await db.execute(stmt)
            existing_dep = result.scalar_one_or_none()
            
            state = status_data.get("state", "pending")
            
            if existing_dep:
                existing_dep.status = state
            else:
                # We need to compute risk score
                # Usually we'd fetch the commit from DB to see files_changed
                # Mock files changed for architecture flow
                files_changed = [] 
                
                risk_score, risk_factors = GithubRiskAnalyzer.analyze_risk(files_changed)
                
                created_at_str = status_data.get("created_at")
                new_dep = GithubDeployment(
                    id=uuid.uuid4(),
                    project_id=uuid.UUID(project_id),
                    repository_id=repo.id,
                    deployment_id=dep_id,
                    environment=dep_data.get("environment", "production"),
                    status=state,
                    description=status_data.get("description"),
                    commit_sha=dep_data.get("sha", ""),
                    author_login=dep_data.get("creator", {}).get("login", ""),
                    risk_score=risk_score,
                    risk_factors=risk_factors,
                    deployed_at=datetime.datetime.fromisoformat(created_at_str.replace("Z", "+00:00")) if created_at_str else datetime.datetime.utcnow()
                )
                db.add(new_dep)
                
        await db.commit()


def process_github_webhook(event_type: str, payload: Dict[str, Any], project_id: str, workspace_id: str):
    """Entry point for RQ worker"""
    import asyncio
    asyncio.run(_process_github_webhook_async(event_type, payload, project_id, workspace_id))
