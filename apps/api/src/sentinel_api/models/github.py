import uuid
from typing import Any, Dict, List, Optional
from datetime import datetime
from sqlalchemy import String, JSON, Integer, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sentinel_api.database.base import BaseModel


class GithubRepository(BaseModel):
    """Connected GitHub Repositories for deployment intelligence."""
    __tablename__ = "github_repositories"

    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True, nullable=False)
    workspace_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"), index=True, nullable=False)
    
    github_repo_id: Mapped[str] = mapped_column(String, index=True, unique=True, nullable=False)
    owner: Mapped[str] = mapped_column(String, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String, index=True, nullable=False)
    
    default_branch: Mapped[str] = mapped_column(String, default="main", nullable=False)
    is_private: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    language: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    framework: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    last_synced_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


class GithubCommit(BaseModel):
    """Synchronized Git Commits."""
    __tablename__ = "github_commits"

    repository_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("github_repositories.id", ondelete="CASCADE"), index=True, nullable=False)
    
    sha: Mapped[str] = mapped_column(String, index=True, unique=True, nullable=False)
    message: Mapped[str] = mapped_column(String, nullable=False)
    author_name: Mapped[str] = mapped_column(String, nullable=False)
    author_email: Mapped[str] = mapped_column(String, nullable=False)
    author_login: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    
    lines_added: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    lines_deleted: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    files_changed: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    
    parents: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)


class GithubPullRequest(BaseModel):
    """Synchronized Pull Requests."""
    __tablename__ = "github_pull_requests"

    repository_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("github_repositories.id", ondelete="CASCADE"), index=True, nullable=False)
    
    pr_number: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    state: Mapped[str] = mapped_column(String, nullable=False) # open, closed
    is_merged: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    author_login: Mapped[str] = mapped_column(String, nullable=False)
    merge_commit_sha: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    merged_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


class GithubDeployment(BaseModel):
    """GitHub Deployments tracking (both native deployments and releases/tags)."""
    __tablename__ = "github_deployments"

    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True, nullable=False)
    repository_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("github_repositories.id", ondelete="CASCADE"), index=True, nullable=False)
    
    deployment_id: Mapped[str] = mapped_column(String, index=True, unique=True, nullable=False) # ID from GH Deployments API or release tag name
    environment: Mapped[str] = mapped_column(String, index=True, nullable=False) # production, staging, preview
    
    status: Mapped[str] = mapped_column(String, nullable=False) # pending, success, failed, error
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    commit_sha: Mapped[str] = mapped_column(String, index=True, nullable=False)
    author_login: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    risk_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    risk_factors: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    
    deployed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
