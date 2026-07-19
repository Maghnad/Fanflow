"""Crowd management / ops dashboard service.

Simulates real-time crowd signals (gate congestion, density, incidents)
and uses GenAI to generate plain-language analyses and recommended
actions for stadium staff.  The simulation engine updates state over
time to mimic pre-match → match → post-match crowd patterns.
"""

from __future__ import annotations

import math
import random
import time
import uuid
from datetime import UTC, datetime

from app.data.stadiums import get_stadium
from app.llm import client as llm_client
from app.schemas import CrowdAnalysisResponse, CrowdStatusResponse, GateStatus, IncidentReport
from app.services.firestore_service import sync_stadium_state

# ---------------------------------------------------------------------------
# Simulation state (in-memory, resets on restart — by design)
# ---------------------------------------------------------------------------

_simulation_state: dict[str, dict[str, object]] = {}
_incidents: dict[str, list[dict[str, object]]] = {}
_last_update: dict[str, float] = {}

# How often to refresh simulation data (seconds)
_UPDATE_INTERVAL: float = 5.0

# Incident generation probability per update cycle
_INCIDENT_PROBABILITY: float = 0.08

_INCIDENT_TYPES: list[dict[str, str]] = [
    {"type": "medical", "severity": "high", "description": "Fan requires medical attention"},
    {
        "type": "medical",
        "severity": "medium",
        "description": "Fan feeling unwell, requests first aid",
    },
    {
        "type": "security",
        "severity": "medium",
        "description": "Unauthorized access attempt at restricted area",
    },
    {"type": "security", "severity": "high", "description": "Altercation reported between fans"},
    {"type": "lost_child", "severity": "critical", "description": "Unaccompanied minor reported"},
    {"type": "equipment", "severity": "low", "description": "Turnstile malfunction at gate"},
    {
        "type": "equipment",
        "severity": "medium",
        "description": "Lighting issue in concourse section",
    },
    {"type": "crowd", "severity": "high", "description": "Crowd density exceeding safe threshold"},
]


# ---------------------------------------------------------------------------
# Density classification
# ---------------------------------------------------------------------------


def classify_density(pct: float) -> str:
    """Classify a congestion percentage into a status level.

    Args:
        pct: Congestion percentage (0–100).

    Returns:
        'green' (0–60), 'yellow' (60–80), or 'red' (80+).
    """
    if pct >= 80.0:
        return "red"
    if pct >= 60.0:
        return "yellow"
    return "green"


# ---------------------------------------------------------------------------
# Simulation engine
# ---------------------------------------------------------------------------


def _init_stadium_state(stadium_id: str) -> None:
    """Initialize simulation state for a stadium.

    Args:
        stadium_id: Lowercase stadium identifier.
    """
    stadium = get_stadium(stadium_id)
    if stadium is None:
        return

    gate_states: dict[str, float] = {}
    waste_states: dict[str, float] = {}
    for gate_id in stadium["gates"]:
        # Start with random base congestion (20–50%)
        gate_states[gate_id] = random.uniform(20.0, 50.0)
    for zone in ["North", "South", "East", "West", "Concourse"]:
        waste_states[zone] = random.uniform(10.0, 30.0)

    _simulation_state[stadium_id] = {"gates": gate_states, "waste": waste_states}
    _incidents[stadium_id] = []
    _last_update[stadium_id] = time.time()


