"""Pydantic request/response models for all API endpoints.

Every incoming request is strictly validated through these schemas —
anything that doesn't match is rejected with 422.  This is a core
security measure: no unvalidated data reaches business logic or the LLM.
"""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

from app.data.translations import SUPPORTED_LANGUAGES

# ---------------------------------------------------------------------------
# Chat
# ---------------------------------------------------------------------------


class ChatRequest(BaseModel):
    """Request body for the chat endpoint.

    model_config = {"extra": "forbid"}


    Attributes:
        message: User's chat message (1–2000 characters).
        language: ISO 639-1 language code.
        stadium_id: Stadium identifier for context.
    """

    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="User chat message",
    )
    language: str = Field(
        default="en",
        description="ISO 639-1 language code",
    )
    stadium_id: str = Field(
        default="metlife",
        description="Stadium identifier",
    )

    @field_validator("language")
    @classmethod
    def validate_language(cls, v: str) -> str:
        """Ensure the language code is supported."""
        if v not in SUPPORTED_LANGUAGES:
            raise ValueError(
                f"Unsupported language '{v}'. Supported: {', '.join(SUPPORTED_LANGUAGES)}"
            )
        return v

    @field_validator("stadium_id")
    @classmethod
    def validate_stadium_id(cls, v: str) -> str:
        """Ensure the stadium_id is lowercase alphanumeric."""
        v = v.lower().strip()
        if not v.isalnum():
            raise ValueError("Stadium ID must be alphanumeric.")
        return v


class ChatResponse(BaseModel):
    """Response body for the chat endpoint.

    Attributes:
        reply: AI-generated response text.
        language: Language of the response.
        stadium: Stadium ID used for context.
    """

    reply: str
    language: str
    stadium: str


# ---------------------------------------------------------------------------
# Navigation
# ---------------------------------------------------------------------------


class NavigationRequest(BaseModel):
    """Request body for the navigation/wayfinding endpoint.

    Attributes:
        stadium_id: Stadium identifier.
        from_location: Starting location (gate letter or named point).
        to_location: Destination location.
        accessible: If True, only use accessible routes (ramps, elevators).
    """

    model_config = {"extra": "forbid"}

    stadium_id: str = Field(
        ...,
        description="Stadium identifier",
    )
    from_location: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Starting location",
    )
    to_location: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Destination location",
    )
    accessible: bool = Field(
        default=False,
        description="Use accessible-only routes",
    )

    @field_validator("stadium_id")
    @classmethod
    def validate_stadium_id(cls, v: str) -> str:
        """Ensure the stadium_id is lowercase alphanumeric."""
        v = v.lower().strip()
        if not v.isalnum():
            raise ValueError("Stadium ID must be alphanumeric.")
        return v

    @field_validator("from_location", "to_location")
    @classmethod
    def normalize_location(cls, v: str) -> str:
        """Normalize location names to lowercase for lookup."""
        return v.lower().strip()


class NavigationResponse(BaseModel):
    """Response body for the navigation endpoint.

    Attributes:
        route: Ordered list of location names in the path.
        distance_meters: Total walking distance in meters.
        estimated_minutes: Estimated walking time in minutes.
        accessible: Whether the route uses only accessible paths.
        stadium_id: Stadium ID.
    """

    route: list[str]
    distance_meters: float
    estimated_minutes: float
    accessible: bool
    stadium_id: str


# ---------------------------------------------------------------------------
# Crowd / Dashboard
# ---------------------------------------------------------------------------


class GateStatus(BaseModel):
    """Status of a single gate.

    Attributes:
        gate_id: Gate letter/identifier.
        name: Human-readable gate name.
        zone: Stadium zone.
        congestion_pct: Current congestion as a percentage (0–100).
        status: Status level ('green', 'yellow', 'red').
    """

    gate_id: str
    name: str
    zone: str
    congestion_pct: float
    status: str


class IncidentReport(BaseModel):
    """A simulated incident report.

    Attributes:
        id: Unique incident identifier.
        type: Incident type (medical, security, lost_child, equipment).
        severity: Severity level ('low', 'medium', 'high', 'critical').
        location: Where the incident was reported.
        description: Brief description.
        timestamp: ISO format timestamp string.
        resolved: Whether the incident has been resolved.
    """

    id: str
    type: str
    severity: str
    location: str
    description: str
    timestamp: str
    resolved: bool = False


class CrowdStatusResponse(BaseModel):
    """Response body for the crowd status endpoint.

    Attributes:
        stadium_id: Stadium identifier.
        stadium_name: Human-readable stadium name.
        overall_density_pct: Overall crowd density percentage.
        overall_status: Overall status ('green', 'yellow', 'red').
        gates: Per-gate status list.
        incidents: Active incident reports.
        last_updated: ISO timestamp of the last data refresh.
    """

    stadium_id: str
    stadium_name: str
    overall_density_pct: float
    overall_status: str
    gates: list[GateStatus]
    incidents: list[IncidentReport]
    waste_levels: dict[str, float] = Field(default_factory=dict)
    last_updated: str


class CrowdAnalysisRequest(BaseModel):
    """Request body for the AI crowd analysis endpoint.

    Attributes:
        stadium_id: Stadium identifier.
    """

    model_config = {"extra": "forbid"}

    stadium_id: str = Field(
        default="metlife",
        description="Stadium identifier",
    )

    @field_validator("stadium_id")
    @classmethod
    def validate_stadium_id(cls, v: str) -> str:
        """Ensure the stadium_id is lowercase alphanumeric."""
        v = v.lower().strip()
        if not v.isalnum():
            raise ValueError("Stadium ID must be alphanumeric.")
        return v


class CrowdAnalysisResponse(BaseModel):
    """Response body for the AI crowd analysis endpoint.

    Attributes:
        stadium_id: Stadium identifier.
        analysis: Plain-language AI analysis of crowd conditions.
        recommendations: List of recommended actions.
    """

    stadium_id: str
    analysis: str
    recommendations: list[str]


class OpsChatRequest(BaseModel):
    """Request body for the ops chat copilot endpoint.

    Attributes:
        message: The staff member's query.
        stadium_id: Stadium identifier.
    """

    model_config = {"extra": "forbid"}

    message: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="User query",
    )
    stadium_id: str = Field(
        default="metlife",
        description="Stadium identifier",
    )

    @field_validator("stadium_id")
    @classmethod
    def validate_stadium_id(cls, v: str) -> str:
        """Ensure the stadium_id is lowercase alphanumeric."""
        v = v.lower().strip()
        if not v.isalnum():
            raise ValueError("Stadium ID must be alphanumeric.")
        return v


class OpsChatResponse(BaseModel):
    """Response body for the ops chat copilot endpoint.

    Attributes:
        reply: AI-generated response text based on real-time data.
    """

    reply: str
