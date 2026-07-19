"""Navigation / wayfinding API routes.

POST /api/navigate            — calculate a route
GET  /api/stadiums            — list all stadiums
GET  /api/stadiums/{id}       — single stadium details
GET  /api/stadiums/{id}/transport — transport options
GET  /api/translations/{lang} — UI strings for a language
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter, HTTPException, Request

if TYPE_CHECKING:
    from app.data.stadiums import TransportHub
from app.data.translations import get_ui_strings, is_supported_language
from app.schemas import NavigationRequest, NavigationResponse
from app.security import limiter
from app.services import routing_service

router = APIRouter(tags=["navigation"])


@router.post(
    "/api/navigate",
    response_model=NavigationResponse,
    summary="Calculate a walking route between two stadium locations",
)
@limiter.limit("60/minute")
async def navigate(request: Request, body: NavigationRequest) -> NavigationResponse:
    """Calculate the shortest path between two locations in a stadium.

    Args:
        request: FastAPI request (needed by rate limiter).
        body: Validated NavigationRequest.

    Returns:
        NavigationResponse with route, distance, and estimated time.
    """
    try:
        path, distance, minutes = routing_service.calculate_distance(
            stadium_id=body.stadium_id,
            from_location=body.from_location,
            to_location=body.to_location,
            accessible=body.accessible,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return NavigationResponse(
        route=path,
        distance_meters=distance,
        estimated_minutes=minutes,
        accessible=body.accessible,
        stadium_id=body.stadium_id,
    )


@router.get(
    "/api/stadiums",
    summary="List all FIFA World Cup 2026 stadiums",
)
@limiter.limit("60/minute")
async def list_stadiums(request: Request) -> list[dict[str, str | int]]:
    """Return a summary list of all available stadiums.

    Args:
        request: FastAPI request.

    Returns:
        List of stadium summary dicts.
    """
    return routing_service.get_all_stadiums()


@router.get(
    "/api/stadiums/{stadium_id}",
    summary="Get detailed information about a specific stadium",
)
@limiter.limit("60/minute")
async def get_stadium(request: Request, stadium_id: str) -> dict[str, object]:
    """Return full information for a single stadium.

    Args:
        request: FastAPI request.
        stadium_id: Lowercase stadium identifier.

    Returns:
        Stadium data dict.
    """
    info = routing_service.get_stadium_info(stadium_id.lower())
    if info is None:
        raise HTTPException(status_code=404, detail=f"Stadium '{stadium_id}' not found.")
    return info


@router.get(
    "/api/stadiums/{stadium_id}/transport",
    summary="Get transport options near a stadium",
)
@limiter.limit("60/minute")
async def get_transport(request: Request, stadium_id: str) -> list[TransportHub]:
    """Return transport hubs near a stadium.

    Args:
        request: FastAPI request.
        stadium_id: Lowercase stadium identifier.

    Returns:
        List of transport hub dicts.
    """
    options = routing_service.get_transport_options(stadium_id.lower())
    if not options:
        raise HTTPException(status_code=404, detail=f"No transport data for '{stadium_id}'.")
    return options


@router.get(
    "/api/translations/{language}",
    summary="Get UI translation strings for a language",
)
@limiter.limit("60/minute")
async def get_translations(request: Request, language: str) -> dict[str, str]:
    """Return UI strings for the given language.

    Args:
        request: FastAPI request.
        language: ISO 639-1 language code.

    Returns:
        Dict of UI string keys to translated values.
    """
    if not is_supported_language(language):
        raise HTTPException(status_code=404, detail=f"Language '{language}' not supported.")
    return get_ui_strings(language)
