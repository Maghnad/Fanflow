"""FIFA World Cup 2026 stadium data — in-memory dict lookups.

Contains real 2026 host venues with gate layouts, section mappings,
transport hubs, and walking-distance graphs for wayfinding.  This data
is static and intentionally kept in-memory to avoid unnecessary DB/network
round-trips (an efficiency design choice).
"""

from __future__ import annotations

from typing import TypedDict

# ---------------------------------------------------------------------------
# Type definitions
# ---------------------------------------------------------------------------


class GateInfo(TypedDict):
    """Gate metadata."""

    name: str
    zone: str
    capacity_pct: float
    lat: float
    lon: float


class TransportHub(TypedDict):
    """Transport connection point near a stadium."""

    name: str
    type: str
    distance_meters: int
    directions: str


class StadiumData(TypedDict):
    """Full stadium record."""

    name: str
    city: str
    country: str
    capacity: int
    gates: dict[str, GateInfo]
    sections: dict[str, list[str]]
    transport: list[TransportHub]
    graph: dict[str, dict[str, int]]


# ---------------------------------------------------------------------------
# Stadium registry
# ---------------------------------------------------------------------------

STADIUMS: dict[str, StadiumData] = {
    "metlife": {
        "name": "MetLife Stadium",
        "city": "East Rutherford, NJ",
        "country": "USA",
        "capacity": 82500,
        "gates": {
            "A": {
                "name": "Gate A",
                "zone": "North",
                "capacity_pct": 0.0,
                "lat": 40.8135,
                "lon": -74.0745,
            },
            "B": {
                "name": "Gate B",
                "zone": "East",
                "capacity_pct": 0.0,
                "lat": 40.8130,
                "lon": -74.0735,
            },
            "C": {
                "name": "Gate C",
                "zone": "South",
                "capacity_pct": 0.0,
                "lat": 40.8120,
                "lon": -74.0745,
            },
            "D": {
                "name": "Gate D",
                "zone": "West",
                "capacity_pct": 0.0,
                "lat": 40.8130,
                "lon": -74.0755,
            },
            "E": {
                "name": "Gate E",
                "zone": "North-East",
                "capacity_pct": 0.0,
                "lat": 40.8133,
                "lon": -74.0738,
            },
            "F": {
                "name": "Gate F",
                "zone": "South-West",
                "capacity_pct": 0.0,
                "lat": 40.8123,
                "lon": -74.0752,
            },
        },
        "sections": {
            "100": ["A", "B"],
            "200": ["B", "C"],
            "300": ["C", "D"],
            "400": ["D", "A"],
            "500": ["E", "F"],
        },
        "transport": [
            {
                "name": "Meadowlands Rail Station",
                "type": "rail",
                "distance_meters": 400,
                "directions": "Exit Gate A, follow signs north.",
            },
            {
                "name": "Lot K Parking",
                "type": "parking",
                "distance_meters": 200,
                "directions": "Exit Gate D, cross pedestrian bridge.",
            },
            {
                "name": "Bus Terminal East",
                "type": "bus",
                "distance_meters": 350,
                "directions": "Exit Gate B, walk east 5 minutes.",
            },
        ],
        "graph": {
            "A": {"B": 180, "D": 200, "E": 100, "concourse_north": 50},
            "B": {"A": 180, "C": 170, "E": 120, "concourse_east": 50},
            "C": {"B": 170, "D": 190, "F": 110, "concourse_south": 50},
            "D": {"A": 200, "C": 190, "F": 130, "concourse_west": 50},
            "E": {"A": 100, "B": 120, "concourse_north": 80},
            "F": {"C": 110, "D": 130, "concourse_south": 70},
            "concourse_north": {
                "A": 50,
                "E": 80,
                "concourse_east": 150,
                "concourse_west": 160,
                "restroom_north": 30,
                "food_court_1": 60,
            },
            "concourse_east": {
                "B": 50,
                "concourse_north": 150,
                "concourse_south": 140,
                "restroom_east": 25,
                "first_aid": 40,
            },
            "concourse_south": {
                "C": 50,
                "F": 70,
                "concourse_east": 140,
                "concourse_west": 150,
                "restroom_south": 30,
                "food_court_2": 55,
            },
            "concourse_west": {
                "D": 50,
                "concourse_north": 160,
                "concourse_south": 150,
                "restroom_west": 35,
                "fan_zone": 70,
            },
            "restroom_north": {"concourse_north": 30},
            "restroom_east": {"concourse_east": 25},
            "restroom_south": {"concourse_south": 30},
            "restroom_west": {"concourse_west": 35},
            "food_court_1": {"concourse_north": 60},
            "food_court_2": {"concourse_south": 55},
            "first_aid": {"concourse_east": 40},
            "fan_zone": {"concourse_west": 70},
        },
    },
    "sofi": {
        "name": "SoFi Stadium",
        "city": "Inglewood, CA",
        "country": "USA",
        "capacity": 70240,
        "gates": {
            "A": {
                "name": "Gate A",
                "zone": "North",
                "capacity_pct": 0.0,
                "lat": 33.9535,
                "lon": -118.3392,
            },
            "B": {
                "name": "Gate B",
                "zone": "East",
                "capacity_pct": 0.0,
                "lat": 33.9530,
                "lon": -118.3382,
            },
            "C": {
                "name": "Gate C",
                "zone": "South",
                "capacity_pct": 0.0,
                "lat": 33.9520,
                "lon": -118.3392,
            },
            "D": {
                "name": "Gate D",
                "zone": "West",
                "capacity_pct": 0.0,
                "lat": 33.9530,
                "lon": -118.3402,
            },
        },
        "sections": {
            "100": ["A", "B"],
            "200": ["B", "C"],
            "300": ["C", "D"],
            "400": ["D", "A"],
        },
        "transport": [
            {
                "name": "Inglewood Transit Center",
                "type": "rail",
                "distance_meters": 600,
                "directions": "Exit Gate A, walk north along Prairie Ave.",
            },
            {
                "name": "Lot 1 Parking",
                "type": "parking",
                "distance_meters": 250,
                "directions": "Exit Gate C, follow orange signs.",
            },
            {
                "name": "Rideshare Pickup Zone",
                "type": "rideshare",
                "distance_meters": 300,
                "directions": "Exit Gate D, follow blue signs west.",
            },
        ],
        "graph": {
            "A": {"B": 200, "D": 210, "concourse_north": 55},
            "B": {"A": 200, "C": 190, "concourse_east": 55},
            "C": {"B": 190, "D": 200, "concourse_south": 55},
            "D": {"A": 210, "C": 200, "concourse_west": 55},
            "concourse_north": {
                "A": 55,
                "concourse_east": 160,
                "concourse_west": 170,
                "restroom_north": 30,
                "food_court_1": 50,
            },
            "concourse_east": {
                "B": 55,
                "concourse_north": 160,
                "concourse_south": 155,
                "first_aid": 35,
            },
            "concourse_south": {
                "C": 55,
                "concourse_east": 155,
                "concourse_west": 165,
                "restroom_south": 30,
                "food_court_2": 45,
            },
            "concourse_west": {
                "D": 55,
                "concourse_north": 170,
                "concourse_south": 165,
                "fan_zone": 60,
            },
            "restroom_north": {"concourse_north": 30},
            "restroom_south": {"concourse_south": 30},
            "food_court_1": {"concourse_north": 50},
            "food_court_2": {"concourse_south": 45},
            "first_aid": {"concourse_east": 35},
            "fan_zone": {"concourse_west": 60},
        },
    },
    "att": {
        "name": "AT&T Stadium",
        "city": "Arlington, TX",
        "country": "USA",
        "capacity": 80000,
        "gates": {
            "A": {
                "name": "Gate A",
                "zone": "North",
                "capacity_pct": 0.0,
                "lat": 32.7480,
                "lon": -97.0925,
            },
            "B": {
                "name": "Gate B",
                "zone": "East",
                "capacity_pct": 0.0,
                "lat": 32.7475,
                "lon": -97.0915,
            },
            "C": {
                "name": "Gate C",
                "zone": "South",
                "capacity_pct": 0.0,
                "lat": 32.7465,
                "lon": -97.0925,
            },
            "D": {
                "name": "Gate D",
                "zone": "West",
                "capacity_pct": 0.0,
                "lat": 32.7475,
                "lon": -97.0935,
            },
        },
        "sections": {
            "100": ["A", "B"],
            "200": ["B", "C"],
            "300": ["C", "D"],
            "400": ["D", "A"],
        },
        "transport": [
            {
                "name": "CentrePort/DFW Station",
                "type": "rail",
                "distance_meters": 3200,
                "directions": "Take shuttle from Gate A parking area.",
            },
            {
                "name": "Lot 4 Parking",
                "type": "parking",
                "distance_meters": 350,
                "directions": "Exit Gate D, walk west.",
            },
        ],
        "graph": {
            "A": {"B": 220, "D": 230, "concourse_north": 60},
            "B": {"A": 220, "C": 210, "concourse_east": 60},
            "C": {"B": 210, "D": 220, "concourse_south": 60},
            "D": {"A": 230, "C": 220, "concourse_west": 60},
            "concourse_north": {
                "A": 60,
                "concourse_east": 170,
                "concourse_west": 180,
                "restroom_north": 35,
                "food_court_1": 55,
            },
            "concourse_east": {
                "B": 60,
                "concourse_north": 170,
                "concourse_south": 165,
                "first_aid": 40,
            },
            "concourse_south": {
                "C": 60,
                "concourse_east": 165,
                "concourse_west": 175,
                "restroom_south": 35,
            },
            "concourse_west": {
                "D": 60,
                "concourse_north": 180,
                "concourse_south": 175,
                "fan_zone": 65,
            },
            "restroom_north": {"concourse_north": 35},
            "restroom_south": {"concourse_south": 35},
            "food_court_1": {"concourse_north": 55},
            "first_aid": {"concourse_east": 40},
            "fan_zone": {"concourse_west": 65},
        },
    },
    "hardrock": {
        "name": "Hard Rock Stadium",
        "city": "Miami Gardens, FL",
        "country": "USA",
        "capacity": 65326,
        "gates": {
            "A": {
                "name": "Gate A",
                "zone": "North",
                "capacity_pct": 0.0,
                "lat": 25.9580,
                "lon": -80.2389,
            },
            "B": {
                "name": "Gate B",
                "zone": "East",
                "capacity_pct": 0.0,
                "lat": 25.9575,
                "lon": -80.2379,
            },
            "C": {
                "name": "Gate C",
                "zone": "South",
                "capacity_pct": 0.0,
                "lat": 25.9565,
                "lon": -80.2389,
            },
            "D": {
                "name": "Gate D",
                "zone": "West",
                "capacity_pct": 0.0,
                "lat": 25.9575,
                "lon": -80.2399,
            },
        },
        "sections": {
            "100": ["A", "B"],
            "200": ["B", "C"],
            "300": ["C", "D"],
            "400": ["D", "A"],
        },
        "transport": [
            {
                "name": "Express Bus to Downtown Miami",
                "type": "bus",
                "distance_meters": 200,
                "directions": "Exit Gate A, follow shuttle signs.",
            },
            {
                "name": "Orange Parking Lot",
                "type": "parking",
                "distance_meters": 300,
                "directions": "Exit Gate C, walk south.",
            },
        ],
        "graph": {
            "A": {"B": 190, "D": 200, "concourse_north": 50},
            "B": {"A": 190, "C": 185, "concourse_east": 50},
            "C": {"B": 185, "D": 195, "concourse_south": 50},
            "D": {"A": 200, "C": 195, "concourse_west": 50},
            "concourse_north": {
                "A": 50,
                "concourse_east": 145,
                "concourse_west": 155,
                "restroom_north": 25,
                "food_court_1": 45,
            },
            "concourse_east": {
                "B": 50,
                "concourse_north": 145,
                "concourse_south": 140,
                "first_aid": 30,
            },
            "concourse_south": {
                "C": 50,
                "concourse_east": 140,
                "concourse_west": 150,
                "restroom_south": 25,
            },
            "concourse_west": {
                "D": 50,
                "concourse_north": 155,
                "concourse_south": 150,
                "fan_zone": 55,
            },
            "restroom_north": {"concourse_north": 25},
            "restroom_south": {"concourse_south": 25},
            "food_court_1": {"concourse_north": 45},
            "first_aid": {"concourse_east": 30},
            "fan_zone": {"concourse_west": 55},
        },
    },
    "azteca": {
        "name": "Estadio Azteca",
        "city": "Mexico City",
        "country": "Mexico",
        "capacity": 87523,
        "gates": {
            "A": {
                "name": "Puerta A",
                "zone": "Norte",
                "capacity_pct": 0.0,
                "lat": 19.3029,
                "lon": -99.1505,
            },
            "B": {
                "name": "Puerta B",
                "zone": "Este",
                "capacity_pct": 0.0,
                "lat": 19.3024,
                "lon": -99.1495,
            },
            "C": {
                "name": "Puerta C",
                "zone": "Sur",
                "capacity_pct": 0.0,
                "lat": 19.3014,
                "lon": -99.1505,
            },
            "D": {
                "name": "Puerta D",
                "zone": "Oeste",
                "capacity_pct": 0.0,
                "lat": 19.3024,
                "lon": -99.1515,
            },
        },
        "sections": {
            "100": ["A", "B"],
            "200": ["B", "C"],
            "300": ["C", "D"],
            "400": ["D", "A"],
        },
        "transport": [
            {
                "name": "Metro Azteca",
                "type": "metro",
                "distance_meters": 500,
                "directions": "Salida Puerta A, caminar al norte por 5 minutos.",
            },
            {
                "name": "Estacionamiento Principal",
                "type": "parking",
                "distance_meters": 200,
                "directions": "Salida Puerta D, seguir señales.",
            },
        ],
        "graph": {
            "A": {"B": 250, "D": 260, "concourse_north": 65},
            "B": {"A": 250, "C": 240, "concourse_east": 65},
            "C": {"B": 240, "D": 250, "concourse_south": 65},
            "D": {"A": 260, "C": 250, "concourse_west": 65},
            "concourse_north": {
                "A": 65,
                "concourse_east": 180,
                "concourse_west": 190,
                "restroom_north": 35,
                "food_court_1": 60,
            },
            "concourse_east": {
                "B": 65,
                "concourse_north": 180,
                "concourse_south": 175,
                "first_aid": 40,
            },
            "concourse_south": {
                "C": 65,
                "concourse_east": 175,
                "concourse_west": 185,
                "restroom_south": 35,
            },
            "concourse_west": {
                "D": 65,
                "concourse_north": 190,
                "concourse_south": 185,
                "fan_zone": 70,
            },
            "restroom_north": {"concourse_north": 35},
            "restroom_south": {"concourse_south": 35},
            "food_court_1": {"concourse_north": 60},
            "first_aid": {"concourse_east": 40},
            "fan_zone": {"concourse_west": 70},
        },
    },
    "bmo": {
        "name": "BMO Field",
        "city": "Toronto, ON",
        "country": "Canada",
        "capacity": 30000,
        "gates": {
            "A": {
                "name": "Gate A",
                "zone": "North",
                "capacity_pct": 0.0,
                "lat": 43.6332,
                "lon": -79.4186,
            },
            "B": {
                "name": "Gate B",
                "zone": "East",
                "capacity_pct": 0.0,
                "lat": 43.6327,
                "lon": -79.4176,
            },
            "C": {
                "name": "Gate C",
                "zone": "South",
                "capacity_pct": 0.0,
                "lat": 43.6322,
                "lon": -79.4186,
            },
            "D": {
                "name": "Gate D",
                "zone": "West",
                "capacity_pct": 0.0,
                "lat": 43.6327,
                "lon": -79.4196,
            },
        },
        "sections": {
            "100": ["A", "B"],
            "200": ["B", "C"],
            "300": ["C", "D"],
            "400": ["D", "A"],
        },
        "transport": [
            {
                "name": "Exhibition GO Station",
                "type": "rail",
                "distance_meters": 300,
                "directions": "Exit Gate A, walk north to Lakeshore Blvd.",
            },
            {
                "name": "Lot A Parking",
                "type": "parking",
                "distance_meters": 150,
                "directions": "Exit Gate C, follow signs.",
            },
        ],
        "graph": {
            "A": {"B": 140, "D": 150, "concourse_north": 35},
            "B": {"A": 140, "C": 135, "concourse_east": 35},
            "C": {"B": 135, "D": 145, "concourse_south": 35},
            "D": {"A": 150, "C": 145, "concourse_west": 35},
            "concourse_north": {
                "A": 35,
                "concourse_east": 100,
                "concourse_west": 110,
                "restroom_north": 20,
            },
            "concourse_east": {
                "B": 35,
                "concourse_north": 100,
                "concourse_south": 95,
                "first_aid": 25,
            },
            "concourse_south": {
                "C": 35,
                "concourse_east": 95,
                "concourse_west": 105,
                "restroom_south": 20,
            },
            "concourse_west": {
                "D": 35,
                "concourse_north": 110,
                "concourse_south": 105,
                "fan_zone": 40,
            },
            "restroom_north": {"concourse_north": 20},
            "restroom_south": {"concourse_south": 20},
            "first_aid": {"concourse_east": 25},
            "fan_zone": {"concourse_west": 40},
        },
    },
}


# ---------------------------------------------------------------------------
# Lookup helpers
# ---------------------------------------------------------------------------


def get_stadium(stadium_id: str) -> StadiumData | None:
    """Return stadium data by ID, or None if not found.

    Args:
        stadium_id: Lowercase stadium identifier.

    Returns:
        StadiumData dict or None.
    """
    return STADIUMS.get(stadium_id)


def list_stadium_ids() -> list[str]:
    """Return all available stadium IDs.

    Returns:
        List of stadium identifier strings.
    """
    return list(STADIUMS.keys())


def list_stadiums_summary() -> list[dict[str, str | int]]:
    """Return a summary list of all stadiums.

    Returns:
        List of dicts with 'id', 'name', 'city', 'country', 'capacity'.
    """
    return [
        {
            "id": sid,
            "name": s["name"],
            "city": s["city"],
            "country": s["country"],
            "capacity": s["capacity"],
        }
        for sid, s in STADIUMS.items()
    ]
