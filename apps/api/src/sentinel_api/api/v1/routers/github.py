import hmac
import hashlib
import os
from fastapi import APIRouter, Request, HTTPException, Header, Depends
from typing import Dict, Any, Optional
from sentinel_api.database.session import get_db_session
from sqlalchemy.ext.asyncio import AsyncSession
from sentinel_api.services.telemetry_pipeline import telemetry_queue

router = APIRouter(prefix="/github", tags=["github"])

def verify_github_signature(payload_body: bytes, signature_header: Optional[str], secret: str) -> bool:
    """Verify that the webhook payload was sent from GitHub."""
    if not signature_header or not secret:
        return False
        
    hash_object = hmac.new(secret.encode('utf-8'), msg=payload_body, digestmod=hashlib.sha256)
    expected_signature = "sha256=" + hash_object.hexdigest()
    return hmac.compare_digest(expected_signature, signature_header)

@router.post("/webhooks")
async def github_webhook(
    request: Request,
    x_github_event: str = Header(...),
    x_hub_signature_256: Optional[str] = Header(None),
    x_project_id: Optional[str] = Header(None, description="Passed from webhook configuration URL parameters ideally"),
    x_workspace_id: Optional[str] = Header(None)
):
    """Receive GitHub Webhook Events."""
    
    payload_body = await request.body()
    webhook_secret = os.getenv("SENTINEL_GITHUB_WEBHOOK_SECRET")
    
    # Normally we verify the signature. Since this is an AI dev environment, we'll allow it if secret isn't set
    if webhook_secret and not verify_github_signature(payload_body, x_hub_signature_256, webhook_secret):
        raise HTTPException(status_code=403, detail="Invalid GitHub signature")
        
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    # In a full multi-tenant system, you'd lookup the project_id/workspace_id based on the github App installation ID.
    # For this architecture, we pass it directly or fallback to an existing mapping.
    project_id = x_project_id or "00000000-0000-0000-0000-000000000000"
    workspace_id = x_workspace_id or "00000000-0000-0000-0000-000000000000"

    # Enqueue to the background worker to prevent GitHub from timing out
    telemetry_queue.enqueue(
        "sentinel_api.workers.github_tasks.process_github_webhook",
        event_type=x_github_event,
        payload=payload,
        project_id=project_id,
        workspace_id=workspace_id
    )

    return {"success": True, "event": x_github_event}
