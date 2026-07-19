"""Tests for signage generator and predictive heatmap — problem statement features."""

import pytest

from app.data.stadiums import STADIUMS
from app.services.crowd_service import (
    generate_dynamic_signage,
    predict_crowd_heatmap,
)


def test_generate_dynamic_signage_returns_signs() -> None:
    """Signage generator should return one sign per gate."""
    stadium_id = list(STADIUMS.keys())[0]
    signs = generate_dynamic_signage(stadium_id)
    assert isinstance(signs, list)
    assert len(signs) > 0
    for sign in signs:
        assert "board_location" in sign
        assert "message" in sign
        assert sign["priority"] in ("low", "medium", "high")


def test_generate_dynamic_signage_unknown_stadium() -> None:
    """Signage generator should raise ValueError for unknown stadium."""
    with pytest.raises(ValueError, match="not found"):
        generate_dynamic_signage("nonexistent_stadium")


def test_predict_crowd_heatmap_returns_forecast() -> None:
    """Predictive heatmap should return current + two forecast snapshots."""
    stadium_id = list(STADIUMS.keys())[0]
    result = predict_crowd_heatmap(stadium_id)
    assert "current" in result
    assert "forecast_15min" in result
    assert "forecast_30min" in result
    assert "predicted_bottlenecks" in result
    assert isinstance(result["predicted_bottlenecks"], list)
    # All gate IDs should be present in every snapshot
    for gate_id in result["current"]:
        assert gate_id in result["forecast_15min"]
        assert gate_id in result["forecast_30min"]


def test_predict_crowd_heatmap_values_in_range() -> None:
    """All forecast values should be clamped between 0 and 100."""
    stadium_id = list(STADIUMS.keys())[0]
    result = predict_crowd_heatmap(stadium_id)
    for snapshot_key in ("current", "forecast_15min", "forecast_30min"):
        for val in result[snapshot_key].values():
            assert 0 <= val <= 100, f"{snapshot_key} value {val} is out of range"


def test_predict_crowd_heatmap_unknown_stadium() -> None:
    """Heatmap should raise ValueError for unknown stadium."""
    with pytest.raises(ValueError, match="not found"):
        predict_crowd_heatmap("nonexistent_stadium")
