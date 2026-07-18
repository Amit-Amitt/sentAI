import uuid
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sentinel_api.database.session import get_db_session
from sentinel_api.models.incident import Incident
from sentinel_api.models.notifications import IncidentComment, IncidentAcknowledgement

router = APIRouter(prefix="/incidents/{incident_id}", tags=["collaboration"])

class CommentPayload(BaseModel):
    user_id: str
    content: str
    attachments: Optional[List[dict]] = []

class AckPayload(BaseModel):
    user_id: str
    action: str # "acknowledged", "resolved", "snoozed"

@router.post("/comments")
async def add_incident_comment(
    incident_id: str,
    payload: CommentPayload,
    db: AsyncSession = Depends(get_db_session)
):
    """Add a comment to an incident for collaboration."""
    incident = await db.get(Incident, uuid.UUID(incident_id))
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
        
    comment = IncidentComment(
        id=uuid.uuid4(),
        incident_id=incident.id,
        user_id=uuid.UUID(payload.user_id) if payload.user_id else None,
        content=payload.content,
        attachments=payload.attachments or []
    )
    db.add(comment)
    await db.commit()
    return {"success": True, "comment_id": comment.id}

@router.post("/acknowledge")
async def acknowledge_incident(
    incident_id: str,
    payload: AckPayload,
    db: AsyncSession = Depends(get_db_session)
):
    """Acknowledge or Resolve an incident."""
    incident = await db.get(Incident, uuid.UUID(incident_id))
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
        
    ack = IncidentAcknowledgement(
        id=uuid.uuid4(),
        incident_id=incident.id,
        user_id=uuid.UUID(payload.user_id) if payload.user_id else None,
        action=payload.action
    )
    db.add(ack)
    
    if payload.action == "resolved":
        incident.status = "Resolved"
    elif incident.status == "Open":
        incident.status = "Investigating"
        
    await db.commit()
    return {"success": True, "status": incident.status}

@router.get("/timeline")
async def get_incident_timeline(
    incident_id: str,
    db: AsyncSession = Depends(get_db_session)
):
    """Fetch all comments and acknowledgements for the incident."""
    comments_stmt = select(IncidentComment).where(IncidentComment.incident_id == uuid.UUID(incident_id))
    acks_stmt = select(IncidentAcknowledgement).where(IncidentAcknowledgement.incident_id == uuid.UUID(incident_id))
    
    comments_res = await db.execute(comments_stmt)
    acks_res = await db.execute(acks_stmt)
    
    comments = comments_res.scalars().all()
    acks = acks_res.scalars().all()
    
    return {
        "comments": comments,
        "acknowledgements": acks
    }
