from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class StandardHeaders(BaseModel):
    """Standard request headers for internal tracking."""

    request_id: str = Field(..., alias="X-Request-ID")
    org_id: Optional[str] = Field(None, alias="X-Org-ID")
    user_id: Optional[str] = Field(None, alias="X-User-ID")


class ErrorResponse(BaseModel):
    """Standard error response format."""

    error: str
    message: str
    request_id: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class HealthCheckResponse(BaseModel):
    """Standard health check response."""

    status: str = "healthy"
    version: str
    service: Optional[str] = None
    components: Dict[str, str] = Field(default_factory=dict)
