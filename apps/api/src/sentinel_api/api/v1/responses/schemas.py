from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Standardized error details returned on 4xx/5xx responses."""

    success: bool = Field(False, description="Always False for error results")
    error: str = Field(..., description="High-level error narrative")
    code: str = Field(..., description="Standardized error category string")
    details: Optional[Any] = Field(None, description="Optional extra debug metadata")


class AnalysisSubmitResponse(BaseModel):
    """Response payload when starting a new incident analysis."""

    investigation_id: str = Field(..., description="UUID of the investigation record")
    status: str = Field(..., description="Incident status")
    incident_id: str = Field(..., description="Unique incident identifier")


class InvestigationListResponse(BaseModel):
    """Paginated collection of historical investigations."""

    results: List[Dict[str, Any]] = Field(..., description="List of investigation records")
    total: int = Field(..., description="Total matching items in DB")
    skip: int = Field(..., description="Offset pagination skip value")
    limit: int = Field(..., description="Offset pagination limit value")


class DeleteResponse(BaseModel):
    """Standardized delete confirmation reply."""

    success: bool = Field(True, description="Deletion success indicator")
    message: str = Field(..., description="Confirmation detail narrative")
