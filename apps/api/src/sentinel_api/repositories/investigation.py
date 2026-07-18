import uuid
from typing import Any, Dict, List, Optional
from sqlalchemy import asc, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from sentinel_api.models.investigation import Investigation


class InvestigationRepository:
    """Repository logic handling database queries for Investigation entities."""

    async def create(
        self,
        db: AsyncSession,
        incident_id: str,
        severity: str,
        status: str,
        summary: str,
        agent_outputs: Dict[str, Any],
        incident_report: Dict[str, Any],
    ) -> Investigation:
        """Saves a new investigation run record into the database."""
        db_obj = Investigation(
            incident_id=incident_id,
            severity=severity,
            status=status,
            summary=summary,
            agent_outputs=agent_outputs,
            incident_report=incident_report,
        )
        db.add(db_obj)
        await db.flush()
        return db_obj

    async def get(self, db: AsyncSession, id: uuid.UUID) -> Optional[Investigation]:
        """Retrieves a single investigation run record by ID."""
        result = await db.execute(
            select(Investigation).where(Investigation.id == id)
        )
        return result.scalars().first()

    async def delete(self, db: AsyncSession, id: uuid.UUID) -> bool:
        """Deletes an investigation run record by ID."""
        db_obj = await self.get(db, id)
        if not db_obj:
            return False
        await db.delete(db_obj)
        return True

    async def list(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> List[Investigation]:
        """Lists, paginates, filters, and sorts historical investigation records."""
        stmt = select(Investigation)
        if status:
            stmt = stmt.where(Investigation.status == status)

        order_col = getattr(Investigation, sort_by, Investigation.created_at)
        if sort_order.lower() == "desc":
            stmt = stmt.order_by(desc(order_col))
        else:
            stmt = stmt.order_by(asc(order_col))

        stmt = stmt.offset(skip).limit(limit)
        result = await db.execute(stmt)
        return list(result.scalars().all())
