import uuid
from typing import Any, List, Dict
import structlog
from sqlalchemy import select, or_, desc, String
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from sentinel_api.models.memory import IncidentMemory, IncidentTag
from sentinel_api.ai.workflows.state import WorkflowState
from sentinel_api.ai.schemas.models import IncidentContext

logger = structlog.get_logger("sentinel_api.services.memory")


class MemoryService:
    """Service for persisting and retrieving AI Incident Memories.
    Currently utilizes PostgreSQL for metadata and keyword matching,
    but is architected to seamlessly transition to Qdrant for semantic search.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save_memory(
        self,
        incident: IncidentContext,
        state: WorkflowState,
        workspace_id: uuid.UUID,
        organization_id: uuid.UUID,
    ) -> IncidentMemory:
        """Saves the completed incident workflow state into long-term memory."""
        
        # Calculate time taken from execution_timeline
        timeline = state.get("execution_timeline", [])
        time_taken_ms = 0
        if timeline:
            time_taken_ms = sum(event.get("duration_ms", 0) for event in timeline)

        memory = IncidentMemory(
            incident_id=incident.incident_id,
            workspace_id=workspace_id,
            organization_id=organization_id,
            summary=incident.summary,
            severity=incident.severity,
            status="RESOLVED",
            confidence=state.get("confidence_score", 0.0),
            time_taken_ms=int(time_taken_ms),
            root_cause=state.get("root_cause", {}),
            recommended_fix={"actions": state.get("recommended_actions", [])},
            generated_report=state.get("generated_report", {}),
            timeline=state.get("incident_timeline", []),
            logs_summary=state.get("log_analysis", {}),
            metrics_summary=state.get("metrics_analysis", {}),
            deployment_summary=state.get("deployment_analysis", {}),
        )

        self.session.add(memory)
        await self.session.flush()

        # Generate tags for filtering
        tags = []
        for service in incident.signals.get("affected_services", []):
            tags.append(IncidentTag(memory_id=memory.id, name="service", value=service))
            
        tags.append(IncidentTag(memory_id=memory.id, name="environment", value=incident.signals.get("environment", "prod")))
        
        if tags:
            self.session.add_all(tags)
            
        await self.session.commit()
        await self.session.refresh(memory)
        
        logger.info("Saved incident memory", memory_id=str(memory.id), incident_id=incident.incident_id)
        return memory

    async def find_similar(
        self,
        workspace_id: uuid.UUID,
        query_text: str,
        tags: List[Dict[str, str]] = None,
        limit: int = 5,
    ) -> List[IncidentMemory]:
        """Retrieves similar past incidents based on workspace, text matching, and tags.
        Ready to be swapped with Qdrant vector retrieval.
        """
        
        # Base query restricted by workspace for security isolation
        stmt = select(IncidentMemory).where(IncidentMemory.workspace_id == workspace_id)

        # Basic keyword matching (placeholder for semantic search)
        if query_text:
            search_term = f"%{query_text}%"
            stmt = stmt.where(
                or_(
                    IncidentMemory.summary.ilike(search_term),
                    # We can cast JSON to text to search inside root cause
                    IncidentMemory.root_cause.cast(String).ilike(search_term),
                )
            )

        # Optional tag filtering
        if tags:
            # For exact matches if they exist
            # Note: A real implementation might do complex joins or intersect
            pass

        stmt = stmt.order_by(desc(IncidentMemory.created_at)).limit(limit)
        stmt = stmt.options(selectinload(IncidentMemory.tags))
        
        result = await self.session.execute(stmt)
        memories = result.scalars().all()
        
        logger.info("Retrieved similar incidents", count=len(memories), workspace_id=str(workspace_id))
        return list(memories)

    async def get_memories(
        self,
        workspace_id: uuid.UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> List[IncidentMemory]:
        """Retrieves a paginated list of all past incident memories for the dashboard."""
        stmt = (
            select(IncidentMemory)
            .where(IncidentMemory.workspace_id == workspace_id)
            .order_by(desc(IncidentMemory.created_at))
            .offset(offset)
            .limit(limit)
            .options(selectinload(IncidentMemory.tags))
        )
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_memory(
        self,
        workspace_id: uuid.UUID,
        memory_id: uuid.UUID,
    ) -> IncidentMemory | None:
        """Retrieves a specific memory."""
        stmt = (
            select(IncidentMemory)
            .where(
                IncidentMemory.workspace_id == workspace_id,
                IncidentMemory.id == memory_id
            )
            .options(selectinload(IncidentMemory.tags))
        )
        
        result = await self.session.execute(stmt)
        return result.scalars().first()
