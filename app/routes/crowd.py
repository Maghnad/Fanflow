"""Crowd management / ops dashboard API routes.

GET  /api/crowd/status    — current crowd snapshot
POST /api/crowd/analyze   — GenAI crowd analysis
GET  /api/crowd/incidents — active incidents
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from app.schemas import (
    CrowdAnalysisRequest,
    CrowdAnalysisResponse,
    CrowdStatusResponse,
    OpsChatRequest,
    OpsChatResponse,
)
from app.security import limiter
from app.services import crowd_service

router = APIRouter(prefix="/api/crowd", tags=["crowd"])


@router.get(
    "/status",
    response_model=CrowdStatusResponse,
    summary="Get current crowd status for a stadium",
)
@limiter.limit("60/minute")
async def crowd_status(request: Request, stadium_id: str = "metlife") -> CrowdStatusResponse:
    """Return the current simulated crowd status.

    Args:
        request: FastAPI request.
        stadium_id: Stadium identifier (query parameter).

    Returns:
        CrowdStatusResponse with gate congestion and incidents.
    """
    try:
        return crowd_service.get_crowd_status(stadium_id.lower())
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post(
    "/analyze",
    response_model=CrowdAnalysisResponse,
    summary="Generate AI analysis of current crowd conditions",
)
@limiter.limit("10/minute")
async def crowd_analyze(
    request: Request,
    body: CrowdAnalysisRequest,
) -> CrowdAnalysisResponse:
    """Use GenAI to analyze crowd data and generate recommendations.

    Args:
        request: FastAPI request.
        body: CrowdAnalysisRequest with stadium_id.

    Returns:
        CrowdAnalysisResponse with analysis and recommendations.
    """
    try:
        return await crowd_service.analyze_crowd(body.stadium_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get(
    "/incidents",
    summary="Get active incidents at a stadium",
)
@limiter.limit("60/minute")
async def crowd_incidents(request: Request, stadium_id: str = "metlife") -> list[dict[str, object]]:
    """Return active (unresolved) incidents for a stadium.

    Args:
        request: FastAPI request.
        stadium_id: Stadium identifier.

    Returns:
        List of incident dicts.
    """
    try:
        status = crowd_service.get_crowd_status(stadium_id.lower())
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return [inc.model_dump() for inc in status.incidents]


@router.post(
    "/ops/chat",
    response_model=OpsChatResponse,
    summary="Chat with the Operations Copilot",
)
@limiter.limit("20/minute")
async def ops_chat_endpoint(
    request: Request,
    body: OpsChatRequest,
) -> OpsChatResponse:
    """Chat with the AI Ops Copilot using real-time data context.

    Args:
        request: FastAPI request.
        body: OpsChatRequest with message and stadium_id.

    Returns:
        OpsChatResponse with the AI's reply.
    """
    try:
        reply = await crowd_service.ops_chat(body.stadium_id, body.message)
        return OpsChatResponse(reply=reply)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
