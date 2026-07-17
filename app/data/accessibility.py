"""Accessibility data for FIFA World Cup 2026 stadiums.

Contains accessible routes (elevator/ramp-only paths), quiet zones,
sensory rooms, sign-language staff locations, wheelchair seating,
and service animal relief areas.  All data is keyed by stadium ID.
"""

from __future__ import annotations

from typing import TypedDict

# ---------------------------------------------------------------------------
# Type definitions
# ---------------------------------------------------------------------------


class AccessibleRoute(TypedDict):
    """An accessible path segment between two locations."""

    from_location: str
    to_location: str
    distance_meters: int
    features: list[str]


class QuietZone(TypedDict):
    """A designated quiet/sensory-friendly zone."""

    name: str
    location: str
    nearest_gate: str
    capacity: int


class SignLanguageStaff(TypedDict):
    """Sign-language interpreter availability."""

    location: str
    languages: list[str]
    hours: str


class AccessibilityData(TypedDict):
    """Full accessibility record for a stadium."""

    accessible_routes: list[AccessibleRoute]
    quiet_zones: list[QuietZone]
    sign_language_staff: list[SignLanguageStaff]
    wheelchair_sections: list[str]
    service_animal_relief: list[str]
    accessible_graph: dict[str, dict[str, int]]


# ---------------------------------------------------------------------------
# Per-stadium accessibility data
# ---------------------------------------------------------------------------

