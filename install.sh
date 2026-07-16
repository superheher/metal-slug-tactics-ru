#!/usr/bin/env bash
# Installing the Metal Slug Tactics translator from source (Linux / macOS-Wine).
#
# This is a thin wrapper: it sets up a Python environment and calls the cross-platform
# tools/install.py. If you do not need Python — grab the ready-made installer from the
# Releases section (it requires nothing to be installed).
#
# Run again after every Steam update of the game — it restores the native bundles.
#
#   ./install.sh              install / update the translation
#   ./install.sh --dry-run    build and verify, but do not touch the game
#   ./install.sh --revert     restore the originals
#   MST_PATH=/path/to/MST ./install.sh    set the game path manually
set -e
cd "$(dirname "$0")"

VENV=".venv"
PY="$VENV/bin/python"

if [ ! -x "$PY" ]; then
    echo "→ creating the environment and installing dependencies (UnityPy, numpy, Pillow)"
    python3 -m venv "$VENV"
    "$VENV/bin/pip" install -q --disable-pip-version-check UnityPy numpy Pillow
fi

exec "$PY" tools/install.py "$@"
