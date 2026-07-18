import uuid
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sentinel_api.database.session import get_db_session
from sentinel_api.api.v1.dependencies.security import get_current_user_jwt
from sentinel_api.services.stripe_client import StripeClient
from sentinel_api.models.billing import BillingPlan, BillingCustomer, WebhookEvent

router = APIRouter(prefix="/billing", tags=["billing"])

class CheckoutRequest(BaseModel):
    organization_id: str
    price_id: str
    success_url: str
    cancel_url: str

class PortalRequest(BaseModel):
    organization_id: str
    return_url: str

@router.get("/plans")
async def get_plans(db: AsyncSession = Depends(get_db_session)):
    """Fetch all active billing plans and their features/quotas."""
    stmt = select(BillingPlan).where(BillingPlan.is_active == True)
    res = await db.execute(stmt)
    return {"plans": res.scalars().all()}

@router.post("/checkout")
async def create_checkout(
    payload: CheckoutRequest,
    current_user: dict = Depends(get_current_user_jwt),
    db: AsyncSession = Depends(get_db_session)
):
    """Generate a Stripe Checkout URL for a plan upgrade."""
    # RBAC check omitted for brevity (ensure current_user is Org Admin)
    
    stmt = select(BillingCustomer).where(BillingCustomer.organization_id == uuid.UUID(payload.organization_id))
    res = await db.execute(stmt)
    customer = res.scalar_one_or_none()
    
    if not customer:
        raise HTTPException(status_code=404, detail="Billing Customer not found for this organization")
        
    url = StripeClient.create_checkout_session(
        customer_id=customer.stripe_customer_id,
        price_id=payload.price_id,
        success_url=payload.success_url,
        cancel_url=payload.cancel_url,
        client_reference_id=payload.organization_id
    )
    return {"url": url}

@router.post("/portal")
async def create_portal(
    payload: PortalRequest,
    current_user: dict = Depends(get_current_user_jwt),
    db: AsyncSession = Depends(get_db_session)
):
    """Generate a Stripe Customer Portal URL."""
    stmt = select(BillingCustomer).where(BillingCustomer.organization_id == uuid.UUID(payload.organization_id))
    res = await db.execute(stmt)
    customer = res.scalar_one_or_none()
    
    if not customer:
        raise HTTPException(status_code=404, detail="Billing Customer not found")
        
    url = StripeClient.create_portal_session(
        customer_id=customer.stripe_customer_id,
        return_url=payload.return_url
    )
    return {"url": url}

@router.post("/webhook")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db_session)):
    """Secure endpoint for Stripe Webhooks."""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    if not sig_header:
        raise HTTPException(status_code=400, detail="Missing signature")
        
    try:
        event = StripeClient.construct_webhook_event(payload, sig_header)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    # Idempotency check
    stmt = select(WebhookEvent).where(WebhookEvent.stripe_event_id == event.id)
    res = await db.execute(stmt)
    if res.scalar_one_or_none():
        return {"status": "already processed"}
        
    # Record webhook receipt for async processing
    wh_event = WebhookEvent(
        id=uuid.uuid4(),
        stripe_event_id=event.id,
        event_type=event.type,
        status="pending"
    )
    db.add(wh_event)
    await db.commit()
    
    # In a real system, we'd trigger a background task here:
    # telemetry_queue.enqueue("sentinel_api.workers.billing_tasks.process_webhook", event_id=str(wh_event.id))
    
    return {"status": "success"}
