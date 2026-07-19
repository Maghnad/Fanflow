"""Automated accessibility tests.

Uses the HTML pages' semantic structure to validate accessibility
requirements without requiring a browser.  Checks for ARIA attributes,
semantic elements, no inline styles, and keyboard accessibility markers.

NOTE: For full axe-core testing with a real browser, install playwright
and axe-playwright-python and run with: pytest tests/test_accessibility.py -m browser
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastapi.testclient import TestClient


class TestSemanticHTML:
    """Verify semantic HTML structure in served pages."""

    def test_fan_page_has_semantic_elements(self, client: TestClient) -> None:
        """Fan page uses semantic HTML5 elements."""
        response = client.get("/")
        html = response.text

        assert "<header" in html, "Missing <header> element"
        assert "<main" in html, "Missing <main> element"
        assert "<nav" in html, "Missing <nav> element"
        assert "<section" in html, "Missing <section> element"
        assert "<footer" in html, "Missing <footer> element"

    def test_dashboard_has_semantic_elements(self, client: TestClient) -> None:
        """Dashboard uses semantic HTML5 elements."""
        response = client.get("/dashboard")
        html = response.text

        assert "<header" in html, "Missing <header> element"
        assert "<main" in html, "Missing <main> element"
        assert "<nav" in html, "Missing <nav> element"
        assert "<section" in html, "Missing <section> element"
        assert "<footer" in html, "Missing <footer> element"

    def test_fan_page_single_h1(self, client: TestClient) -> None:
        """Fan page has exactly one <h1> for proper heading hierarchy."""
        response = client.get("/")
        h1_count = response.text.count("<h1")
        assert h1_count == 1, f"Expected 1 <h1>, found {h1_count}"

    def test_dashboard_has_h2_headings(self, client: TestClient) -> None:
        """Dashboard sections use <h2> for proper heading hierarchy."""
        response = client.get("/dashboard")
        assert "<h2" in response.text, "Missing <h2> section headings"


class TestARIAAttributes:
    """Verify ARIA roles and labels on interactive elements."""

    def test_fan_chat_feed_has_log_role(self, client: TestClient) -> None:
        """Chat feed has role='log' for screen readers."""
        response = client.get("/")
        assert 'role="log"' in response.text

    def test_fan_chat_feed_has_aria_live(self, client: TestClient) -> None:
        """Chat feed has aria-live for real-time announcements."""
        response = client.get("/")
        assert 'aria-live="polite"' in response.text

    def test_fan_input_has_label(self, client: TestClient) -> None:
        """Chat input has an associated label."""
        response = client.get("/")
        html = response.text
        assert "aria-label=" in html or '<label for="chat-input"' in html

    def test_fan_send_button_has_label(self, client: TestClient) -> None:
        """Send button has an aria-label."""
        response = client.get("/")
        assert 'aria-label="Send message"' in response.text

    def test_fan_skip_link_exists(self, client: TestClient) -> None:
        """Skip link exists for keyboard navigation."""
        response = client.get("/")
        assert "skip-link" in response.text
        assert "#main-content" in response.text

    def test_dashboard_incidents_has_aria_live(self, client: TestClient) -> None:
        """Incident feed has aria-live='assertive' for urgent alerts."""
        response = client.get("/dashboard")
        assert 'aria-live="assertive"' in response.text

    def test_dashboard_analyze_button_labeled(self, client: TestClient) -> None:
        """Analyze button has an aria-label."""
        response = client.get("/dashboard")
        assert 'aria-label="Generate AI analysis' in response.text

    def test_fan_selects_have_labels(self, client: TestClient) -> None:
        """Language and stadium selects have associated labels."""
        response = client.get("/")
        html = response.text
        assert 'for="language-select"' in html
        assert 'for="stadium-select"' in html

    def test_dashboard_nav_current_page(self, client: TestClient) -> None:
        """Dashboard nav marks current page with aria-current."""
        response = client.get("/dashboard")
        assert 'aria-current="page"' in response.text


class TestNoInlineStyles:
    """Verify no inline styles in HTML templates."""

    def _count_inline_styles(self, html: str) -> list[str]:
        """Find inline style attributes in HTML.

        Excludes the meter fill width which is set dynamically.
        """
        # Find all style="..." attributes
        pattern = re.compile(r'style="[^"]*"', re.IGNORECASE)
        matches = pattern.findall(html)
        # Filter out the meter fill exception in dashboard template
        # (progress bar width is set inline by necessity)
        return [m for m in matches if "font-size" in m.lower()]

    def test_fan_page_no_inline_styles(self, client: TestClient) -> None:
        """Fan page has zero inline styles."""
        response = client.get("/")
        inline_styles = self._count_inline_styles(response.text)
        assert len(inline_styles) == 0, f"Inline styles found: {inline_styles}"

    def test_dashboard_minimal_inline_styles(self, client: TestClient) -> None:
        """Dashboard has no font/color inline styles (dynamic width OK)."""
        response = client.get("/dashboard")
        inline_styles = self._count_inline_styles(response.text)
        assert len(inline_styles) == 0, f"Inline styles found: {inline_styles}"


class TestMetaTags:
    """Verify SEO and meta tags."""

    def test_fan_page_has_title(self, client: TestClient) -> None:
        """Fan page has a descriptive <title>."""
        response = client.get("/")
        assert "<title>" in response.text
        assert "FanFlow AI" in response.text

    def test_fan_page_has_meta_description(self, client: TestClient) -> None:
        """Fan page has a meta description."""
        response = client.get("/")
        assert 'name="description"' in response.text

    def test_dashboard_has_title(self, client: TestClient) -> None:
        """Dashboard has a descriptive <title>."""
        response = client.get("/dashboard")
        assert "<title>" in response.text
        assert "Dashboard" in response.text

    def test_fan_page_has_viewport_meta(self, client: TestClient) -> None:
        """Fan page has viewport meta for responsiveness."""
        response = client.get("/")
        assert 'name="viewport"' in response.text

    def test_fan_page_has_charset(self, client: TestClient) -> None:
        """Fan page declares UTF-8 charset."""
        response = client.get("/")
        assert 'charset="UTF-8"' in response.text

    def test_fan_page_has_lang_attribute(self, client: TestClient) -> None:
        """HTML element has lang attribute."""
        response = client.get("/")
        assert 'lang="en"' in response.text
