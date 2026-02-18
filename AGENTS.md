# AGENTS.md

## Project overview
This project fetches recently reviewed Anki cards and generates short stories using the reviewed vocabulary.
It talks to Anki via AnkiConnect (HTTP on localhost).

Initial milestone:
- User chooses N cards and a lookback window (e.g., 3/7/30 days)
- Fetch reviewed cards via AnkiConnect
- Save the selected words/cards to a local file (JSON or CSV) deterministically

## Setup
- Create venv and install deps:
  - `./scripts/dev_setup.sh`
- Activate venv:
  - `source .venv/bin/activate`

## Quality gates (must pass before PR is ready)
- `./scripts/check.sh`

## Runtime assumptions
- AnkiConnect is installed and Anki is running.
- Default AnkiConnect endpoint: `http://127.0.0.1:8765`
- All HTTP requests must include a timeout and handle connection errors clearly.

## Coding conventions
- Prefer small, testable functions.
- Use type hints for public functions.
- No secrets or API keys committed.
- Prefer structured logging over print statements.
- When adding dependencies, update `requirements.txt` (runtime) or `requirements-dev.txt` (dev).

## Suggested structure (when adding new code)
- Put core logic in a module (e.g., `anki_stories/`).
- Keep a small CLI entrypoint (e.g., `python -m anki_stories ...`).
- Add tests under `tests/` (pytest).

## Behavior requirements
- If AnkiConnect is unreachable, exit with a clear error message and non-zero status.
- If the deck name is invalid, fail gracefully with a helpful message.
- Output files should include timestamp + parameters used (N, window) for traceability.
