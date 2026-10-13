#!/usr/bin/env bash
# ==============================================================================
# AegisGov AI: Reusable Cloud Status & Telemetry Checker
# Inspects live health, Cloud Run resources, traffic counts, and free-tier metrics.
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Run using python3
python3 "${SCRIPT_DIR}/check_cloud_status.py" "$@"
