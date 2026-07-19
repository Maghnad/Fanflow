"""Static page serving routes.

Serves the semantic HTML templates for the fan chat and staff dashboard.
These are shell pages — all dynamic content is rendered client-side via
JavaScript, never server-side templated.
"""

from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.config import get_settings

router = APIRouter(tags=["pages"])

templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse, summary="Fan chat assistant page")
async def fan_page(request: Request) -> HTMLResponse:
    """Serve the fan-facing chat assistant HTML shell.

    Args:
        request: FastAPI request.

    Returns:
        Rendered fan.html template.
    """
    settings = get_settings()
    return templates.TemplateResponse(
        request=request, name="fan.html", context={"maps_api_key": settings.gcp_maps_api_key}
    )


@router.get("/dashboard", response_class=HTMLResponse, summary="Staff ops dashboard page")
async def dashboard_page(request: Request) -> HTMLResponse:
    """Serve the staff operations dashboard HTML shell.

    Args:
        request: FastAPI request.

    Returns:
        Rendered dashboard.html template.
    """
    return templates.TemplateResponse(request=request, name="dashboard.html")
