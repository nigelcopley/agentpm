# Repository Guidelines

## Project Structure & Module Organization
- `agentpm/` is the installable package: `core/` houses context, database, and workflow logic; `agents/` contains Claude integrations and SOP assets; shared helpers sit in `hooks/`, `utils/`, and `templates/`.
- Tests live in `tests/`; Flask integration helpers (e.g., `test_flask_routes.py`) sit at the repo root.
- `.aipm/` stores runtime data (SQLite DB, cached contexts, migration state). Treat it as generated state—never hand-edit or commit resets.

## CLI Workflow
1. `apm init "<Project>" /path` — bootstrap `.aipm/`, detect stack, seed metadata.
2. `apm work-item create` → `apm task create` — register scoped work while respecting enforced mixes.
3. `apm work-item list --status in_progress` + `apm task list --work-item-id <id>` — monitor execution and blockers.
4. `apm task context <task_id>` — deliver merged project/work-item/task context before handoff.
5. `apm session start` / `apm session end` — capture operational history; never skip the end hook.
6. `apm context refresh` — rebuild plugin facts after schema or dependency shifts.

## Development Commands
- `python -m pip install -e .[dev]` — install contributor tooling, then `apm status` to confirm wiring.
- `pytest` or `pytest -m unit` — run suites with coverage (HTML under `htmlcov/`).
- `black .`, `ruff check .`, `mypy agentpm` — mandatory formatting, linting, and typing gates.

## Coding Style & Documentation
- Format with Black (88 columns) and Ruff’s Black profile; choose domain-aligned names (`SessionActivityService`, `ContextFreshness`) and Google-style docstrings for public APIs.
- Extend structured logging with consistent fields (`event`, `work_item_id`, `duration_ms`); note workflow updates in `docs/developer-guide/`.

## Testing Guidelines
- Pytest discovers `test_*.py` / `*_test.py`; reuse fixtures in `tests/conftest.py` before adding new ones.
- Maintain ~90% coverage; regenerate HTML via `pytest --cov=agentpm --cov-report=html`; tag long scenarios (`integration`, `slow`, `plugin`) for selective runs.

## Commit & PR Expectations
- Use conventional commits (`feat:`, `fix:`, `chore:`) or concise imperatives under 72 characters.
- Reference the relevant work item or doc, summarize scope, and attach validation output (command snippets, screenshots) in every PR.
- Run lint, type-check, and the relevant pytest markers before opening a PR; call out any skipped checks with rationale.

## Must Do / Must Not
- **Must Do**: Respect quality gates, keep `.aipm/` intact, log session decisions through the CLI, update docs when agent behavior changes.
- **Must Not**: Delete `.aipm/data`, bypass `apm session end`, commit generated coverage/cache files, or introduce non-ASCII identifiers unless already present. Store secrets in local `.env` files only.