def _update_simulation(stadium_id: str) -> None:
    """Advance the simulation by one tick.

    Uses a sinusoidal pattern to model crowd flow over time, plus
    random perturbations to keep the data dynamic.

    Args:
        stadium_id: Lowercase stadium identifier.
    """
    now = time.time()
    last = _last_update.get(stadium_id, now)

    if now - last < _UPDATE_INTERVAL:
        return  # Too soon to update

    state = _simulation_state.get(stadium_id)
    if state is None:
        _init_stadium_state(stadium_id)
        return

    gate_states: dict[str, float] = state["gates"]  # type: ignore[assignment]

    # Sinusoidal base (simulates crowd waves)
    phase = (now % 600) / 600 * 2 * math.pi  # 10-minute cycle
    wave = math.sin(phase) * 15  # ±15% swing

    for gate_id in gate_states:
        # Random walk + wave
        delta = random.gauss(0, 3) + wave * random.uniform(0.5, 1.5)
        new_val = gate_states[gate_id] + delta
        # Clamp to 0–100
        gate_states[gate_id] = max(0.0, min(100.0, new_val))

    waste_states: dict[str, float] = state.get("waste", {})  # type: ignore[assignment]
    for zone in waste_states:
        # Waste steadily increases, sometimes drops if "emptied"
        if random.random() < 0.05:
            waste_states[zone] = random.uniform(0.0, 10.0)  # Emptied
        else:
            waste_states[zone] = min(100.0, waste_states[zone] + random.uniform(0.5, 2.0))

    # Maybe generate an incident
    if random.random() < _INCIDENT_PROBABILITY:
        incident_template = random.choice(_INCIDENT_TYPES)
        stadium = get_stadium(stadium_id)
        location = f"Gate {random.choice(list(stadium['gates'].keys()))}" if stadium else "Unknown"
        _incidents.setdefault(stadium_id, []).append(
            {
                "id": str(uuid.uuid4())[:8],
                "type": incident_template["type"],
                "severity": incident_template["severity"],
                "location": location,
                "description": incident_template["description"],
                "timestamp": datetime.now(UTC).isoformat(),
                "resolved": False,
            }
        )

    # Keep only last 20 incidents
    if len(_incidents.get(stadium_id, [])) > 20:
        _incidents[stadium_id] = _incidents[stadium_id][-20:]

    _last_update[stadium_id] = now
    sync_stadium_state(stadium_id, state, _incidents[stadium_id])


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def get_crowd_status(stadium_id: str) -> CrowdStatusResponse:
    """Return the current simulated crowd status for a stadium.

    Args:
        stadium_id: Lowercase stadium identifier.

    Returns:
        CrowdStatusResponse with per-gate status and incidents.

    Raises:
        ValueError: If the stadium is not found.
    """
    stadium = get_stadium(stadium_id)
    if stadium is None:
        raise ValueError(f"Stadium '{stadium_id}' not found.")

    # Initialize if needed
    if stadium_id not in _simulation_state:
        _init_stadium_state(stadium_id)

    # Advance simulation
    _update_simulation(stadium_id)

    state = _simulation_state[stadium_id]
    gate_states: dict[str, float] = state["gates"]  # type: ignore[assignment]
    waste_states: dict[str, float] = state.get("waste", {})  # type: ignore[assignment]

    gates: list[GateStatus] = []
    for gate_id, gate_info in stadium["gates"].items():
        pct = round(gate_states.get(gate_id, 0.0), 1)
        gates.append(
            GateStatus(
                gate_id=gate_id,
                name=gate_info["name"],
                zone=gate_info["zone"],
                congestion_pct=pct,
                status=classify_density(pct),
            )
        )

    overall = round(sum(g.congestion_pct for g in gates) / len(gates), 1) if gates else 0.0

    incidents = [
        IncidentReport(**inc)  # type: ignore[arg-type]
        for inc in _incidents.get(stadium_id, [])
        if not inc.get("resolved", False)
    ]

    return CrowdStatusResponse(
        stadium_id=stadium_id,
        stadium_name=stadium["name"],
        overall_density_pct=overall,
        overall_status=classify_density(overall),
        gates=gates,
        incidents=incidents,
        waste_levels={k: round(v, 1) for k, v in waste_states.items()},
        last_updated=datetime.now(UTC).isoformat(),
    )


