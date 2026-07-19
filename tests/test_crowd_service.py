import pytest

from app.data.stadiums import STADIUMS
from app.services.crowd_service import (
    _incidents,
    get_crowd_status,
)


@pytest.mark.asyncio
async def test_get_crowd_status() -> None:
    stadium_id = list(STADIUMS.keys())[0]
    status = get_crowd_status(stadium_id)
    assert status.stadium_id == stadium_id
    assert len(status.gates) > 0
    assert 0 <= status.overall_density_pct <= 100


@pytest.mark.asyncio
async def test_active_incidents() -> None:
    stadium_id = list(STADIUMS.keys())[0]
    # Ensure initialized
    get_crowd_status(stadium_id)
    # Inject a dummy incident
    _incidents[stadium_id].append(
        {
            "id": "inc-test",
            "type": "medical",
            "description": "Test incident",
            "location": "Gate A",
            "severity": "medium",
            "status": "active",
            "timestamp": "2026-07-19T10:00:00Z",
        }
    )
    status = get_crowd_status(stadium_id)
    assert len(status.incidents) >= 1
    assert any(inc.id == "inc-test" for inc in status.incidents)
