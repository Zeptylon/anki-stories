#!/usr/bin/env bash
set -euo pipefail

# Always run from repo root (even if invoked from elsewhere)
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

PYTHON_BIN="${PYTHON_BIN:-python3}"
VENV_DIR="${VENV_DIR:-.venv}"

if [ ! -d "$VENV_DIR" ]; then
  echo "Creating venv in $VENV_DIR ..."
  "$PYTHON_BIN" -m venv "$VENV_DIR"
fi

# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

echo "Upgrading pip ..."
python -m pip install -U pip

if [ -f requirements.txt ]; then
  echo "Installing runtime dependencies from requirements.txt ..."
  python -m pip install -r requirements.txt
fi

if [ -f requirements-dev.txt ]; then
  echo "Installing dev dependencies from requirements-dev.txt ..."
  python -m pip install -r requirements-dev.txt
fi

echo
echo "Setup complete."
echo "Next:"
echo "  source .venv/bin/activate"
echo "  (then run your script, e.g. python -m <your_module> ...)"
echo "  ./scripts/check.sh   # run quality gates"
