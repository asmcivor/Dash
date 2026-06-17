# AGENTS.md

Purpose
-------
This file gives concise, actionable instructions for AI coding agents working in this repository.

Quick commands
--------------
- Create & activate venv (Windows PowerShell):

  python -m venv .venv
  .venv\Scripts\Activate.ps1

- Install dependencies:

  pip install -r requirements.txt

- Run the app (development):

  python main.py
  # or: uvicorn main:app --reload --host 0.0.0.0 --port 8000

- Run tests:

  pytest

Project layout (what matters to agents)
-------------------------------------
- `main.py` — FastAPI entrypoint and startup/shutdown hooks.
- `routers/` — HTTP routes; `pages.py` for full-page routes, `partials.py` for HTMX fragments.
- `services/` — Business logic and external API calls (address, weather, time, data).
- `templates/` & `static/` — Jinja2 templates and static assets (CSS, images, icons).
- `TestCases/` — Pytest tests; look here when adding or modifying behavior.
- `requirements.txt` and `.venv/` — dependency manifest and local virtualenv.
- `config.py` — Pydantic settings (reads environment variables / .env).

Conventions & expectations
--------------------------
- Framework: FastAPI + Jinja2 templates; HTMX is used for partial updates.
- Keep business logic in `services/`; routers should remain thin and return `HTMLResponse` or templates.
- Tests follow `pytest` and live in `TestCases/`; run `pytest` locally before proposing changes.
- Use `logging.getLogger(__name__)` in modules; avoid incorrect imports like `from venv import logger`.

Agent workflow guidance
----------------------
- Discoverability: Link to existing docs rather than duplicating them.
- Minimal edits: Make the smallest change that fixes the root cause; prefer refactors that preserve behavior.
- Tests: Add or update tests in `TestCases/` for any behavior changes. Run `pytest` to confirm.
- Environment: Do not commit local `.venv/` changes; if adding environment docs, update this file.

Notable pitfalls (quick list)
----------------------------
- Logging imports in some service modules need replacing with `import logging` + `logging.getLogger(__name__)`.
- Geocoding and weather APIs have edge cases (null coords, no results); add defensive checks and tests.

If you want further customization (agent hooks, rules, or automated checks), request `/create-(agent|hook|instruction|prompt|skill) ...` and describe the intended automation.
