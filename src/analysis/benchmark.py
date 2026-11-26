"""Comprehensive Benchmarking Engine for Operating System Resource Management.
Runs standardized workloads across all 4 OS modules, calculates comparative metrics,
and prepares structured analytical datasets for reporting.
"""

from typing import List, Dict, Any
from src.scheduler.algorithms import ProcessScheduler
from src.memory.contiguous import ContiguousMemoryManager
from src.memory.paging import PageReplacementSimulator
from src.deadlock.bankers import BankersAlgorithm
from src.storage.disk_scheduler import DiskScheduler
from src.logger import app_logger


class BenchmarkSuite:
    """Executes comparative simulations on standardized operating system workloads."""

    @staticmethod
    def get_standard_processes() -> List[Dict[str, Any]]:
        """Standard process scheduling benchmark dataset."""
        return [
            {"pid": "P1", "arrival_time": 0, "burst_time": 8, "priority": 3},
            {"pid": "P2", "arrival_time": 1, "burst_time": 4, "priority": 1},
            {"pid": "P3", "arrival_time": 2, "burst_time": 9, "priority": 4},
            {"pid": "P4", "arrival_time": 3, "burst_time": 5, "priority": 2},
            {"pid": "P5", "arrival_time": 4, "burst_time": 2, "priority": 5},
        ]

    @staticmethod
    def get_standard_memory_blocks() -> List[int]:
        """Standard contiguous memory blocks (in KB)."""
        return [100, 500, 200, 300, 600]

    @staticmethod
    def get_standard_memory_requests() -> List[Dict[str, Any]]:
        """Standard contiguous memory process requests (in KB)."""
        return [
            {"pid": "P1", "size": 212},
            {"pid": "P2", "size": 417},
            {"pid": "P3", "size": 112},
            {"pid": "P4", "size": 426},
        ]

    @staticmethod
    def get_standard_page_reference_string() -> List[int]:
        """Standard page reference string containing Belady's Anomaly test sequence."""
        return [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]

    @staticmethod
    def get_standard_bankers_dataset() -> Dict[str, Any]:
        """Standard Banker's Algorithm allocation state."""
        return {
            "processes": ["P0", "P1", "P2", "P3", "P4"],
            "available": [3, 3, 2],
            "max_matrix": [
                [7, 5, 3],
                [3, 2, 2],
                [9, 0, 2],
                [2, 2, 2],
                [4, 3, 3],
            ],
            "allocation": [
                [0, 1, 0],
                [2, 0, 0],
                [3, 0, 2],
                [2, 1, 1],
                [0, 0, 2],
            ],
            "resource_names": ["A", "B", "C"],
        }

    @staticmethod
    def get_standard_disk_requests() -> Dict[str, Any]:
        """Standard disk cylinder track benchmark queue."""
        return {
            "requests": [98, 183, 37, 122, 14, 124, 65, 67],
            "initial_head": 53,
            "total_cylinders": 200,
            "direction": "RIGHT",
        }

    # --- Benchmark Run Methods ---

    @classmethod
    def benchmark_process_scheduling(cls) -> List[Dict[str, Any]]:
        """Compares FCFS, SJF, SRTF, Priority, and Round Robin on common process dataset."""
        procs = cls.get_standard_processes()
        results = []

        # 1. FCFS
        res_fcfs = ProcessScheduler.fcfs(procs)
        # 2. SJF (Non-preemptive)
        res_sjf = ProcessScheduler.sjf_non_preemptive(procs)
        # 3. SRTF (Preemptive)
        res_srtf = ProcessScheduler.srtf_preemptive(procs)
        # 4. Priority (Non-preemptive)
        res_prio = ProcessScheduler.priority_non_preemptive(procs)
        # 5. Round Robin (Q=2)
        res_rr2 = ProcessScheduler.round_robin(procs, quantum=2)
        # 6. Round Robin (Q=4)
        res_rr4 = ProcessScheduler.round_robin(procs, quantum=4)

        for r in [res_fcfs, res_sjf, res_srtf, res_prio, res_rr2, res_rr4]:
            results.append({
                "Algorithm": r.algorithm_name,
                "Avg WT (ms)": round(r.avg_waiting_time, 2),
                "Avg TAT (ms)": round(r.avg_turnaround_time, 2),
                "Avg RT (ms)": round(r.avg_response_time, 2),
                "Context Switches": r.context_switches,
                "CPU Utilization (%)": round(r.cpu_utilization, 1),
                "Total Time": r.total_time,
                "_raw_result": r,
            })

        app_logger.info("Process scheduling benchmark completed.")
        return results

    @classmethod
    def benchmark_memory_allocation(cls) -> List[Dict[str, Any]]:
        """Compares First Fit, Best Fit, and Worst Fit contiguous placement."""
        blocks = cls.get_standard_memory_blocks()
        requests = cls.get_standard_memory_requests()
        mgr = ContiguousMemoryManager(blocks)

        ff = mgr.allocate_first_fit(requests)
        bf = mgr.allocate_best_fit(requests)
        wf = mgr.allocate_worst_fit(requests)

        results = []
        for res in [ff, bf, wf]:
            num_allocated = len(res["allocations"]) - len(res["unallocated_processes"])
            results.append({
                "Algorithm": res["algorithm"],
                "Allocated Count": f"{num_allocated}/{len(requests)}",
                "Internal Frag (KB)": res["total_internal_fragmentation"],
                "External Frag (KB)": res["external_fragmentation"],
                "Remaining Free (KB)": res["total_free_memory"],
                "Unallocated PIDs": ", ".join(res["unallocated_processes"]) if res["unallocated_processes"] else "None",
                "_raw_result": res,
            })

        app_logger.info("Contiguous memory allocation benchmark completed.")
        return results

    @classmethod
    def benchmark_page_replacement(cls) -> List[Dict[str, Any]]:
        """Compares FIFO, LRU, and Optimal across frame sizes (3 and 4) on common reference string."""
        pages = cls.get_standard_page_reference_string()
        results = []

        for fc in [3, 4]:
            fifo_res = PageReplacementSimulator.fifo(pages, fc)
            lru_res = PageReplacementSimulator.lru(pages, fc)
            opt_res = PageReplacementSimulator.optimal(pages, fc)

            for r in [fifo_res, lru_res, opt_res]:
                results.append({
                    "Algorithm": r.algorithm_name,
                    "Frames": fc,
                    "Total References": r.total_references,
                    "Page Faults": r.page_faults,
                    "Page Hits": r.page_hits,
                    "Hit Ratio (%)": round(r.hit_ratio, 2),
                    "Fault Ratio (%)": round(r.fault_ratio, 2),
                    "_raw_result": r,
                })

        app_logger.info("Page replacement benchmark completed.")
        return results

    @classmethod
    def benchmark_disk_scheduling(cls) -> List[Dict[str, Any]]:
        """Compares FCFS, SSTF, SCAN, C-SCAN, LOOK, C-LOOK on common track queue."""
        data = cls.get_standard_disk_requests()
        reqs = data["requests"]
        head = data["initial_head"]
        tot = data["total_cylinders"]
        direction = data["direction"]

        sched_fcfs = DiskScheduler.fcfs(reqs, head, tot)
        sched_sstf = DiskScheduler.sstf(reqs, head, tot)
        sched_scan = DiskScheduler.scan(reqs, head, tot, direction)
        sched_cscan = DiskScheduler.c_scan(reqs, head, tot, direction)
        sched_look = DiskScheduler.look(reqs, head, tot, direction)
        sched_clook = DiskScheduler.c_look(reqs, head, tot, direction)

        results = []
        for r in [sched_fcfs, sched_sstf, sched_scan, sched_cscan, sched_look, sched_clook]:
            results.append({
                "Algorithm": r.algorithm_name,
                "Initial Head": r.initial_head,
                "Total Movement": r.total_head_movements,
                "Avg Seek Distance": round(r.average_seek_distance, 2),
                "Direction": r.direction,
                "_raw_result": r,
            })

        app_logger.info("Disk scheduling benchmark completed.")
        return results

