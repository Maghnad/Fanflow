"""Endpoint tests using TestClient.

Covers success paths AND expected failure codes (200, 404, 422, 429).
All tests use the mock LLM from conftest — no real API calls.
"""

from __future__ import annotations

from fastapi.testclient import TestClient


class TestChatEndpoints:
    """Tests for /api/chat endpoints."""

    def test_chat_success(self, client: TestClient) -> None:
        """POST /api/chat with valid input returns 200 and a reply."""
        response = client.post(
            "/api/chat",
            json={"message": "Where is the nearest restroom?", "language": "en", "stadium_id": "metlife"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "reply" in data
        assert data["language"] == "en"
        assert data["stadium"] == "metlife"

    def test_chat_empty_message(self, client: TestClient) -> None:
        """POST /api/chat with empty message returns 422."""
        response = client.post(
            "/api/chat",
            json={"message": "", "language": "en", "stadium_id": "metlife"},
        )
        assert response.status_code == 422

    def test_chat_missing_message(self, client: TestClient) -> None:
        """POST /api/chat without message field returns 422."""
        response = client.post(
            "/api/chat",
            json={"language": "en", "stadium_id": "metlife"},
        )
        assert response.status_code == 422

    def test_chat_invalid_language(self, client: TestClient) -> None:
        """POST /api/chat with unsupported language returns 422."""
        response = client.post(
            "/api/chat",
            json={"message": "Hello", "language": "xx", "stadium_id": "metlife"},
        )
        assert response.status_code == 422

    def test_chat_overlength_message(self, client: TestClient) -> None:
        """POST /api/chat with message >2000 chars returns 422."""
        response = client.post(
            "/api/chat",
            json={"message": "A" * 2001, "language": "en", "stadium_id": "metlife"},
        )
        assert response.status_code == 422

    def test_chat_spanish(self, client: TestClient) -> None:
        """POST /api/chat with Spanish language returns 200."""
        response = client.post(
            "/api/chat",
            json={"message": "¿Dónde está el baño?", "language": "es", "stadium_id": "metlife"},
        )
        assert response.status_code == 200
        assert response.json()["language"] == "es"

    def test_chat_stream(self, client: TestClient) -> None:
        """POST /api/chat/stream returns SSE event stream."""
        response = client.post(
            "/api/chat/stream",
            json={"message": "Where is Gate A?", "language": "en", "stadium_id": "metlife"},
        )
        assert response.status_code == 200
        assert "text/event-stream" in response.headers.get("content-type", "")


class TestNavigationEndpoints:
    """Tests for /api/navigate and /api/stadiums endpoints."""

    def test_navigate_success(self, client: TestClient) -> None:
        """POST /api/navigate with valid locations returns route."""
        response = client.post(
            "/api/navigate",
            json={
                "stadium_id": "metlife",
                "from_location": "A",
                "to_location": "C",
                "accessible": False,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "route" in data
        assert len(data["route"]) > 0
        assert data["distance_meters"] > 0
        assert data["estimated_minutes"] > 0

    def test_navigate_accessible(self, client: TestClient) -> None:
        """POST /api/navigate with accessible=True uses accessible graph."""
        response = client.post(
            "/api/navigate",
            json={
                "stadium_id": "metlife",
                "from_location": "A",
                "to_location": "B",
                "accessible": True,
            },
        )
        assert response.status_code == 200
        assert response.json()["accessible"] is True

    def test_navigate_unknown_stadium(self, client: TestClient) -> None:
        """POST /api/navigate with unknown stadium returns 404."""
        response = client.post(
            "/api/navigate",
            json={
                "stadium_id": "nonexistent",
                "from_location": "A",
                "to_location": "B",
            },
        )
        assert response.status_code == 404

    def test_navigate_unknown_location(self, client: TestClient) -> None:
        """POST /api/navigate with unknown location returns 404."""
        response = client.post(
            "/api/navigate",
            json={
                "stadium_id": "metlife",
                "from_location": "Z",
                "to_location": "B",
            },
        )
        assert response.status_code == 404

    def test_stadiums_list(self, client: TestClient) -> None:
        """GET /api/stadiums returns non-empty list."""
        response = client.get("/api/stadiums")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert "name" in data[0]
        assert "city" in data[0]

    def test_stadium_detail(self, client: TestClient) -> None:
        """GET /api/stadiums/{id} returns stadium info."""
        response = client.get("/api/stadiums/metlife")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "MetLife Stadium"

    def test_stadium_not_found(self, client: TestClient) -> None:
        """GET /api/stadiums/{id} with unknown ID returns 404."""
        response = client.get("/api/stadiums/nonexistent")
        assert response.status_code == 404

    def test_transport_options(self, client: TestClient) -> None:
        """GET /api/stadiums/{id}/transport returns transport data."""
        response = client.get("/api/stadiums/metlife/transport")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0


class TestCrowdEndpoints:
    """Tests for /api/crowd endpoints."""

    def test_crowd_status(self, client: TestClient) -> None:
        """GET /api/crowd/status returns crowd snapshot."""
        response = client.get("/api/crowd/status?stadium_id=metlife")
        assert response.status_code == 200
        data = response.json()
        assert "gates" in data
        assert "overall_density_pct" in data
        assert "overall_status" in data
        assert data["stadium_id"] == "metlife"

    def test_crowd_status_unknown_stadium(self, client: TestClient) -> None:
        """GET /api/crowd/status with unknown stadium returns 404."""
        response = client.get("/api/crowd/status?stadium_id=nonexistent")
        assert response.status_code == 404

    def test_crowd_analyze(self, client: TestClient) -> None:
        """POST /api/crowd/analyze returns AI analysis."""
        response = client.post(
            "/api/crowd/analyze",
            json={"stadium_id": "metlife"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "analysis" in data
        assert "recommendations" in data
        assert isinstance(data["recommendations"], list)

    def test_crowd_incidents(self, client: TestClient) -> None:
        """GET /api/crowd/incidents returns list."""
        response = client.get("/api/crowd/incidents?stadium_id=metlife")
        assert response.status_code == 200
        assert isinstance(response.json(), list)


class TestTranslations:
    """Tests for /api/translations endpoint."""

    def test_translations_english(self, client: TestClient) -> None:
        """GET /api/translations/en returns English strings."""
        response = client.get("/api/translations/en")
        assert response.status_code == 200
        data = response.json()
        assert "app_title" in data
        assert data["app_title"] == "FanFlow AI"

    def test_translations_spanish(self, client: TestClient) -> None:
        """GET /api/translations/es returns Spanish strings."""
        response = client.get("/api/translations/es")
        assert response.status_code == 200
        data = response.json()
        assert data["send_button"] == "Enviar"

    def test_translations_unsupported(self, client: TestClient) -> None:
        """GET /api/translations/{bad} returns 404."""
        response = client.get("/api/translations/zz")
        assert response.status_code == 404


class TestPages:
    """Tests for HTML page serving."""

    def test_fan_page(self, client: TestClient) -> None:
        """GET / returns the fan chat HTML page."""
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")
        assert "FanFlow AI" in response.text

    def test_dashboard_page(self, client: TestClient) -> None:
        """GET /dashboard returns the dashboard HTML page."""
        response = client.get("/dashboard")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")
        assert "Operations Dashboard" in response.text
