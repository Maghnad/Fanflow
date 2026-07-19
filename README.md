# ⚽ FanFlow AI

> **GenAI-enabled stadium operations solution for the FIFA World Cup 2026**
>
> Built for the **Google Prompt Wars** competition.

FanFlow AI is a coherent, two-surface product that uses Generative AI to improve the tournament experience for both **fans** and **stadium staff**:

1. **Fan-Facing GenAI Assistant** — A multilingual chat interface with **Voice UI (Speech-to-Text & Text-to-Speech)** that helps fans with wayfinding, accessible routing, gate information, transport options, and general venue Q&A.
2. **Staff Operations Dashboard** — Ingests simulated real-time signals (gate congestion, crowd density, incident reports, waste levels) and provides an interactive **Ops Copilot (Live AI Control Tower)** to generate plain-language alerts and actionable recommendations.
3. **Smart Congestion-Aware Routing** — Dynamically alters routing paths in real-time to steer fans away from crowded gates using Dijkstra's algorithm augmented with live congestion penalties.

---

## 🏆 Submission Requirements

### 🎯 Chosen Vertical
**Stadium Operations & Fan Experience**

### 🧠 Approach and Logic
Our approach is to bridge the gap between back-of-house stadium operations and front-of-house fan experience using Generative AI. We use a deterministic backend (FastAPI, Dijkstra's algorithm, simulated IoT sensors) to ground the AI in reality. The LLM acts as an intelligent reasoning layer on top of this structured data—translating complex operational metrics into plain-language recommendations for staff, and turning static stadium maps into a conversational, accessible, multilingual concierge for fans.

### ⚙️ How the Solution Works
1. **Data Ingestion:** The app runs a background asynchronous loop (`crowd_service.py`) that simulates live IoT sensor data (gate congestion, waste levels, incident reports) across major 2026 World Cup venues.
2. **Staff Operations (Ops Copilot):** Stadium staff view this live data on a dashboard. They can chat with the Ops Copilot, which intercepts the current state of the stadium, injects it into the prompt context, and uses the LLM to generate immediate, localized action plans (e.g., "Deploy 3 staff to Gate A to manage a 90% congestion spike").
3. **Fan Experience:** Fans use a voice-enabled, multilingual chat interface. When a fan asks for directions, the app calculates the shortest path using a graph of the stadium (`routing_service.py`). Crucially, the edge weights are dynamically penalized by the live congestion data, steering fans away from bottlenecks.

### 🤔 Assumptions Made
- We assume that by 2026, stadiums will be equipped with IoT sensors capable of estimating crowd density at major chokepoints (gates, concourses) and waste bin fill levels.
- We assume fans have internet connectivity (Wi-Fi or 5G) inside the stadium to access the web app.
- We assume stadium staff are equipped with tablets or mobile devices to access the web-based operations dashboard.
- The LLM provider (Groq/OpenAI/Gemini) will maintain high availability with low latency during the event.

---

## 🏗️ Architecture Overview

```
┌──────────────┐     HTTP/SSE      ┌──────────────────────────────────────┐
│  Fan Browser │ ◄──────────────► │           FastAPI Backend            │
│  (Vanilla JS)│                   │                                      │
└──────────────┘                   │  ┌────────┐    ┌──────────────────┐ │
                                   │  │ Routes │───►│    Services      │ │
┌──────────────┐     HTTP/Poll     │  │ (HTTP  │    │ (Business Logic) │ │
│ Staff Browser│ ◄──────────────► │  │  only) │    │                  │ │
│  (Vanilla JS)│                   │  └────────┘    └───────┬──────────┘ │
└──────────────┘                   │                        │            │
                                   │                ┌───────▼──────────┐ │
                                   │                │   LLM Client     │ │
                                   │                │ (Provider-Agnostic│ │
                                   │                │   via httpx)     │ │
                                   │                └───────┬──────────┘ │
                                   │                        │            │
                                   │              ┌─────────▼─────────┐ │
                                   │              │ Security Layer    │ │
                                   │              │ (Sanitize, Guard) │ │
                                   │              └───────────────────┘ │
                                   └──────────────────────────────────────┘
                                                    │
                                                    ▼
                                          ┌──────────────────┐
                                          │  Your LLM API    │
                                          │ (OpenAI, Gemini, │
                                          │  Groq, Ollama…)  │
                                          └──────────────────┘
```

### Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **FastAPI, fully async** | Non-blocking I/O throughout for efficiency |
| **Strict route/service separation** | Routes contain zero business logic — all in `app/services/` |
| **In-memory dict lookups** | No DB needed for static data — eliminates unnecessary round-trips |
| **Provider-agnostic LLM client** | Swap providers by editing one file (`app/llm/client.py`) |
| **SSE streaming for chat** | Reduces perceived latency — tokens appear as they arrive |
| **Client-side rendering** | Server never templates dynamic content — efficiency + clean separation |
| **LRU cache on LLM calls** | Avoids redundant API calls for repeated queries |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- An LLM API key (optional — the app starts without one using fallback responses)

### Setup

```bash
# Clone the repository
git clone <repo-url>
cd fanflow-ai

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your LLM API key and provider settings

# Run the development server
uvicorn app.main:app --reload --port 8000
```

### Access the Application

- **Fan Chat:** http://localhost:8000/
- **Staff Dashboard:** http://localhost:8000/dashboard
- **API Docs:** http://localhost:8000/docs

---

## 🔌 Plugging In Your LLM Provider

FanFlow AI uses a provider-agnostic LLM client. Configure it via `.env`:

```env
LLM_PROVIDER=openai          # Identifier (for logging)
LLM_MODEL=gpt-4o-mini        # Model name
LLM_API_KEY=sk-your-key      # API key (server-side only)
LLM_BASE_URL=https://api.openai.com/v1  # OpenAI-compatible endpoint
```

**Compatible providers** (any OpenAI-compatible API):

| Provider | `LLM_BASE_URL` | `LLM_MODEL` |
|----------|----------------|-------------|
| OpenAI | `https://api.openai.com/v1` | `gpt-4o-mini` |
| Google (via OpenAI compat) | `https://generativelanguage.googleapis.com/v1beta/openai` | `gemini-2.0-flash` |
| Groq | `https://api.groq.com/openai/v1` | `llama-3.1-70b-versatile` |
| Together | `https://api.together.xyz/v1` | `meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo` |
| Ollama (local) | `http://localhost:11434/v1` | `llama3.1` |

To swap providers, change **only** the `.env` file. No code changes needed.

---

## 📋 Problem Statement Alignment

> "Build a GenAI-enabled solution that enhances stadium operations and the overall tournament experience for fans, organizers, volunteers, or venue staff."

| Shipped Feature | Problem Statement Pillar | Implementation |
|----------------|-------------------------|----------------|
| Multilingual fan chat (6 languages) | **"multilingual assistance"** | Language selector + LLM language instruction + full i18n UI strings (EN, ES, FR, AR, PT, DE) |
| Wayfinding + gate info + Smart Routing | **"navigation"** | Dijkstra shortest-path over stadium graphs, dynamically penalized by real-time gate congestion to avoid bottlenecks. |
| Accessible routing + Voice UI | **"accessibility"** | Speech-to-Text and Text-to-Speech for visually impaired fans, wheelchair sections, sensory rooms. |
| Real-time crowd & sustainability dashboard | **"crowd management"** + **"operational intelligence"** | Simulated gate congestion, waste bin levels, per-gate status cards, incident feed |
| Ops Copilot (Live AI Control Tower) | **"real-time decision support"** | Interactive chat interface for staff. LLM analyzes live crowd snapshot + waste levels + incidents → plain-language answers and action items |
| 📺 Dynamic Signage Generator | **"real-time signage updates"** | Generates dynamic, AI-driven directional text to steer fans away from red-status gates. |
| 🔮 Predictive Crowd Heatmap | **"crowd density forecasting"** | Generates gate traffic forecasts 15 and 30 minutes into the future to alert staff of bottlenecks before they happen. |

**All seven features are fully functional**, not mocked. Real 2026 venue data (MetLife Stadium, SoFi Stadium, AT&T Stadium, Hard Rock Stadium, Estadio Azteca, BMO Field).

---

## 🧪 Testing

```bash
# Run full test suite
pytest tests/ -v --tb=short

# Run only fuzzing tests
pytest tests/test_fuzzing.py -v

# Run only endpoint tests
pytest tests/test_endpoints.py -v

# Run only accessibility tests
pytest tests/test_accessibility.py -v
```

### Test Coverage

| Test File | What It Tests | Count |
|-----------|--------------|-------|
| `test_endpoints.py` | All API routes (including new signage/heatmap routes) — success + error paths (200, 404, 422) | 24 tests |
| `test_fuzzing.py` | Property-based fuzzing with Hypothesis on sanitization, density classification, walking calculations | 16 tests |
| `test_llm_mocked.py` | Chat flow with deterministic mock LLM — prompt construction, SSE format, output sanitization | 9 tests |
| `test_accessibility.py` | Semantic HTML, ARIA attributes, 100% no inline styles, meta tags, heading hierarchy | 21 tests |
| `test_signage_heatmap.py` | AI dynamic signage generator and predictive crowd forecasting outputs | 5 tests |
| `test_chat_service.py` | Chat assistant fallback logic and stadium contextualization | 3 tests |
| `test_config.py` | Configuration settings and LLM provider config verification | 2 tests |
| `test_crowd_service.py` | Crowd status simulation state checks | 2 tests |
| `test_firestore.py` | Firestore live state synchronization | 4 tests |
| `test_llm_client.py` | LLM client request validation, sanitization, and fallback | 3 tests |
| `test_routing_service.py` | Pathfinding routing speed calculations | 2 tests |

**LLM is mocked in all tests** — CI never hits the real API. Total of **91 passing tests** with **85% total code coverage**!

---

## 🔒 Security

| Measure | Implementation |
|---------|---------------|
| **Input validation** | Strict Pydantic schemas on every endpoint — reject non-matching requests with 422 |
| **Input sanitization** | `sanitize_input()` strips control chars, normalizes Unicode, enforces 2000-char limit |
| **Prompt injection defense** | Heuristic pattern detection + delimiter-based system/user role separation (never concatenated) |
| **Output sanitization** | `sanitize_llm_output()` redacts leaked API keys, enforces output length limit |
| **Rate limiting** | SlowAPI with per-IP limits (30/min on chat, 60/min on other endpoints, 10/min on analysis) |
| **CORS** | Explicit origin allowlist — never `*` |
| **API key isolation** | LLM API key lives server-side only, read from env vars, never exposed to frontend |
| **Dependency scanning** | `pip-audit` in CI pipeline |

---

## 📁 Project Structure

```
fanflow-ai/
├── app/
│   ├── main.py              # App factory, CORS, rate limiting, routes
│   ├── config.py             # pydantic-settings env var config
│   ├── schemas.py            # Pydantic request/response models
│   ├── security.py           # Sanitization, injection guards, rate limiter
│   ├── llm/
│   │   └── client.py         # Provider-agnostic LLM abstraction
│   ├── routes/
│   │   ├── chat.py           # POST /api/chat, /api/chat/stream
│   │   ├── crowd.py          # GET/POST crowd status & analysis
│   │   ├── navigation.py     # POST /api/navigate, GET /api/stadiums
│   │   └── static_pages.py   # Serve HTML pages
│   ├── services/
│   │   ├── chat_service.py   # Multilingual chat logic & prompt building
│   │   ├── crowd_service.py  # Crowd simulation & AI analysis
│   │   └── routing_service.py # Dijkstra wayfinding
│   └── data/
│       ├── stadiums.py       # Real 2026 venue data
│       ├── accessibility.py  # Accessible routes, quiet zones
│       └── translations.py   # 6-language i18n tables
├── tests/
│   ├── conftest.py           # Mock LLM fixtures
│   ├── test_endpoints.py     # API route tests
│   ├── test_fuzzing.py       # Hypothesis property-based tests
│   ├── test_llm_mocked.py    # Chat flow with mock LLM
│   └── test_accessibility.py # Semantic HTML & ARIA checks
├── static/css/               # base.css, fan.css, dashboard.css
├── static/js/                # fan.js, dashboard.js
├── templates/                # fan.html, dashboard.html
├── .github/workflows/ci.yml  # pytest + ruff + mypy + pip-audit
├── .pre-commit-config.yaml   # black + isort + ruff + mypy
├── .env.example              # Environment template
├── pyproject.toml            # Project config & tool settings
└── requirements.txt          # Pinned dependencies
```

---

## 🛠️ Code Quality

- **Type hints** on every function signature (enforced by `mypy --strict`)
- **Docstrings** on every function and class
- **Linting** via `ruff` (covers flake8 + isort + pyupgrade)
- **Formatting** via `black` (100-char line length)
- **Pre-commit hooks** committed and configured
- **CI pipeline** runs all checks on every push

```bash
# Run quality checks locally
ruff check .
mypy app/ --ignore-missing-imports
black --check .
```

---

## ♿ Accessibility

- Semantic HTML5: `<header>`, `<nav>`, `<main>`, `<section>`, `<footer>` — no div soup
- ARIA roles: `role="log"`, `role="banner"`, `role="main"`, `role="contentinfo"`
- `aria-live="polite"` on chat feed, `aria-live="assertive"` on incident feed
- Skip-to-content link for keyboard users
- Full keyboard navigability (Enter to send, Escape to clear, Tab navigation)
- WCAG AA contrast ratios (all text/background combos ≥ 4.5:1)
- RTL support for Arabic (`dir="rtl"` on language change)
- No inline styles (100% in CSS files)
- Focus-visible styles (bright accent outline, never `outline: none`)

---

## 📄 License

MIT