ACCESSIBILITY: dict[str, AccessibilityData] = {
    "metlife": {
        "accessible_routes": [
            {"from_location": "A", "to_location": "concourse_north", "distance_meters": 70, "features": ["ramp", "wide_path"]},
            {"from_location": "concourse_north", "to_location": "elevator_north", "distance_meters": 40, "features": ["elevator"]},
            {"from_location": "elevator_north", "to_location": "concourse_east", "distance_meters": 160, "features": ["wide_path", "tactile_paving"]},
            {"from_location": "B", "to_location": "concourse_east", "distance_meters": 65, "features": ["ramp", "wide_path"]},
            {"from_location": "concourse_east", "to_location": "elevator_east", "distance_meters": 35, "features": ["elevator"]},
            {"from_location": "C", "to_location": "concourse_south", "distance_meters": 70, "features": ["ramp", "wide_path"]},
            {"from_location": "concourse_south", "to_location": "elevator_south", "distance_meters": 40, "features": ["elevator"]},
            {"from_location": "D", "to_location": "concourse_west", "distance_meters": 70, "features": ["ramp", "wide_path"]},
            {"from_location": "concourse_west", "to_location": "elevator_west", "distance_meters": 45, "features": ["elevator"]},
        ],
        "quiet_zones": [
            {"name": "Quiet Room North", "location": "concourse_north", "nearest_gate": "A", "capacity": 20},
            {"name": "Sensory Room East", "location": "concourse_east", "nearest_gate": "B", "capacity": 15},
        ],
        "sign_language_staff": [
            {"location": "Gate A Information Desk", "languages": ["ASL"], "hours": "2h before kickoff — 1h after match"},
            {"location": "Guest Services (Section 100)", "languages": ["ASL", "ISL"], "hours": "All match hours"},
        ],
        "wheelchair_sections": ["Section 100", "Section 200", "Section 300", "Section 400"],
        "service_animal_relief": ["Relief Area near Gate D (outdoor)", "Relief Area near Gate A (outdoor)"],
        "accessible_graph": {
            "A": {"concourse_north": 70},
            "B": {"concourse_east": 65},
            "C": {"concourse_south": 70},
            "D": {"concourse_west": 70},
            "concourse_north": {"A": 70, "elevator_north": 40, "concourse_east": 170, "concourse_west": 180, "restroom_north": 35, "quiet_room_north": 45},
            "concourse_east": {"B": 65, "elevator_east": 35, "concourse_north": 170, "concourse_south": 155, "restroom_east": 30, "first_aid": 45},
            "concourse_south": {"C": 70, "elevator_south": 40, "concourse_east": 155, "concourse_west": 165, "restroom_south": 35},
            "concourse_west": {"D": 70, "elevator_west": 45, "concourse_north": 180, "concourse_south": 165, "restroom_west": 40},
            "elevator_north": {"concourse_north": 40},
            "elevator_east": {"concourse_east": 35},
            "elevator_south": {"concourse_south": 40},
            "elevator_west": {"concourse_west": 45},
            "quiet_room_north": {"concourse_north": 45},
            "restroom_north": {"concourse_north": 35},
            "restroom_east": {"concourse_east": 30},
            "restroom_south": {"concourse_south": 35},
            "restroom_west": {"concourse_west": 40},
            "first_aid": {"concourse_east": 45},
        },
    },
    "sofi": {
        "accessible_routes": [
            {"from_location": "A", "to_location": "concourse_north", "distance_meters": 75, "features": ["ramp", "wide_path"]},
            {"from_location": "concourse_north", "to_location": "elevator_north", "distance_meters": 45, "features": ["elevator"]},
            {"from_location": "B", "to_location": "concourse_east", "distance_meters": 70, "features": ["ramp", "wide_path"]},
            {"from_location": "C", "to_location": "concourse_south", "distance_meters": 75, "features": ["ramp", "wide_path"]},
            {"from_location": "D", "to_location": "concourse_west", "distance_meters": 75, "features": ["ramp", "wide_path"]},
        ],
        "quiet_zones": [
            {"name": "Sensory Suite West", "location": "concourse_west", "nearest_gate": "D", "capacity": 25},
        ],
        "sign_language_staff": [
            {"location": "Guest Services (Gate A)", "languages": ["ASL"], "hours": "All match hours"},
        ],
        "wheelchair_sections": ["Section 100", "Section 200", "Section 300", "Section 400"],
        "service_animal_relief": ["Relief Area near Gate C (outdoor)"],
        "accessible_graph": {
            "A": {"concourse_north": 75},
            "B": {"concourse_east": 70},
            "C": {"concourse_south": 75},
            "D": {"concourse_west": 75},
            "concourse_north": {"A": 75, "elevator_north": 45, "concourse_east": 175, "concourse_west": 185},
            "concourse_east": {"B": 70, "concourse_north": 175, "concourse_south": 170, "first_aid": 40},
            "concourse_south": {"C": 75, "concourse_east": 170, "concourse_west": 180},
            "concourse_west": {"D": 75, "concourse_north": 185, "concourse_south": 180},
            "elevator_north": {"concourse_north": 45},
            "first_aid": {"concourse_east": 40},
        },
    },
    "att": {
        "accessible_routes": [
            {"from_location": "A", "to_location": "concourse_north", "distance_meters": 80, "features": ["ramp", "wide_path"]},
            {"from_location": "B", "to_location": "concourse_east", "distance_meters": 80, "features": ["ramp", "wide_path"]},
            {"from_location": "C", "to_location": "concourse_south", "distance_meters": 80, "features": ["ramp", "wide_path"]},
            {"from_location": "D", "to_location": "concourse_west", "distance_meters": 80, "features": ["ramp", "wide_path"]},
        ],
        "quiet_zones": [
            {"name": "Quiet Room South", "location": "concourse_south", "nearest_gate": "C", "capacity": 18},
        ],
        "sign_language_staff": [
            {"location": "Gate A Guest Services", "languages": ["ASL"], "hours": "All match hours"},
        ],
        "wheelchair_sections": ["Section 100", "Section 200", "Section 300", "Section 400"],
        "service_animal_relief": ["Relief Area near Gate D (outdoor)"],
        "accessible_graph": {
            "A": {"concourse_north": 80},
            "B": {"concourse_east": 80},
            "C": {"concourse_south": 80},
            "D": {"concourse_west": 80},
            "concourse_north": {"A": 80, "concourse_east": 185, "concourse_west": 195},
            "concourse_east": {"B": 80, "concourse_north": 185, "concourse_south": 180, "first_aid": 45},
            "concourse_south": {"C": 80, "concourse_east": 180, "concourse_west": 190},
            "concourse_west": {"D": 80, "concourse_north": 195, "concourse_south": 190},
            "first_aid": {"concourse_east": 45},
        },
    },
    "hardrock": {
        "accessible_routes": [
            {"from_location": "A", "to_location": "concourse_north", "distance_meters": 65, "features": ["ramp", "wide_path"]},
            {"from_location": "B", "to_location": "concourse_east", "distance_meters": 65, "features": ["ramp", "wide_path"]},
            {"from_location": "C", "to_location": "concourse_south", "distance_meters": 65, "features": ["ramp", "wide_path"]},
            {"from_location": "D", "to_location": "concourse_west", "distance_meters": 65, "features": ["ramp", "wide_path"]},
        ],
        "quiet_zones": [
            {"name": "Sensory Room North", "location": "concourse_north", "nearest_gate": "A", "capacity": 15},
        ],
        "sign_language_staff": [
            {"location": "Guest Services (Gate B)", "languages": ["ASL"], "hours": "All match hours"},
        ],
        "wheelchair_sections": ["Section 100", "Section 200", "Section 300"],
        "service_animal_relief": ["Relief Area near Gate A (outdoor)"],
        "accessible_graph": {
            "A": {"concourse_north": 65},
            "B": {"concourse_east": 65},
            "C": {"concourse_south": 65},
            "D": {"concourse_west": 65},
            "concourse_north": {"A": 65, "concourse_east": 160, "concourse_west": 170},
            "concourse_east": {"B": 65, "concourse_north": 160, "concourse_south": 155, "first_aid": 35},
            "concourse_south": {"C": 65, "concourse_east": 155, "concourse_west": 165},
            "concourse_west": {"D": 65, "concourse_north": 170, "concourse_south": 165},
            "first_aid": {"concourse_east": 35},
        },
    },
    "azteca": {
        "accessible_routes": [
            {"from_location": "A", "to_location": "concourse_north", "distance_meters": 85, "features": ["ramp", "wide_path"]},
            {"from_location": "B", "to_location": "concourse_east", "distance_meters": 85, "features": ["ramp", "wide_path"]},
            {"from_location": "C", "to_location": "concourse_south", "distance_meters": 85, "features": ["ramp", "wide_path"]},
            {"from_location": "D", "to_location": "concourse_west", "distance_meters": 85, "features": ["ramp", "wide_path"]},
        ],
        "quiet_zones": [
            {"name": "Sala Sensorial Norte", "location": "concourse_north", "nearest_gate": "A", "capacity": 20},
        ],
        "sign_language_staff": [
            {"location": "Servicios (Puerta A)", "languages": ["LSM"], "hours": "Horario completo del partido"},
        ],
        "wheelchair_sections": ["Sección 100", "Sección 200", "Sección 300", "Sección 400"],
        "service_animal_relief": ["Área de alivio cerca de Puerta D (exterior)"],
        "accessible_graph": {
            "A": {"concourse_north": 85},
            "B": {"concourse_east": 85},
            "C": {"concourse_south": 85},
            "D": {"concourse_west": 85},
            "concourse_north": {"A": 85, "concourse_east": 195, "concourse_west": 205},
            "concourse_east": {"B": 85, "concourse_north": 195, "concourse_south": 190, "first_aid": 45},
            "concourse_south": {"C": 85, "concourse_east": 190, "concourse_west": 200},
            "concourse_west": {"D": 85, "concourse_north": 205, "concourse_south": 200},
            "first_aid": {"concourse_east": 45},
        },
    },
    "bmo": {
        "accessible_routes": [
            {"from_location": "A", "to_location": "concourse_north", "distance_meters": 50, "features": ["ramp", "wide_path"]},
            {"from_location": "B", "to_location": "concourse_east", "distance_meters": 50, "features": ["ramp", "wide_path"]},
            {"from_location": "C", "to_location": "concourse_south", "distance_meters": 50, "features": ["ramp", "wide_path"]},
            {"from_location": "D", "to_location": "concourse_west", "distance_meters": 50, "features": ["ramp", "wide_path"]},
        ],
        "quiet_zones": [
            {"name": "Quiet Room West", "location": "concourse_west", "nearest_gate": "D", "capacity": 12},
        ],
        "sign_language_staff": [
            {"location": "Guest Services (Gate A)", "languages": ["ASL"], "hours": "All match hours"},
        ],
        "wheelchair_sections": ["Section 100", "Section 200"],
        "service_animal_relief": ["Relief Area near Gate C (outdoor)"],
        "accessible_graph": {
            "A": {"concourse_north": 50},
            "B": {"concourse_east": 50},
            "C": {"concourse_south": 50},
            "D": {"concourse_west": 50},
            "concourse_north": {"A": 50, "concourse_east": 115, "concourse_west": 125},
            "concourse_east": {"B": 50, "concourse_north": 115, "concourse_south": 110, "first_aid": 30},
            "concourse_south": {"C": 50, "concourse_east": 110, "concourse_west": 120},
            "concourse_west": {"D": 50, "concourse_north": 125, "concourse_south": 120},
            "first_aid": {"concourse_east": 30},
        },
    },
}


# ---------------------------------------------------------------------------
# Lookup helpers
# ---------------------------------------------------------------------------


def get_accessibility(stadium_id: str) -> AccessibilityData | None:
    """Return accessibility data for a stadium.

    Args:
        stadium_id: Lowercase stadium identifier.

    Returns:
        AccessibilityData dict or None if not found.
    """
    return ACCESSIBILITY.get(stadium_id)


def get_quiet_zones(stadium_id: str) -> list[QuietZone]:
    """Return quiet/sensory zones for a stadium.

    Args:
        stadium_id: Lowercase stadium identifier.

    Returns:
        List of QuietZone dicts (empty if stadium not found).
    """
    data = ACCESSIBILITY.get(stadium_id)
    return data["quiet_zones"] if data else []


def get_sign_language_info(stadium_id: str) -> list[SignLanguageStaff]:
    """Return sign-language staff information for a stadium.

    Args:
        stadium_id: Lowercase stadium identifier.

    Returns:
        List of SignLanguageStaff dicts (empty if stadium not found).
    """
    data = ACCESSIBILITY.get(stadium_id)
    return data["sign_language_staff"] if data else []
