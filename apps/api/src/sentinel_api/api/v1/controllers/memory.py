import uuid
from typing import List, Dict, Any
from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from sentinel_api.services.memory import MemoryService
from sentinel_api.models.memory import IncidentMemory


class MemoryResponse(BaseModel):
    id: uuid.UUID
    incident_id: str
    summary: str
    severity: str
    status: str
    confidence: float
    time_taken_ms: int
    root_cause: dict
    recommended_fix: dict
    generated_report: dict
    timeline: list
    tags: List[Dict[str, Any]]
    
    class Config:
        from_attributes = True


class MemoryController:
    """Controller handling AI Memory REST endpoints."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.memory_service = MemoryService(session)

    async def list_memories(
        self,
        workspace_id: uuid.UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> List[MemoryResponse]:
        """Fetch historical incidents for the workspace."""
        try:
            memories = await self.memory_service.get_memories(
                workspace_id=workspace_id,
                limit=limit,
                offset=offset
            )
            
            # Format tags for response
            response = []
            for memory in memories:
                mem_dict = {
                    "id": memory.id,
                    "incident_id": memory.incident_id,
                    "summary": memory.summary,
                    "severity": memory.severity,
                    "status": memory.status,
                    "confidence": memory.confidence,
                    "time_taken_ms": memory.time_taken_ms,
                    "root_cause": memory.root_cause,
                    "recommended_fix": memory.recommended_fix,
                    "generated_report": memory.generated_report,
                    "timeline": memory.timeline,
                    "tags": [{"name": t.name, "value": t.value} for t in memory.tags]
                }
                response.append(MemoryResponse(**mem_dict))
                
            return response
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def get_memory(
        self,
        workspace_id: uuid.UUID,
        memory_id: uuid.UUID,
    ) -> MemoryResponse:
        """Fetch a specific historical incident."""
        try:
            memory = await self.memory_service.get_memory(workspace_id, memory_id)
            if not memory:
                raise HTTPException(status_code=404, detail="Memory not found.")
                
            mem_dict = {
                "id": memory.id,
                "incident_id": memory.incident_id,
                "summary": memory.summary,
                "severity": memory.severity,
                "status": memory.status,
                "confidence": memory.confidence,
                "time_taken_ms": memory.time_taken_ms,
                "root_cause": memory.root_cause,
                "recommended_fix": memory.recommended_fix,
                "generated_report": memory.generated_report,
                "timeline": memory.timeline,
                "tags": [{"name": t.name, "value": t.value} for t in memory.tags]
            }
            return MemoryResponse(**mem_dict)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def search_similar(
        self,
        workspace_id: uuid.UUID,
        query: str,
        limit: int = 5,
    ) -> List[MemoryResponse]:
        """Retrieves similar past incidents based on query text."""
        try:
            memories = await self.memory_service.find_similar(
                workspace_id=workspace_id,
                query_text=query,
                limit=limit
            )
            
            response = []
            for memory in memories:
                mem_dict = {
                    "id": memory.id,
                    "incident_id": memory.incident_id,
                    "summary": memory.summary,
                    "severity": memory.severity,
                    "status": memory.status,
                    "confidence": memory.confidence,
                    "time_taken_ms": memory.time_taken_ms,
                    "root_cause": memory.root_cause,
                    "recommended_fix": memory.recommended_fix,
                    "generated_report": memory.generated_report,
                    "timeline": memory.timeline,
                    "tags": [{"name": t.name, "value": t.value} for t in memory.tags]
                }
                response.append(MemoryResponse(**mem_dict))
            return response
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
