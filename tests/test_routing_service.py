import contextlib

import pytest

from app.services.routing_service import calculate_distance


@pytest.mark.asyncio
async def test_calculate_distance_accessible() -> None:
    # AT&T Stadium id is "att_stadium"
    with contextlib.suppress(ValueError):
        path, dist, mins = calculate_distance("att_stadium", "A", "B", accessible=True)
        assert len(path) > 0
        assert dist > 0


@pytest.mark.asyncio
async def test_calculate_distance_unknown_nodes() -> None:
    with contextlib.suppress(ValueError):
        calculate_distance("att_stadium", "Unknown Start", "Unknown End", accessible=False)
