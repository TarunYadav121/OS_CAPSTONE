"""Integrated Operating System Resource Management Simulation Suite.
Master CLI and Interactive Menu Interface.
Coordinates scheduling, memory, deadlock, and storage simulations with full logging and visualization.
"""

import sys
import os
import json
import argparse
from typing import Dict, Any, List

from src.logger import app_logger, setup_logger
from src.exceptions import OSSimulationError
from src.utils.validator import InputValidator
from src.utils.formatting import TextFormatter
from src.scheduler.algorithms import ProcessScheduler
from src.memory.contiguous import ContiguousMemoryManager
from src.memory.paging import PageReplacementSimulator
from src.deadlock.bankers import BankersAlgorithm
from src.deadlock.detection import DeadlockDetector
from src.storage.disk_scheduler import DiskScheduler
from src.analysis.benchmark import BenchmarkSuite
from src.analysis.visualizer import SystemVisualizer

BANNER = r"""
========================================================================
     OPERATING SYSTEM RESOURCE MANAGEMENT SIMULATION SUITE (v1.0)
     Integrated Architecture: Scheduling | Memory | Deadlock | Disk
========================================================================
"""


def load_json_file(file_path: str) -> Any:
    """Loads and parses JSON file safely."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Input file not found: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


# --- Module Handlers ---

def run_process_scheduling(custom_data: List[Dict[str, Any]] = None):
    print("\n--- CPU PROCESS SCHEDULING MODULE ---")
    data = custom_data or BenchmarkSuite.get_standard_processes()
    print(f"Loaded {len(data)} processes for simulation:")
    headers = ["PID", "Arrival Time", "Burst Time", "Priority"]
    rows = [[p["pid"], p["arrival_time"], p["burst_time"], p.get("priority", 0)] for p in data]
    print(TextFormatter.render_table(headers, rows))

    algorithms = [
        ("FCFS", lambda: ProcessScheduler.fcfs(data)),
        ("SJF (Non-Preemptive)", lambda: ProcessScheduler.sjf_non_preemptive(data)),
        ("SRTF (Preemptive)", lambda: ProcessScheduler.srtf_preemptive(data)),
        ("Priority (Non-Preemptive)", lambda: ProcessScheduler.priority_non_preemptive(data)),
        ("Round Robin (Q=2)", lambda: ProcessScheduler.round_robin(data, quantum=2)),
        ("Round Robin (Q=4)", lambda: ProcessScheduler.round_robin(data, quantum=4)),
    ]

    for name, func in algorithms:
        res = func()
        h, r = res.get_summary_table()
        print(TextFormatter.render_table(h, r, title=f"Results: {name}"))
        print(f"Metrics: Avg Waiting Time = {res.avg_waiting_time:.2f} ms | Avg Turnaround Time = {res.avg_turnaround_time:.2f} ms | Context Switches = {res.context_switches}")
        print(TextFormatter.render_gantt_chart(res.timeline))


def run_memory_management(custom_data: Dict[str, Any] = None):
    print("\n--- MEMORY MANAGEMENT MODULE ---")
    # Part 1: Contiguous Allocation
    print("\n[Part 1: Contiguous Allocation]")
    blocks = (custom_data or {}).get("blocks") or BenchmarkSuite.get_standard_memory_blocks()
    requests = (custom_data or {}).get("requests") or BenchmarkSuite.get_standard_memory_requests()
    mgr = ContiguousMemoryManager(blocks)

    for alg_name, func in [
        ("First Fit", mgr.allocate_first_fit),
        ("Best Fit", mgr.allocate_best_fit),
        ("Worst Fit", mgr.allocate_worst_fit),
    ]:
        res = func(requests)
        h = ["Process", "Requested (KB)", "Allocated Block", "Block Size", "Internal Frag (KB)", "Status"]
        r = [
            [
                a["pid"],
                a["size"],
                f"Block {a['block_id']}" if a["block_id"] else "-",
                f"{a['block_size']} KB" if a["block_size"] else "-",
                f"{a['internal_frag']} KB",
                a["status"],
            ]
            for a in res["allocations"]
        ]
        print(TextFormatter.render_table(h, r, title=f"Contiguous Allocation: {alg_name}"))
        print(f"Summary: Internal Frag = {res['total_internal_fragmentation']} KB | External Frag = {res['external_fragmentation']} KB | Remaining Free = {res['total_free_memory']} KB")

    # Part 2: Virtual Memory Page Replacement
    print("\n[Part 2: Virtual Memory Page Replacement]")
    pages = BenchmarkSuite.get_standard_page_reference_string()
    print(f"Reference String: {pages}")
    for fc in [3, 4]:
        print(f"\n>> Simulating with {fc} Physical Frames:")
        for name, func in [
            ("FIFO", PageReplacementSimulator.fifo),
            ("LRU", PageReplacementSimulator.lru),
            ("Optimal", PageReplacementSimulator.optimal),
        ]:
            res = func(pages, fc)
            print(f"{name} ({fc} frames): Page Faults = {res.page_faults} | Page Hits = {res.page_hits} | Hit Ratio = {res.hit_ratio:.2f}% | Fault Ratio = {res.fault_ratio:.2f}%")


def run_deadlock_management(custom_data: Dict[str, Any] = None):
    print("\n--- DEADLOCK MANAGEMENT MODULE ---")
    data = custom_data or BenchmarkSuite.get_standard_bankers_dataset()
    bankers = BankersAlgorithm(
        processes=data["processes"],
        available=data["available"],
        max_matrix=data["max_matrix"],
        allocation=data["allocation"],
        resource_names=data.get("resource_names"),
    )

    print("\n[Banker's Safety Algorithm State Evaluation]")
    need_mat = bankers.compute_need_matrix()
    res_names = bankers.resource_names

    headers = ["Process", "Allocation", "Max Claim", "Remaining Need"]
    rows = []
    for i, p in enumerate(bankers.processes):
        rows.append([
            p,
            str(bankers.allocation[i]),
            str(bankers.max_matrix[i]),
            str(need_mat[i]),
        ])
    print(TextFormatter.render_table(headers, rows, title=f"Banker's Matrices (Resources: {', '.join(res_names)})"))
    print(f"Current Available Vector: {bankers.available}")

    safety = bankers.is_safe_state()
    if safety.is_safe:
        print(f"\n[+] SYSTEM STATUS: SAFE STATE")
        print(f"    Safe Execution Sequence: {' -> '.join(safety.safe_sequence)}")
    else:
        print(f"\n[-] SYSTEM STATUS: UNSAFE STATE (Deadlock Risk)")

    # Simulate Request
    print("\n[Simulating Resource-Request Algorithm]")
    sample_req = [1, 0, 2]
    req_p = "P1"
    print(f"Process '{req_p}' requests resources: {sample_req}")
    req_res = bankers.request_resources(req_p, sample_req)
    print(f"Outcome: Granted = {req_res['granted']}")
    print(f"Details: {req_res['reason']}")

    # Wait-For Graph Deadlock Detection
    print("\n[Wait-For Graph (WFG) Deadlock Detection]")
    detector = DeadlockDetector(["P1", "P2", "P3", "P4"])
    detector.add_wait_dependency("P1", "P2")
    detector.add_wait_dependency("P2", "P3")
    detector.add_wait_dependency("P3", "P1")  # Cycle: P1 -> P2 -> P3 -> P1
    detector.add_wait_dependency("P4", "P2")
    has_dl, cycles = detector.detect_deadlock()
    print(f"Deadlock Detected: {has_dl}")
    if has_dl:
        for c in cycles:
            print(f"  Cycle Found: {' -> '.join(c)}")


def run_storage_scheduling(custom_data: Dict[str, Any] = None):
    print("\n--- DISK STORAGE SCHEDULING MODULE ---")
    data = custom_data or BenchmarkSuite.get_standard_disk_requests()
    reqs = data["requests"]
    head = data["initial_head"]
    tot = data["total_cylinders"]
    direction = data.get("direction", "RIGHT")

    print(f"Cylinder Request Queue: {reqs}")
    print(f"Initial Head Position: {head} | Total Cylinders: {tot} | Direction: {direction}")

    algorithms = [
        ("FCFS", lambda: DiskScheduler.fcfs(reqs, head, tot)),
        ("SSTF", lambda: DiskScheduler.sstf(reqs, head, tot)),
        ("SCAN", lambda: DiskScheduler.scan(reqs, head, tot, direction)),
        ("C-SCAN", lambda: DiskScheduler.c_scan(reqs, head, tot, direction)),
        ("LOOK", lambda: DiskScheduler.look(reqs, head, tot, direction)),
        ("C-LOOK", lambda: DiskScheduler.c_look(reqs, head, tot, direction)),
    ]

    h = ["Algorithm", "Head Movements (Cylinders)", "Avg Seek Distance", "Seek Sequence"]
    r = []
    for name, func in algorithms:
        res = func()
        seq_str = " -> ".join(str(c) for c in res.seek_sequence[:8]) + ("..." if len(res.seek_sequence) > 8 else "")
        r.append([res.algorithm_name, res.total_head_movements, f"{res.average_seek_distance:.2f}", seq_str])

    print(TextFormatter.render_table(h, r, title="Disk Scheduling Comparison"))


def export_all_output_traces():
    """Generates and writes structured output trace files to output_traces/."""
    os.makedirs("output_traces", exist_ok=True)
    print("\nExporting comprehensive output traces to output_traces/...")

    # 1. Process traces
    procs = BenchmarkSuite.get_standard_processes()
    with open("output_traces/process_schedule_trace.txt", "w", encoding="utf-8") as f:
        f.write("=== CPU PROCESS SCHEDULING SIMULATION TRACES ===\n")
        for alg_name, func in [
            ("FCFS", lambda: ProcessScheduler.fcfs(procs)),
            ("SJF_NP", lambda: ProcessScheduler.sjf_non_preemptive(procs)),
            ("SRTF_P", lambda: ProcessScheduler.srtf_preemptive(procs)),
            ("Priority_NP", lambda: ProcessScheduler.priority_non_preemptive(procs)),
            ("RoundRobin_Q2", lambda: ProcessScheduler.round_robin(procs, quantum=2)),
        ]:
            res = func()
            h, r = res.get_summary_table()
            f.write(TextFormatter.render_table(h, r, title=alg_name) + "\n")
            f.write(f"Metrics: Avg WT={res.avg_waiting_time:.2f}, Avg TAT={res.avg_turnaround_time:.2f}, Context Switches={res.context_switches}\n")
            f.write(TextFormatter.render_gantt_chart(res.timeline) + "\n\n")

    # 2. Memory traces
    with open("output_traces/memory_trace.txt", "w", encoding="utf-8") as f:
        f.write("=== MEMORY MANAGEMENT SIMULATION TRACES ===\n")
        blocks = BenchmarkSuite.get_standard_memory_blocks()
        reqs = BenchmarkSuite.get_standard_memory_requests()
        mgr = ContiguousMemoryManager(blocks)
        for name, fn in [("First Fit", mgr.allocate_first_fit), ("Best Fit", mgr.allocate_best_fit), ("Worst Fit", mgr.allocate_worst_fit)]:
            res = fn(reqs)
            f.write(f"\n--- {name} Contiguous Allocation ---\n")
            f.write(json.dumps(res, indent=2) + "\n")

        pages = BenchmarkSuite.get_standard_page_reference_string()
        f.write("\n--- Virtual Memory Page Replacement Traces (Frames=3 & 4) ---\n")
        for fc in [3, 4]:
            for p_name, p_fn in [("FIFO", PageReplacementSimulator.fifo), ("LRU", PageReplacementSimulator.lru), ("Optimal", PageReplacementSimulator.optimal)]:
                res = p_fn(pages, fc)
                h, r = res.get_summary_table()
                f.write(TextFormatter.render_table(h, r, title=f"{p_name} ({fc} Frames)") + "\n")
                f.write(f"Faults: {res.page_faults}, Hits: {res.page_hits}, Hit Ratio: {res.hit_ratio:.2f}%\n\n")

    # 3. Deadlock traces
    with open("output_traces/deadlock_trace.txt", "w", encoding="utf-8") as f:
        f.write("=== DEADLOCK MANAGEMENT SIMULATION TRACES ===\n")
        d_data = BenchmarkSuite.get_standard_bankers_dataset()
        b = BankersAlgorithm(d_data["processes"], d_data["available"], d_data["max_matrix"], d_data["allocation"], d_data["resource_names"])
        safety = b.is_safe_state()
        f.write(f"Initial State Safe: {safety.is_safe}\n")
        f.write(f"Safe Sequence: {' -> '.join(safety.safe_sequence)}\n")
        f.write("\nSafety Step Traces:\n")
        f.write(json.dumps(safety.step_traces, indent=2) + "\n")

        # Test request
        req = b.request_resources("P1", [1, 0, 2])
        f.write(f"\nResource Request for P1 [1, 0, 2]: Granted={req['granted']}, Reason={req['reason']}\n")

    # 4. Storage traces
    with open("output_traces/disk_trace.txt", "w", encoding="utf-8") as f:
        f.write("=== DISK STORAGE SCHEDULING SIMULATION TRACES ===\n")
        dk = BenchmarkSuite.get_standard_disk_requests()
        for name, fn in [
            ("FCFS", lambda: DiskScheduler.fcfs(dk["requests"], dk["initial_head"], dk["total_cylinders"])),
            ("SSTF", lambda: DiskScheduler.sstf(dk["requests"], dk["initial_head"], dk["total_cylinders"])),
            ("SCAN", lambda: DiskScheduler.scan(dk["requests"], dk["initial_head"], dk["total_cylinders"], "RIGHT")),
            ("C-SCAN", lambda: DiskScheduler.c_scan(dk["requests"], dk["initial_head"], dk["total_cylinders"], "RIGHT")),
            ("LOOK", lambda: DiskScheduler.look(dk["requests"], dk["initial_head"], dk["total_cylinders"], "RIGHT")),
            ("C-LOOK", lambda: DiskScheduler.c_look(dk["requests"], dk["initial_head"], dk["total_cylinders"], "RIGHT")),
        ]:
            res = fn()
            h, r = res.get_summary_table()
            f.write(TextFormatter.render_table(h, r, title=name) + "\n")
            f.write(f"Total Movement: {res.total_head_movements} | Avg Seek Distance: {res.average_seek_distance:.2f}\n\n")

    print("[+] All output trace logs successfully generated in 'output_traces/'.")


def run_benchmark_and_charts():
    print("\n--- RUNNING COMPREHENSIVE BENCHMARK SUITE ---")
    # 1. Process
    p_res = BenchmarkSuite.benchmark_process_scheduling()
    h = ["Algorithm", "Avg WT (ms)", "Avg TAT (ms)", "Avg RT (ms)", "Context Switches", "CPU Util (%)"]
    r = [[d["Algorithm"], d["Avg WT (ms)"], d["Avg TAT (ms)"], d["Avg RT (ms)"], d["Context Switches"], d["CPU Utilization (%)"]] for d in p_res]
    print(TextFormatter.render_table(h, r, title="Process Scheduling Comparative Benchmark"))

    # 2. Memory
    m_res = BenchmarkSuite.benchmark_memory_allocation()
    h = ["Algorithm", "Allocated Count", "Internal Frag (KB)", "External Frag (KB)", "Remaining Free (KB)"]
    r = [[d["Algorithm"], d["Allocated Count"], d["Internal Frag (KB)"], d["External Frag (KB)"], d["Remaining Free (KB)"]] for d in m_res]
    print(TextFormatter.render_table(h, r, title="Contiguous Memory Allocation Comparative Benchmark"))

    # 3. Paging
    pg_res = BenchmarkSuite.benchmark_page_replacement()
    h = ["Algorithm", "Frames", "Page Faults", "Page Hits", "Hit Ratio (%)", "Fault Ratio (%)"]
    r = [[d["Algorithm"], d["Frames"], d["Page Faults"], d["Page Hits"], d["Hit Ratio (%)"], d["Fault Ratio (%)"]] for d in pg_res]
    print(TextFormatter.render_table(h, r, title="Page Replacement Comparative Benchmark"))

    # 4. Storage
    s_res = BenchmarkSuite.benchmark_disk_scheduling()
    h = ["Algorithm", "Total Head Movement", "Avg Seek Distance", "Direction"]
    r = [[d["Algorithm"], d["Total Movement"], d["Avg Seek Distance"], d["Direction"]] for d in s_res]
    print(TextFormatter.render_table(h, r, title="Disk Storage Comparative Benchmark"))

    print("\nGenerating graphical analytical plots...")
    charts = SystemVisualizer.generate_all_charts()
    for name, path in charts.items():
        print(f"  [+] Saved {name}: {path}")


def interactive_menu():
    """Interactive text menu for user exploration."""
    while True:
        print(BANNER)
        print("Please choose an option:")
        print("  1. Process Scheduling Module (FCFS, SJF, SRTF, Priority, Round Robin)")
        print("  2. Memory Management Module (Contiguous Fit & Page Replacement)")
        print("  3. Deadlock Management Module (Banker's Avoidance & WFG Detection)")
        print("  4. Disk Storage Scheduling Module (FCFS, SSTF, SCAN, C-SCAN, LOOK, C-LOOK)")
        print("  5. Run Full Benchmark Comparison & Generate Graphical Charts")
        print("  6. Export Structured Output Trace Files")
        print("  7. Run Automated System Tests")
        print("  8. Exit")
        print("=" * 72)

        try:
            choice = input("Enter choice (1-8): ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting simulator.")
            break

        if choice == "1":
            run_process_scheduling()
        elif choice == "2":
            run_memory_management()
        elif choice == "3":
            run_deadlock_management()
        elif choice == "4":
            run_storage_scheduling()
        elif choice == "5":
            run_benchmark_and_charts()
        elif choice == "6":
            export_all_output_traces()
        elif choice == "7":
            import pytest
            pytest.main(["-v", "tests"])
        elif choice == "8" or choice.lower() in ("exit", "quit", "q"):
            print("Thank you for using the OS Resource Management Simulation Suite.")
            break
        else:
            print("Invalid selection. Please choose an option from 1 to 8.")

        input("\nPress [Enter] to return to main menu...")


def main():
    parser = argparse.ArgumentParser(description="Operating System Resource Management Simulation Suite")
    parser.add_argument("--all", action="store_true", help="Run complete benchmark suite and export all traces and charts")
    parser.add_argument("--module", choices=["scheduler", "memory", "deadlock", "storage"], help="Run specific simulation module")
    parser.add_argument("--benchmark", action="store_true", help="Run comparative benchmark analysis")
    parser.add_argument("--generate-charts", action="store_true", help="Generate all analytical matplotlib charts")
    parser.add_argument("--export-traces", action="store_true", help="Export trace files to output_traces/")
    parser.add_argument("--input", type=str, help="Path to custom JSON configuration input file")

    args = parser.parse_args()

    custom_data = None
    if args.input:
        custom_data = load_json_file(args.input)

    if args.all:
        print(BANNER)
        print("[+] Executing Complete Integrated OS Simulation Suite...")
        run_process_scheduling(custom_data if args.module == "scheduler" else None)
        run_memory_management(custom_data if args.module == "memory" else None)
        run_deadlock_management(custom_data if args.module == "deadlock" else None)
        run_storage_scheduling(custom_data if args.module == "storage" else None)
        run_benchmark_and_charts()
        export_all_output_traces()
        print("\n[+] Full Suite Execution Completed Successfully.")
        return

    if args.module == "scheduler":
        run_process_scheduling(custom_data)
        return
    elif args.module == "memory":
        run_memory_management(custom_data)
        return
    elif args.module == "deadlock":
        run_deadlock_management(custom_data)
        return
    elif args.module == "storage":
        run_storage_scheduling(custom_data)
        return

    if args.benchmark:
        run_benchmark_and_charts()
        return

    if args.generate_charts:
        SystemVisualizer.generate_all_charts()
        print("[+] Charts generated in charts/.")
        return

    if args.export_traces:
        export_all_output_traces()
        return

    # If no flags passed, launch interactive menu
    interactive_menu()


if __name__ == "__main__":
    try:
        main()
    except OSSimulationError as e:
        app_logger.error(f"Simulation Error: {e}")
        print(f"\n[FATAL OS ERROR] {e}")
        sys.exit(1)
    except Exception as e:
        app_logger.exception(f"Unexpected kernel fault: {e}")
        print(f"\n[UNEXPECTED KERNEL FAULT] {e}")
        sys.exit(1)

