import uuid
from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from sentinel_api.database.session import get_db_session
from sentinel_api.api.v1.controllers.memory import MemoryController, MemoryResponse

router = APIRouter(prefix="/memory", tags=["memory"])


def get_controller(session: AsyncSession = Depends(get_db_session)) -> MemoryController:
    """Dependency helper instantiating MemoryController."""
    return MemoryController(session)


@router.get("", response_model=List[MemoryResponse])
async def list_memories(
    workspace_id: uuid.UUID = Query(..., description="The ID of the active workspace"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    controller: MemoryController = Depends(get_controller),
):
    """Retrieves all past incident memories for a given workspace."""
    return await controller.list_memories(
        workspace_id=workspace_id, limit=limit, offset=offset
    )


@router.get("/search", response_model=List[MemoryResponse])
async def search_memories(
    workspace_id: uuid.UUID = Query(..., description="The ID of the active workspace"),
    q: str = Query(..., description="Search query or incident traits"),
    limit: int = Query(5, ge=1, le=20),
    controller: MemoryController = Depends(get_controller),
):
    """Searches past incidents based on textual summary matching."""
    return await controller.search_similar(
        workspace_id=workspace_id, query=q, limit=limit
    )


@router.get("/{memory_id}", response_model=MemoryResponse)
async def get_memory(
    memory_id: uuid.UUID,
    workspace_id: uuid.UUID = Query(..., description="The ID of the active workspace"),
    controller: MemoryController = Depends(get_controller),
):
    """Retrieves a specific incident memory by ID."""
    return await controller.get_memory(workspace_id=workspace_id, memory_id=memory_id)
