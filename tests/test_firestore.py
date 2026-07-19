"""Tests for Firestore integration."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.config import get_settings
from app.services.firestore_service import get_firestore_client, sync_stadium_state


@pytest.fixture(autouse=True)
def reset_firestore() -> None:
    """Reset the global firestore client before each test."""
    import app.services.firestore_service as fs

    fs._db = None


def test_get_firestore_client_disabled() -> None:
    """Test get_firestore_client returns None when disabled."""
    settings = get_settings()
    settings.use_firestore = False
    assert get_firestore_client() is None


@patch("app.services.firestore_service.firestore")
def test_get_firestore_client_enabled(mock_firestore: AsyncMock) -> None:
    """Test get_firestore_client initializes successfully."""
    settings = get_settings()
    settings.use_firestore = True
    settings.gcp_project_id = "test-project"

    # Reset
    import app.services.firestore_service as fs

    fs._db = None

    client = get_firestore_client()
    assert client is not None
    mock_firestore.AsyncClient.assert_called_once_with(project="test-project")


@patch("app.services.firestore_service.firestore")
def test_get_firestore_client_fallback(mock_firestore: AsyncMock) -> None:
    """Test get_firestore_client falls back gracefully on exception."""
    settings = get_settings()
    settings.use_firestore = True
    settings.gcp_project_id = "test-project"

    import app.services.firestore_service as fs

    fs._db = None

    mock_firestore.AsyncClient.side_effect = Exception("Boom")

    client = get_firestore_client()
    assert client is None


@pytest.mark.asyncio
@patch("app.services.firestore_service.firestore")
@patch("app.services.firestore_service.logger")
async def test_sync_stadium_state(mock_logger: AsyncMock, mock_firestore: AsyncMock) -> None:
    """Test sync_stadium_state pushes to Firestore."""
    settings = get_settings()
    settings.use_firestore = True

    import app.services.firestore_service as fs

    fs._db = None

    mock_db = MagicMock()
    mock_db.collection.return_value.document.return_value.set = AsyncMock()
    mock_firestore.AsyncClient.return_value = mock_db

    # We call it, which fires off a task.
    sync_stadium_state("stadium_1", {"gates": {}}, [])

    # Let asyncio loop run tasks
    import asyncio

    await asyncio.sleep(0.01)

    mock_db.collection.assert_called_once_with("stadiums")
    mock_db.collection().document.assert_called_once_with("stadium_1")
    mock_db.collection().document().set.assert_called_once()
