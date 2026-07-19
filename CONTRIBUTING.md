# Contributing to FanFlow AI

Thank you for your interest in contributing to FanFlow AI! This document outlines our development practices.

## Development Setup

```bash
# Clone and install
git clone <repo-url>
cd fanflow-ai
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
pip install -e ".[dev]"

# Set up pre-commit hooks
pre-commit install
```

## Code Quality Standards

### Type Safety
- **Every** function must have full type annotations (enforced by `mypy --strict`).
- Use `from __future__ import annotations` at the top of every module.

### Documentation
- **Every** public function and class must have a Google-style docstring.
- Include `Args:`, `Returns:`, and `Raises:` sections where applicable.

### Linting & Formatting
- We use `ruff` for linting and `black` for formatting.
- Line length is 100 characters.
- Run checks locally before pushing:

```bash
ruff check .
black --check .
mypy app/ --ignore-missing-imports
```

### Testing
- Write tests for every new feature or bug fix.
- We use `pytest` with `pytest-asyncio` and `hypothesis` for property-based testing.
- The LLM client is **always** mocked in tests — CI must never hit a real API.
- Run the full suite with coverage:

```bash
pytest tests/ -v --cov=app --tb=short
```

## Architecture Rules

1. **Routes contain zero business logic.** All logic lives in `app/services/`.
2. **The LLM client is the only module that talks to external APIs.** Never import `httpx` outside `app/llm/client.py`.
3. **All user input passes through `app/security.sanitize_input()` before touching business logic or the LLM.**
4. **Static data lives in `app/data/`.** No database needed for venue information.

## Pull Request Checklist

- [ ] All existing tests pass (`pytest tests/`)
- [ ] New tests added for new functionality
- [ ] Type checks pass (`mypy app/`)
- [ ] Linting passes (`ruff check .`)
- [ ] Formatting is correct (`black --check .`)
- [ ] Docstrings added for new public functions
