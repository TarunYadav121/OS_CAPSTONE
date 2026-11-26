#!/usr/bin/env bash
# ========================================================================
#   OPERATING SYSTEM RESOURCE MANAGEMENT SIMULATION SUITE
#   Master Orchestrator and Interactive Bash Launcher
# ========================================================================

set -e

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================================================${NC}"
echo -e "${GREEN}     OPERATING SYSTEM RESOURCE MANAGEMENT SIMULATION SUITE (v1.0)${NC}"
echo -e "${BLUE}     Integrated Architecture: Python Kernel with Bash Orchestration     ${NC}"
echo -e "${BLUE}========================================================================${NC}"

# Detect Python executable
if command -v python3 &>/dev/null; then
    PY_BIN="python3"
elif command -v python &>/dev/null; then
    PY_BIN="python"
else
    echo -e "${RED}[ERROR] Neither python3 nor python was found in PATH.${NC}"
    exit 1
fi

echo -e "${YELLOW}[*] Using Python binary: $($PY_BIN --version)${NC}"

show_menu() {
    echo ""
    echo -e "${BLUE}Please select an operating system simulation option:${NC}"
    echo "  1) Run Complete Integrated OS Simulation Suite (--all)"
    echo "  2) CPU Process Scheduling Module"
    echo "  3) Memory Management Module (Contiguous Allocation & Paging)"
    echo "  4) Deadlock Management Module (Banker's Algorithm & WFG Detection)"
    echo "  5) Disk Storage Scheduling Module"
    echo "  6) Run Benchmark Comparisons & Regenerate Analytical Charts"
    echo "  7) Run System Hardware & Resource Diagnostics (Bash)"
    echo "  8) Parse & Analyze Simulation Audit Logs (awk/grep/sed)"
    echo "  9) Run Automated Test Suite (pytest)"
    echo " 10) Exit"
    echo -e "${BLUE}========================================================================${NC}"
    read -p "Enter selection [1-10]: " choice
    case $choice in
        1)
            $PY_BIN main.py --all
            ;;
        2)
            $PY_BIN main.py --module scheduler
            ;;
        3)
            $PY_BIN main.py --module memory
            ;;
        4)
            $PY_BIN main.py --module deadlock
            ;;
        5)
            $PY_BIN main.py --module storage
            ;;
        6)
            $PY_BIN main.py --benchmark
            $PY_BIN main.py --generate-charts
            ;;
        7)
            bash bash_scripts/system_diagnostic.sh
            ;;
        8)
            bash bash_scripts/log_analyzer.sh
            ;;
        9)
            bash bash_scripts/run_all_tests.sh
            ;;
        10)
            echo -e "${GREEN}Exiting OS Simulator. Goodbye!${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}Invalid selection. Please choose an option 1-10.${NC}"
            ;;
    esac
}

# If arguments passed directly, pass to python or handle
if [ $# -gt 0 ]; then
    $PY_BIN main.py "$@"
else
    while true; do
        show_menu
        echo ""
        read -p "Press [Enter] to return to menu..."
    done
fi

