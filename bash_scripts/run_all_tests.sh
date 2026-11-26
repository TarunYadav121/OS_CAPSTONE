#!/usr/bin/env bash
# ========================================================================
#   Automated Test Harness
#   Executes PyTest suite, checks exit codes, and reports coverage.
# ========================================================================

set -e

PY="python"
if command -v python3 &>/dev/null; then
    PY="python3"
fi

echo "========================================================================"
echo "           STARTING OPERATING SYSTEM MODULE TEST SUITE                  "
echo "========================================================================"

$PY -m pytest tests -v --tb=short

echo ""
echo "========================================================================"
echo "[+] All OS verification tests completed successfully!"
echo "========================================================================"

