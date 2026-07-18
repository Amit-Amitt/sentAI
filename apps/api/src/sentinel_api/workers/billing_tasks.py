import datetime
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, func

from sentinel_api.database.session import engine
from sentinel_api.models.billing import UsageRecord, BillingSubscription, BillingCustomer

logger = structlog.get_logger("sentinel_api.workers.billing_tasks")

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def _aggregate_usage_async():
    """Daily cron job to aggregate usage and check quotas."""
    async with AsyncSessionLocal() as db:
        # Example: check telemetry limits
        today = datetime.datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        start_of_month = today.replace(day=1)
        
        stmt = (
            select(
                UsageRecord.organization_id,
                func.sum(UsageRecord.quantity).label("total")
            )
            .where(
                UsageRecord.metric_name == "telemetry_events",
                UsageRecord.date >= start_of_month
            )
            .group_by(UsageRecord.organization_id)
        )
        
        res = await db.execute(stmt)
        usage_data = res.all()
        
        for org_id, total in usage_data:
            # Here we would fetch the Organization's current plan and verify the quota
            # If `total` > `plan.quotas['telemetry_events_per_month']`, we trigger an alert
            # or send a warning email.
            pass
            
        logger.info("Usage aggregation and quota check complete", processed_orgs=len(usage_data))

def aggregate_usage():
    import asyncio
    asyncio.run(_aggregate_usage_async())
