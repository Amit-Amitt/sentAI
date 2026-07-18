import uuid
from typing import Any, Dict, List, Optional
from datetime import datetime
from sqlalchemy import String, JSON, Float, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from sentinel_api.database.base import BaseModel


class RemediationPlan(BaseModel):
    """AI-generated remediation plans linked to an incident."""
    __tablename__ = "remediation_plans"

    incident_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("incidents.id", ondelete="CASCADE"), index=True, nullable=False)
    
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    
    # application_code, configuration, kubernetes_yaml, terraform, etc.
    remediation_type: Mapped[str] = mapped_column(String, index=True, nullable=False)
    
    # The actual patch/diff or script to run
    patch_content: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    files_changed: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)
    potential_risks: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    expected_impact: Mapped[str] = mapped_column(String, nullable=False)
    
    rollback_plan: Mapped[str] = mapped_column(String, nullable=False)
    
    # draft, pending_validation, pending_approval, approved, rejected, executed, failed
    status: Mapped[str] = mapped_column(String, default="draft", index=True, nullable=False)


class ValidationResult(BaseModel):
    """Results of Sandbox Validation (Linting, Tests, Build)."""
    __tablename__ = "validation_results"

    remediation_plan_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("remediation_plans.id", ondelete="CASCADE"), index=True, nullable=False)
    
    step_name: Mapped[str] = mapped_column(String, nullable=False) # e.g., 'npm test', 'flake8', 'terraform plan'
    status: Mapped[str] = mapped_column(String, nullable=False) # success, failed, error
    
    output_log: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    duration_ms: Mapped[int] = mapped_column(Float, default=0.0, nullable=False)


class DraftPullRequest(BaseModel):
    """GitHub Pull Request automation linkage."""
    __tablename__ = "draft_pull_requests"

    remediation_plan_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("remediation_plans.id", ondelete="CASCADE"), index=True, nullable=False)
    
    repository: Mapped[str] = mapped_column(String, nullable=False) # owner/repo
    pr_number: Mapped[int] = mapped_column(Integer, nullable=False)
    pr_url: Mapped[str] = mapped_column(String, nullable=False)
    
    branch_name: Mapped[str] = mapped_column(String, nullable=False)
    base_sha: Mapped[str] = mapped_column(String, nullable=False)
    
    status: Mapped[str] = mapped_column(String, nullable=False) # open, merged, closed


class ApprovalRequest(BaseModel):
    """Audit log for human approvals of remediations."""
    __tablename__ = "approval_requests"

    remediation_plan_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("remediation_plans.id", ondelete="CASCADE"), index=True, nullable=False)
    
    approver_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    decision: Mapped[str] = mapped_column(String, nullable=False) # approved, rejected
    reason: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    execution_mode: Mapped[str] = mapped_column(String, nullable=False) # draft_pr, direct_execution
    
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
