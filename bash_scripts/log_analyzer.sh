#!/usr/bin/env bash
# ========================================================================
#   Simulation Audit Log Analyzer
#   Uses awk, grep, and sed to parse and summarize simulation.log
# ========================================================================

LOG_FILE="simulation.log"

if [ ! -f "$LOG_FILE" ]; then
    echo "[!] Log file '$LOG_FILE' does not exist yet. Run simulation first."
    exit 1
fi

echo "========================================================================"
echo "                 SIMULATION AUDIT LOG ANALYSIS REPORT                   "
echo "========================================================================"
echo "Target Audit File: $LOG_FILE"
echo "Total Log Entries: $(wc -l < "$LOG_FILE")"
echo ""

echo "[*] Severity Level Distribution:"
awk -F'[][]' '{print $4}' "$LOG_FILE" | tr -d ' ' | sort | uniq -c
echo ""

echo "[*] Component Activity Breakdown:"
awk -F'[][]' '{print $6}' "$LOG_FILE" | sort | uniq -c
echo ""

echo "[*] Top Logged Decisions / Events (Recent 10):"
tail -n 10 "$LOG_FILE"
echo ""

echo "[*] Any Warning / Error Events Detected:"
grep -E "WARNING|ERROR|UNSAFE|Deadlock" "$LOG_FILE" || echo "  [+] No system errors found in audit trace."
echo "========================================================================"

