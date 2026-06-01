#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Installing Python dependencies..."
pip install -r "$SCRIPT_DIR/requirements.txt"

echo "Starting Resume Tailor API on port 8001..."
python -m uvicorn api.main:app --host 0.0.0.0 --port 8001 --reload --app-dir "$SCRIPT_DIR/.."
