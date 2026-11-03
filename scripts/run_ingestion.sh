#!/usr/bin/env bash
# ==============================================================================
# Sprints LEARMS - Standard Production Ingestion Wrapper
# Non-root execution for Sprints Systems Administrators
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_ROOT="$(dirname "$SCRIPT_DIR")"

echo "Executing Sprints LEARMS Data Ingestion Pipeline..."
python3 "$APP_ROOT/code/main.py" "$@"
