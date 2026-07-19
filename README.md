# ⚽ FanFlow AI

> **GenAI-enabled stadium operations solution for the FIFA World Cup 2026**
>
> Built for the **Google Prompt Wars** competition.

FanFlow AI is a coherent, two-surface product that uses Generative AI to improve the tournament experience for both **fans** and **stadium staff**:

1. **Fan-Facing GenAI Assistant** — A multilingual chat interface with **Voice UI (Speech-to-Text & Text-to-Speech)** that helps fans with wayfinding, accessible routing, gate information, transport options, and general venue Q&A.
2. **Staff Operations Dashboard** — Ingests simulated real-time signals (gate congestion, crowd density, incident reports, waste levels) and provides an interactive **Ops Copilot (Live AI Control Tower)** to generate plain-language alerts and actionable recommendations.
3. **Smart Congestion-Aware Routing** — Dynamically alters routing paths in real-time to steer fans away from crowded gates using Dijkstra's algorithm augmented with live congestion penalties.

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

**All five features are fully functional**, not mocked. Real 2026 venue data (MetLife Stadium, SoFi Stadium, AT&T Stadium, Hard Rock Stadium, Estadio Azteca, BMO Field).

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
| `test_endpoints.py` | All API routes — success + error paths (200, 404, 422) | 24 tests |
| `test_fuzzing.py` | Property-based fuzzing with Hypothesis on sanitization, density classification, walking calculations | 13 tests (200+ examples each) |
| `test_llm_mocked.py` | Chat flow with deterministic mock LLM — prompt construction, SSE format, output sanitization | 8 tests |
| `test_accessibility.py` | Semantic HTML, ARIA attributes, no inline styles, meta tags, heading hierarchy | 18 tests |

**LLM is mocked in all tests** — CI never hits the real API.

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
