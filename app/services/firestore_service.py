"""Firestore service for FanFlow AI.

This module provides an asynchronous client for Google Cloud Firestore.
It implements graceful degradation — if the environment lacks GCP credentials,
or USE_FIRESTORE is false, this service can simply act as a no-op or the
callers can handle the logic locally.
"""

from __future__ import annotations

import logging
from typing import Any

from google.cloud import firestore

from app.config import get_settings

logger = logging.getLogger(__name__)

_db: firestore.AsyncClient | None = None


def get_firestore_client() -> firestore.AsyncClient | None:
    """Return the shared Firestore async client, creating it if needed.

    Returns:
        Firestore AsyncClient if enabled and configured, otherwise None.
    """
    global _db
    settings = get_settings()

    if not settings.use_firestore:
        return None

    if _db is None:
        try:
            if settings.gcp_project_id:
                _db = firestore.AsyncClient(project=settings.gcp_project_id)
            else:
                _db = firestore.AsyncClient()
            logger.info("Successfully initialized Firestore AsyncClient.")
        except Exception as e:
            logger.error(f"Failed to initialize Firestore: {e}. Falling back to in-memory state.")
            _db = None

    return _db


def sync_stadium_state(
    stadium_id: str, state: dict[str, Any], incidents: list[dict[str, Any]]
) -> None:
    """Fire-and-forget sync to Firestore.

    Args:
        stadium_id: Stadium ID.
        state: Crowd state dict.
        incidents: List of active incidents.
    """
    db = get_firestore_client()
    if db is None:
        return

    import asyncio

    async def _write() -> None:
        """Write the stadium state to Firestore asynchronously."""
        try:
            doc_ref = db.collection("stadiums").document(stadium_id)
            await doc_ref.set(
                {
                    "gates": state["gates"],
                    "incidents": incidents,
                    "last_update": firestore.SERVER_TIMESTAMP,
                },
                merge=True,
            )
        except Exception as e:
            logger.error(f"Firestore sync failed: {e}")

    try:
        loop = asyncio.get_running_loop()
        loop.create_task(_write())
    except RuntimeError:
        # If there's no running loop, we can't create a task.
        pass
