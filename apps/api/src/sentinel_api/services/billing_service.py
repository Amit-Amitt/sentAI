import uuid
import datetime
import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from sentinel_api.database.session import AsyncSessionLocal
from sentinel_api.models.billing import BillingSubscription, BillingPlan, UsageRecord

logger = structlog.get_logger("sentinel_api.services.billing_service")

class FeatureGate:
    """Centralized authorization layer for checking if an Organization has access to premium features."""
    
    @staticmethod
    async def check(organization_id: str, feature_key: str, db: AsyncSession) -> bool:
        """
        Returns True if the organization's current plan allows access to the feature.
        Never directly queries Stripe; relies on the local synced BillingPlan.
        """
        stmt = select(BillingSubscription).where(
            BillingSubscription.customer_id.in_(
                select(BillingSubscription.customer_id).where(
                    # We would join on BillingCustomer to match org_id, but for brevity:
                    # let's assume we have a helper or relationship properly mapped.
                    pass
                )
            )
        )
        # Simplified query for brevity:
        # In a real app we'd join: BillingCustomer -> BillingSubscription -> BillingPlan
        from sentinel_api.models.billing import BillingCustomer
        stmt = (
            select(BillingPlan)
            .join(BillingSubscription, BillingSubscription.plan_id == BillingPlan.id)
            .join(BillingCustomer, BillingCustomer.id == BillingSubscription.customer_id)
            .where(BillingCustomer.organization_id == uuid.UUID(organization_id))
            .where(BillingSubscription.status == "active")
        )
        
        result = await db.execute(stmt)
        plan = result.scalar_one_or_none()
        
        if not plan:
            # Fallback to a default 'Free' plan if no active subscription is found
            stmt_free = select(BillingPlan).where(BillingPlan.name == "Free")
            res_free = await db.execute(stmt_free)
            plan = res_free.scalar_one_or_none()
            if not plan:
                return False
                
        return plan.features.get(feature_key, False)

class Meter:
    """Usage metering tracking."""
    
    @staticmethod
    async def record_usage(organization_id: str, metric_name: str, amount: int = 1):
        """
        Optimistically tracks usage. Usually called via a background task 
        to avoid slowing down the main request thread.
        """
        try:
            async with AsyncSessionLocal() as db:
                today = datetime.datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
                
                stmt = select(UsageRecord).where(
                    UsageRecord.organization_id == uuid.UUID(organization_id),
                    UsageRecord.metric_name == metric_name,
                    UsageRecord.date == today
                )
                res = await db.execute(stmt)
                record = res.scalar_one_or_none()
                
                if record:
                    record.quantity += amount
                else:
                    record = UsageRecord(
                        id=uuid.uuid4(),
                        organization_id=uuid.UUID(organization_id),
                        metric_name=metric_name,
                        date=today,
                        quantity=amount
                    )
                    db.add(record)
                    
                await db.commit()
        except Exception as e:
            logger.error("Failed to record usage", error=str(e), org_id=organization_id)
