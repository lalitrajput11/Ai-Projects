"""Pydantic models for request/response validation and state management."""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class WebhookTrigger(BaseModel):
    """Model for n8n webhook trigger payload."""
    trigger_id: str = Field(..., description="Unique identifier for this trigger")
    action: str = Field(..., description="Action to perform")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Action parameters")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional context")


class AgentResponse(BaseModel):
    """Model for agent execution response."""
    trigger_id: str
    status: str  # "success", "error", "pending"
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time: float
    timestamp: datetime = Field(default_factory=datetime.now)


class AgentState(BaseModel):
    """Model for LangGraph agent state."""
    messages: List[Dict[str, str]] = Field(default_factory=list)
    current_task: Optional[str] = None
    plan: List[str] = Field(default_factory=list)
    tool_results: List[Dict[str, Any]] = Field(default_factory=list)
    memory_context: Dict[str, Any] = Field(default_factory=dict)
    iteration: int = 0
    max_iterations: int = 10
    finished: bool = False


class ToolCall(BaseModel):
    """Model for tool invocation."""
    tool_name: str
    parameters: Dict[str, Any]
    result: Optional[Any] = None
    error: Optional[str] = None
