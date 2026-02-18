#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

if [ ! -d ".venv" ]; then
  echo "ERROR: .venv not found. Run ./scripts/dev_setup.sh first."
  exit 1
fi

# shellcheck disable=SC1091
source ".venv/bin/activate"

echo "Ruff format check (and format if needed) ..."
ruff format .

echo "Ruff lint ..."
ruff check .

echo "Pytest ..."
pytest -q
