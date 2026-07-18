import uuid
import datetime
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sentinel_api.database.session import get_db_session
from sentinel_api.models.remediation import RemediationPlan, ApprovalRequest

router = APIRouter(prefix="/remediations", tags=["remediation"])

class ApprovalPayload(BaseModel):
    user_id: str
    decision: str # "approved", "rejected"
    reason: str = ""
    execution_mode: str = "draft_pr"

@router.get("/pending")
async def get_pending_remediations(db: AsyncSession = Depends(get_db_session)):
    """Fetch all remediations waiting for human approval."""
    stmt = select(RemediationPlan).where(RemediationPlan.status == "pending_approval")
    result = await db.execute(stmt)
    plans = result.scalars().all()
    return {"pending_remediations": plans}

@router.post("/{plan_id}/approve")
async def approve_remediation(
    plan_id: str,
    payload: ApprovalPayload,
    db: AsyncSession = Depends(get_db_session)
):
    """Approve or reject an AI-generated remediation."""
    plan = await db.get(RemediationPlan, uuid.UUID(plan_id))
    if not plan:
        raise HTTPException(status_code=404, detail="Remediation Plan not found")
        
    if plan.status != "pending_approval":
        raise HTTPException(status_code=400, detail=f"Plan is currently {plan.status}")
        
    # Audit log
    approval = ApprovalRequest(
        id=uuid.uuid4(),
        remediation_plan_id=plan.id,
        approver_id=uuid.UUID(payload.user_id) if payload.user_id else None,
        decision=payload.decision,
        reason=payload.reason,
        execution_mode=payload.execution_mode
    )
    db.add(approval)
    
    if payload.decision == "approved":
        plan.status = "approved"
        # In a real system, we might enqueue a background task to actually trigger the execution
        # (e.g. merging the PR or pushing infrastructure updates to Kubernetes)
    else:
        plan.status = "rejected"
        
    await db.commit()
    
    return {"success": True, "status": plan.status}
