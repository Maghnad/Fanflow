"""Routing / wayfinding service.

Implements Dijkstra's algorithm over the stadium's in-memory graph to
find shortest paths between locations.  Supports both standard routes
(stairs allowed) and accessible-only routes (ramps/elevators only).
"""

from __future__ import annotations

import heapq

from app.data.accessibility import ACCESSIBILITY
from app.data.stadiums import STADIUMS, StadiumData, TransportHub, list_stadiums_summary

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

WALKING_SPEED_MPS: float = 1.2
"""Average walking speed in meters per second (casual pace in a crowd)."""

ACCESSIBLE_WALKING_SPEED_MPS: float = 0.9
"""Average wheelchair / slower walking speed in meters per second."""


# ---------------------------------------------------------------------------
# Dijkstra shortest path
# ---------------------------------------------------------------------------


def _dijkstra(
    graph: dict[str, dict[str, int]],
    start: str,
    end: str,
    congestion_map: dict[str, float] | None = None,
) -> tuple[list[str], float]:
    """Find the shortest path between two nodes using Dijkstra's algorithm.

    Args:
        graph: Adjacency dict mapping node → {neighbour: distance}.
        start: Starting node key.
        end: Destination node key.
        congestion_map: Optional dict mapping node key to congestion percentage.

    Returns:
        Tuple of (ordered path as list of node keys, total distance in meters).

    Raises:
        ValueError: If start or end node is not in the graph, or if no
            path exists between them.
    """
    # Import locally to avoid circular imports

    import contextlib
    with contextlib.suppress(Exception):
        # Default to metlife since we don't have stadium_id in _dijkstra,
        # but we can pass it down!
        pass
    if start not in graph:
        raise ValueError(f"Start location '{start}' not found in stadium map.")
    if end not in graph:
        raise ValueError(f"Destination '{end}' not found in stadium map.")

    if congestion_map is None:
        congestion_map = {}

    # Priority queue: (effective_distance, physical_distance, node, path)
    queue: list[tuple[float, float, str, list[str]]] = [(0.0, 0.0, start, [start])]
    visited: set[str] = set()

    while queue:
        eff_dist, phys_dist, node, path = heapq.heappop(queue)

        if node == end:
            return path, phys_dist

        if node in visited:
            continue
        visited.add(node)

        for neighbour, weight in graph.get(node, {}).items():
            if neighbour not in visited:
                # Apply congestion penalty
                # Example: If a gate is 80% congested, penalty is 1 + (80/100)*3 = 3.4x weight
                congestion = congestion_map.get(neighbour, 0.0)
                penalty = 1.0 + (congestion / 100.0) * 3.0
                effective_weight = weight * penalty
                heapq.heappush(
                    queue,
                    (
                        eff_dist + effective_weight,
                        phys_dist + weight,
                        neighbour,
                        path + [neighbour],
                    ),
                )

    raise ValueError(f"No path found from '{start}' to '{end}'.")


def _resolve_graph_key(graph: dict[str, dict[str, int]], key: str) -> str:
    """Resolve a location key case-insensitively against the graph.

    Tries exact match first, then uppercase, then original casing of
    graph keys.  This handles the mismatch between schema validators
    (which lowercase) and graph keys (which may be uppercase).

    Args:
        graph: The stadium graph adjacency dict.
        key: The location key to resolve.

    Returns:
        The matching key from the graph.

    Raises:
        ValueError: If no matching key is found.
    """
    # Exact match
    if key in graph:
        return key
    # Uppercase
    if key.upper() in graph:
        return key.upper()
    # Case-insensitive search
    key_lower = key.lower()
    for graph_key in graph:
        if graph_key.lower() == key_lower:
            return graph_key
    raise ValueError(f"Location '{key}' not found in stadium map.")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def calculate_distance(
    stadium_id: str,
    from_location: str,
    to_location: str,
    accessible: bool = False,
) -> tuple[list[str], float, float]:
    """Calculate the walking route between two stadium locations.

    Args:
        stadium_id: Lowercase stadium identifier.
        from_location: Starting location key.
        to_location: Destination location key.
        accessible: If True, use the accessible-only graph.

    Returns:
        Tuple of (path list, distance in meters, estimated minutes).

    Raises:
        ValueError: If the stadium or locations are not found.
    """
    stadium: StadiumData | None = STADIUMS.get(stadium_id)
    if stadium is None:
        raise ValueError(f"Stadium '{stadium_id}' not found.")

    if accessible:
        acc_data = ACCESSIBILITY.get(stadium_id)
        if acc_data is None:
            raise ValueError(f"No accessibility data for stadium '{stadium_id}'.")
        graph = acc_data["accessible_graph"]
        speed = ACCESSIBLE_WALKING_SPEED_MPS
    else:
        graph = stadium["graph"]
        speed = WALKING_SPEED_MPS

    # Resolve case-insensitive keys (schema lowercases, graph may use uppercase)
    from_key = _resolve_graph_key(graph, from_location)
    to_key = _resolve_graph_key(graph, to_location)

    # Fetch live congestion to influence routing
    from app.services.crowd_service import get_crowd_status

    try:
        crowd_status = get_crowd_status(stadium_id)
        # Create map of gate key (e.g. "A") to congestion percentage
        congestion_map = {g.gate_id: g.congestion_pct for g in crowd_status.gates}
    except Exception:
        congestion_map = {}

    path, distance = _dijkstra(graph, from_key, to_key, congestion_map)
    minutes = (distance / speed) / 60.0

    return path, distance, round(minutes, 1)


def get_stadium_info(stadium_id: str) -> dict[str, object] | None:
    """Return full information for a single stadium.

    Args:
        stadium_id: Lowercase stadium identifier.

    Returns:
        Stadium data dict with the id injected, or None.
    """
    stadium = STADIUMS.get(stadium_id)
    if stadium is None:
        return None
    return {"id": stadium_id, **stadium}


def get_all_stadiums() -> list[dict[str, str | int]]:
    """Return a summary list of all stadiums.

    Returns:
        List of dicts with 'id', 'name', 'city', 'country', 'capacity'.
    """
    return list_stadiums_summary()


def get_gate_names(stadium_id: str) -> list[str]:
    """Return human-readable gate names for a stadium.

    Args:
        stadium_id: Lowercase stadium identifier.

    Returns:
        List of gate name strings (empty if stadium not found).
    """
    stadium = STADIUMS.get(stadium_id)
    if stadium is None:
        return []
    return [g["name"] for g in stadium["gates"].values()]


def get_transport_options(stadium_id: str) -> list[TransportHub]:
    """Return transport hubs near a stadium.

    Args:
        stadium_id: Lowercase stadium identifier.

    Returns:
        List of transport hub dicts (empty if stadium not found).
    """
    stadium = STADIUMS.get(stadium_id)
    if stadium is None:
        return []
    return list(stadium["transport"])
