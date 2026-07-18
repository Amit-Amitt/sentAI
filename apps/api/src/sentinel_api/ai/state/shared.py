from typing import Any

from pydantic import BaseModel, Field


class SharedAgentState(BaseModel):
    """Encapsulates the global state shared across multiple collaborating agents."""

    conversation_history: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Chronological list of agent messages, tool returns, and user signals.",
    )
    execution_state: dict[str, Any] = Field(
        default_factory=dict,
        description="Active state variables, loop counts, execution logs, and routing metrics.",
    )
    incident_state: dict[str, Any] = Field(
        default_factory=dict,
        description="Current diagnostic facts, hypotheses, and investigations regarding the incident.",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Telemetric tracking details, engine labels, and environmental metadata.",
    )
    context: dict[str, Any] = Field(
        default_factory=dict,
        description="Dynamic runtime context variables and local parameter overrides.",
    )
