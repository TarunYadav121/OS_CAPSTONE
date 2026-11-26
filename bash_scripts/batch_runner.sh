#!/usr/bin/env bash
# ========================================================================
#   Batch Simulation Runner
#   Executes simulations across all sample input profiles and logs timings.
# ========================================================================

set -e

PY="python"
if command -v python3 &>/dev/null; then
    PY="python3"
fi

echo "========================================================================"
echo "          STARTING BATCH OPERATING SYSTEM SIMULATION RUNNER             "
echo "========================================================================"

mkdir -p output_traces
mkdir -p charts

START_TIME=$(date +%s)

echo "[1/4] Running CPU Scheduler profile..."
$PY main.py --module scheduler --input sample_inputs/processes_sample.json > output_traces/batch_scheduler.log

echo "[2/4] Running Contiguous & Paging Memory profile..."
$PY main.py --module memory --input sample_inputs/memory_sample.json > output_traces/batch_memory.log

echo "[3/4] Running Deadlock & Banker's profile..."
$PY main.py --module deadlock --input sample_inputs/deadlock_sample.json > output_traces/batch_deadlock.log

echo "[4/4] Running Disk Storage arm profile..."
$PY main.py --module storage --input sample_inputs/disk_requests.json > output_traces/batch_storage.log

echo "[*] Generating Benchmark Comparisons and Analytical Visualizations..."
$PY main.py --benchmark
$PY main.py --generate-charts
$PY main.py --export-traces

END_TIME=$(date +%s)
ELAPSED=$((END_TIME - START_TIME))

echo "========================================================================"
echo "[+] Batch simulation run finished in $ELAPSED second(s)."
echo "[+] Check 'output_traces/' and 'charts/' for generated artifacts."
echo "========================================================================"