async def analyze_crowd(stadium_id: str) -> CrowdAnalysisResponse:
    """Use GenAI to analyze current crowd conditions and generate recommendations.

    Args:
        stadium_id: Lowercase stadium identifier.

    Returns:
        CrowdAnalysisResponse with plain-language analysis and action items.
    """
    status = get_crowd_status(stadium_id)

    # Build a data snapshot for the LLM
    gate_summary = "\n".join(
        f"  - {g.name} ({g.zone}): {g.congestion_pct}% congestion [{g.status.upper()}]"
        for g in status.gates
    )
    incident_summary = (
        "\n".join(
            f"  - [{i.severity.upper()}] {i.type}: {i.description} at {i.location} ({i.timestamp})"
            for i in status.incidents
        )
        or "  No active incidents."
    )

    prompt = (
        f"Current crowd status at {status.stadium_name}:\n"
        f"Overall density: {status.overall_density_pct}% [{status.overall_status.upper()}]\n\n"
        f"Gate-by-gate congestion:\n{gate_summary}\n\n"
        f"Active incidents:\n{incident_summary}\n\n"
        "Based on this data, provide:\n"
        "1. A brief plain-language analysis of the current situation (2-3 sentences).\n"
        "2. A numbered list of 3-5 specific, actionable recommendations for stadium staff."
    )

    system_prompt = (
        "You are the FanFlow AI operations intelligence assistant for FIFA World Cup 2026. "
        "You analyze real-time crowd data and provide clear, actionable recommendations "
        "to stadium staff. Be concise and specific. Focus on safety first, then efficiency."
    )

    raw_response = await llm_client.generate(
        prompt=prompt,
        system=system_prompt,
        use_cache=False,  # Always fresh analysis
    )

    # Parse recommendations from the response
    lines = raw_response.strip().split("\n")
    recommendations: list[str] = []
    analysis_parts: list[str] = []

    in_recommendations = False
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        # Detect numbered recommendations
        if stripped and stripped[0].isdigit() and "." in stripped[:4]:
            in_recommendations = True
            # Remove the number prefix
            rec_text = stripped.split(".", 1)[1].strip() if "." in stripped else stripped
            recommendations.append(rec_text)
        elif not in_recommendations:
            analysis_parts.append(stripped)

    analysis = " ".join(analysis_parts) if analysis_parts else raw_response
    if not recommendations:
        recommendations = [raw_response]

    return CrowdAnalysisResponse(
        stadium_id=stadium_id,
        analysis=analysis,
        recommendations=recommendations,
    )


async def ops_chat(stadium_id: str, message: str) -> str:
    """Use GenAI as an operations copilot for the stadium staff.

    Args:
        stadium_id: Lowercase stadium identifier.
        message: Staff member's query.

    Returns:
        String reply from the LLM.
    """
    status = get_crowd_status(stadium_id)

    # Build a data snapshot for the LLM
    gate_summary = "\n".join(
        f"  - {g.name} ({g.zone}): {g.congestion_pct}% congestion [{g.status.upper()}]"
        for g in status.gates
    )
    incident_summary = (
        "\n".join(
            f"  - [{i.severity.upper()}] {i.type}: {i.description} at {i.location} ({i.timestamp})"
            for i in status.incidents
        )
        or "  No active incidents."
    )
    waste_summary = (
        "\n".join(f"  - {zone}: {pct}% full" for zone, pct in status.waste_levels.items())
        or "  No waste data."
    )

    system_prompt = (
        "You are the FanFlow AI Command Center Copilot for FIFA World Cup 2026 organizers. "
        "You assist stadium staff by answering questions using real-time operational data. "
        "Keep your answers concise, direct, and focused on operational safety and efficiency.\n\n"
        f"=== REAL-TIME DATA (STADIUM: {status.stadium_name}) ===\n"
        f"Overall density: {status.overall_density_pct}% [{status.overall_status.upper()}]\n\n"
        f"Gate-by-gate congestion:\n{gate_summary}\n\n"
        f"Active incidents:\n{incident_summary}\n\n"
        f"Sustainability / Waste Bin Levels:\n{waste_summary}\n"
        "=======================================================\n"
    )

    try:
        raw_response = await llm_client.generate(
            prompt=message,
            system=system_prompt,
            use_cache=False,
        )
        return raw_response
    except Exception as e:
        return f"Unable to connect to Ops Copilot at this time. ({str(e)})"


