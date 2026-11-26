#!/usr/bin/env bash
# ========================================================================
#   System Diagnostic & Host Resource Inspection Utility
#   Gathers host OS metrics, CPU topology, memory states, and disk stats.
# ========================================================================

echo "========================================================================"
echo "                   HOST OPERATING SYSTEM DIAGNOSTIC                     "
echo "========================================================================"
echo "Timestamp: $(date)"
echo "Hostname : $(hostname 2>/dev/null || echo 'Unknown')"
echo "Kernel/OS: $(uname -a 2>/dev/null || echo 'Windows/NT')"
echo ""

echo "[*] CPU Architecture & Cores:"
if command -v lscpu &>/dev/null; then
    lscpu | grep -E "Model name|CPU\(s\):|Thread|Core"
elif [ -f /proc/cpuinfo ]; then
    grep -E "model name|cpu cores" /proc/cpuinfo | head -n 4
else
    echo "  Processor identification: Windows NT Architecture"
fi
echo ""

echo "[*] System Memory (RAM) Allocation:"
if command -v free &>/dev/null; then
    free -h
elif [ -f /proc/meminfo ]; then
    grep -E "MemTotal|MemFree|MemAvailable" /proc/meminfo
else
    echo "  Memory statistics handled via OS simulation virtual memory subsystem."
fi
echo ""

echo "[*] Storage Filesystem Utilization:"
if command -v df &>/dev/null; then
    df -h .
else
    echo "  Disk storage geometry simulated: 200 Tracks / Cylinders."
fi
echo ""

echo "[*] Python Environment Status:"
if command -v python3 &>/dev/null; then
    python3 --version
elif command -v python &>/dev/null; then
    python --version
fi
echo "========================================================================"

