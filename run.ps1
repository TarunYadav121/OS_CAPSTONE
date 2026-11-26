# ========================================================================
#   OPERATING SYSTEM RESOURCE MANAGEMENT SIMULATION SUITE
#   PowerShell Native Runner for Windows
# ========================================================================

Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "     OPERATING SYSTEM RESOURCE MANAGEMENT SIMULATION SUITE (v1.0)" -ForegroundColor Green
Write-Host "     Integrated Architecture: Python Kernel with PowerShell & Bash" -ForegroundColor Cyan
Write-Host "========================================================================" -ForegroundColor Cyan

function Show-Menu {
    Write-Host ""
    Write-Host "Please select an operating system simulation option:" -ForegroundColor Yellow
    Write-Host "  1) Run Complete Integrated OS Simulation Suite (--all)"
    Write-Host "  2) CPU Process Scheduling Module"
    Write-Host "  3) Memory Management Module (Contiguous Allocation & Paging)"
    Write-Host "  4) Deadlock Management Module (Banker's Algorithm & WFG Detection)"
    Write-Host "  5) Disk Storage Scheduling Module"
    Write-Host "  6) Run Benchmark Comparisons & Regenerate Analytical Charts"
    Write-Host "  7) Run Automated Test Suite (pytest)"
    Write-Host "  8) Export All Formatted Trace Files"
    Write-Host "  9) Exit"
    Write-Host "========================================================================" -ForegroundColor Cyan
    
    $choice = Read-Host "Enter selection [1-9]"
    switch ($choice) {
        "1" { python main.py --all }
        "2" { python main.py --module scheduler }
        "3" { python main.py --module memory }
        "4" { python main.py --module deadlock }
        "5" { python main.py --module storage }
        "6" { python main.py --benchmark; python main.py --generate-charts }
        "7" { pytest tests -v }
        "8" { python main.py --export-traces }
        "9" { Write-Host "Exiting OS Simulator. Goodbye!" -ForegroundColor Green; exit }
        default { Write-Host "Invalid selection. Please choose an option 1-9." -ForegroundColor Red }
    }
}

if ($args.Count -gt 0) {
    python main.py $args
} else {
    while ($true) {
        Show-Menu
        Write-Host ""
        Read-Host "Press [Enter] to return to menu..."
    }
}