def generate_dynamic_signage(stadium_id: str) -> list[dict[str, str]]:
    """Generate AI-driven directional messages for digital signage boards.

    Analyzes current gate congestion to produce plain-language messages
    that can be pushed to stadium digital displays, directing fans away
    from congested gates toward less busy alternatives.

    Args:
        stadium_id: Lowercase stadium identifier.

    Returns:
        List of signage dicts with 'board_location', 'message', and 'priority'.

    Raises:
        ValueError: If the stadium is not found.
    """
    status = get_crowd_status(stadium_id)
    signs: list[dict[str, str]] = []

    # Find the least congested gate for rerouting suggestions
    sorted_gates = sorted(status.gates, key=lambda g: g.congestion_pct)
    least_busy = sorted_gates[0] if sorted_gates else None

    for gate in status.gates:
        if gate.status == "red":
            alt = least_busy.name if least_busy and least_busy.gate_id != gate.gate_id else "staff"
            signs.append(
                {
                    "board_location": gate.name,
                    "message": (
                        f"⚠️ {gate.name} is congested ({gate.congestion_pct:.0f}%). "
                        f"Please use {alt} for faster entry."
                    ),
                    "priority": "high",
                }
            )
        elif gate.status == "yellow":
            signs.append(
                {
                    "board_location": gate.name,
                    "message": (
                        f"ℹ️ {gate.name} is moderately busy ({gate.congestion_pct:.0f}%). "
                        "Allow extra time."
                    ),
                    "priority": "medium",
                }
            )
        else:
            signs.append(
                {
                    "board_location": gate.name,
                    "message": f"✅ {gate.name} — entry is smooth. Welcome!",
                    "priority": "low",
                }
            )

    return signs


def predict_crowd_heatmap(stadium_id: str) -> dict[str, object]:
    """Predict crowd density 15 and 30 minutes into the future.

    Uses the current congestion data and a simple linear-trend model to
    forecast whether each gate will become more or less congested over
    the next 15–30 minutes.  This gives ops staff early warning of
    bottlenecks before they happen.

    Args:
        stadium_id: Lowercase stadium identifier.

    Returns:
        Dict with 'current', 'forecast_15min', and 'forecast_30min' snapshots,
        each mapping gate IDs to predicted congestion percentages.

    Raises:
        ValueError: If the stadium is not found.
    """
    status = get_crowd_status(stadium_id)

    current: dict[str, float] = {}
    forecast_15: dict[str, float] = {}
    forecast_30: dict[str, float] = {}

    for gate in status.gates:
        pct = gate.congestion_pct
        current[gate.gate_id] = pct

        # Simple predictive model: if above 60%, trending up; if below, trending down
        if pct >= 80:
            trend = random.uniform(-5, 3)  # Near capacity — slight regression to mean
        elif pct >= 60:
            trend = random.uniform(1, 8)  # Yellow zone — likely to worsen
        else:
            trend = random.uniform(-2, 4)  # Green zone — slight upward drift

        forecast_15[gate.gate_id] = round(max(0, min(100, pct + trend)), 1)
        forecast_30[gate.gate_id] = round(max(0, min(100, pct + trend * 1.8)), 1)

    bottlenecks: list[str] = [
        gid for gid, val in forecast_30.items() if val >= 80 and current[gid] < 80
    ]

    return {
        "stadium_id": stadium_id,
        "current": current,
        "forecast_15min": forecast_15,
        "forecast_30min": forecast_30,
        "predicted_bottlenecks": bottlenecks,
    }
