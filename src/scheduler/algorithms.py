"""Implementation of Core CPU Scheduling Algorithms.
Supports FCFS, SJF (Non-preemptive), SRTF (Preemptive), Priority (NP & P), and Round Robin.
"""

from typing import List, Dict, Any, Optional
import copy
from src.scheduler.process import Process, ScheduleResult
from src.utils.validator import InputValidator
from src.logger import app_logger


class ProcessScheduler:
    """Orchestrates CPU process scheduling simulations."""

    @staticmethod
    def _create_processes(proc_dicts: List[Dict[str, Any]]) -> List[Process]:
        validated = InputValidator.validate_processes(proc_dicts)
        return [
            Process(
                pid=p["pid"],
                arrival_time=p["arrival_time"],
                burst_time=p["burst_time"],
                priority=p.get("priority", 0)
            )
            for p in validated
        ]

    @staticmethod
    def _compute_metrics(
        algorithm_name: str,
        processes: List[Process],
        timeline: List[tuple[str, int, int]],
        context_switches: int,
        total_time: int,
        idle_time: int,
    ) -> ScheduleResult:
        n = len(processes)
        for p in processes:
            p.turnaround_time = p.completion_time - p.arrival_time
            p.waiting_time = p.turnaround_time - p.burst_time

        avg_wt = sum(p.waiting_time for p in processes) / n if n > 0 else 0.0
        avg_tat = sum(p.turnaround_time for p in processes) / n if n > 0 else 0.0
        avg_rt = sum(p.response_time for p in processes) / n if n > 0 else 0.0
        cpu_util = ((total_time - idle_time) / total_time * 100.0) if total_time > 0 else 0.0

        app_logger.info(
            f"Scheduling completed [{algorithm_name}]: {n} processes, Avg WT={avg_wt:.2f}, Avg TAT={avg_tat:.2f}"
        )

        return ScheduleResult(
            algorithm_name=algorithm_name,
            processes=processes,
            timeline=timeline,
            context_switches=context_switches,
            total_time=total_time,
            idle_time=idle_time,
            cpu_utilization=cpu_util,
            avg_waiting_time=avg_wt,
            avg_turnaround_time=avg_tat,
            avg_response_time=avg_rt,
        )

    # 1. First-Come, First-Served (FCFS)
    @classmethod
    def fcfs(cls, raw_processes: List[Dict[str, Any]]) -> ScheduleResult:
        processes = cls._create_processes(raw_processes)
        processes.sort(key=lambda p: (p.arrival_time, p.pid))

        timeline: List[tuple[str, int, int]] = []
        current_time = 0
        idle_time = 0
        context_switches = 0
        last_pid = None

        for p in processes:
            if current_time < p.arrival_time:
                idle_duration = p.arrival_time - current_time
                timeline.append(("IDLE", current_time, p.arrival_time))
                idle_time += idle_duration
                current_time = p.arrival_time

            if last_pid is not None and last_pid != p.pid and last_pid != "IDLE":
                context_switches += 1

            p.start_time = current_time
            p.response_time = current_time - p.arrival_time
            p.completion_time = current_time + p.burst_time
            timeline.append((p.pid, current_time, p.completion_time))
            current_time = p.completion_time
            last_pid = p.pid

        return cls._compute_metrics("FCFS", processes, timeline, context_switches, current_time, idle_time)

    # 2. Shortest Job First (SJF - Non-preemptive)
    @classmethod
    def sjf_non_preemptive(cls, raw_processes: List[Dict[str, Any]]) -> ScheduleResult:
        processes = cls._create_processes(raw_processes)
        ready_pool = sorted(processes, key=lambda p: (p.arrival_time, p.burst_time, p.pid))

        completed = []
        timeline: List[tuple[str, int, int]] = []
        current_time = 0
        idle_time = 0
        context_switches = 0
        last_pid = None

        remaining = ready_pool.copy()
        while remaining:
            available = [p for p in remaining if p.arrival_time <= current_time]
            if not available:
                next_arr = min(p.arrival_time for p in remaining)
                timeline.append(("IDLE", current_time, next_arr))
                idle_time += next_arr - current_time
                current_time = next_arr
                available = [p for p in remaining if p.arrival_time <= current_time]

            # Pick shortest burst time; tie breaker arrival_time, then pid
            chosen = min(available, key=lambda p: (p.burst_time, p.arrival_time, p.pid))
            remaining.remove(chosen)

            if last_pid is not None and last_pid != chosen.pid and last_pid != "IDLE":
                context_switches += 1

            chosen.start_time = current_time
            chosen.response_time = current_time - chosen.arrival_time
            chosen.completion_time = current_time + chosen.burst_time
            timeline.append((chosen.pid, current_time, chosen.completion_time))
            current_time = chosen.completion_time
            last_pid = chosen.pid
            completed.append(chosen)

        return cls._compute_metrics("SJF (Non-Preemptive)", completed, timeline, context_switches, current_time, idle_time)

    # 3. Shortest Remaining Time First (SRTF - Preemptive SJF)
    @classmethod
    def srtf_preemptive(cls, raw_processes: List[Dict[str, Any]]) -> ScheduleResult:
        processes = cls._create_processes(raw_processes)
        n = len(processes)
        completed = []
        timeline_raw: List[tuple[str, int, int]] = []
        current_time = 0
        idle_time = 0
        context_switches = 0
        last_pid = None

        proc_map = {p.pid: p for p in processes}
        active = [p for p in processes]

        while len(completed) < n:
            available = [p for p in active if p.arrival_time <= current_time and p.remaining_time > 0]
            if not available:
                next_arr = min(p.arrival_time for p in active if p.remaining_time > 0)
                timeline_raw.append(("IDLE", current_time, next_arr))
                idle_time += next_arr - current_time
                current_time = next_arr
                available = [p for p in active if p.arrival_time <= current_time and p.remaining_time > 0]

            chosen = min(available, key=lambda p: (p.remaining_time, p.arrival_time, p.pid))

            if chosen.response_time == -1:
                chosen.response_time = current_time - chosen.arrival_time

            if last_pid is not None and last_pid != chosen.pid and last_pid != "IDLE":
                context_switches += 1

            timeline_raw.append((chosen.pid, current_time, current_time + 1))
            chosen.remaining_time -= 1
            current_time += 1
            last_pid = chosen.pid

            if chosen.remaining_time == 0:
                chosen.completion_time = current_time
                completed.append(chosen)
                active.remove(chosen)

        # Merge contiguous timeline segments
        merged_timeline: List[tuple[str, int, int]] = []
        for pid, st, en in timeline_raw:
            if merged_timeline and merged_timeline[-1][0] == pid and merged_timeline[-1][2] == st:
                merged_timeline[-1] = (pid, merged_timeline[-1][1], en)
            else:
                merged_timeline.append((pid, st, en))

        return cls._compute_metrics("SRTF (Preemptive)", processes, merged_timeline, context_switches, current_time, idle_time)

    # 4. Priority Scheduling (Non-Preemptive) - lower number = higher priority
    @classmethod
    def priority_non_preemptive(cls, raw_processes: List[Dict[str, Any]]) -> ScheduleResult:
        processes = cls._create_processes(raw_processes)
        completed = []
        timeline: List[tuple[str, int, int]] = []
        current_time = 0
        idle_time = 0
        context_switches = 0
        last_pid = None

        remaining = processes.copy()
        while remaining:
            available = [p for p in remaining if p.arrival_time <= current_time]
            if not available:
                next_arr = min(p.arrival_time for p in remaining)
                timeline.append(("IDLE", current_time, next_arr))
                idle_time += next_arr - current_time
                current_time = next_arr
                available = [p for p in remaining if p.arrival_time <= current_time]

            # Pick lowest priority number (highest priority)
            chosen = min(available, key=lambda p: (p.priority, p.arrival_time, p.pid))
            remaining.remove(chosen)

            if last_pid is not None and last_pid != chosen.pid and last_pid != "IDLE":
                context_switches += 1

            chosen.start_time = current_time
            chosen.response_time = current_time - chosen.arrival_time
            chosen.completion_time = current_time + chosen.burst_time
            timeline.append((chosen.pid, current_time, chosen.completion_time))
            current_time = chosen.completion_time
            last_pid = chosen.pid
            completed.append(chosen)

        return cls._compute_metrics("Priority (Non-Preemptive)", completed, timeline, context_switches, current_time, idle_time)

    # 5. Round Robin (RR)
    @classmethod
    def round_robin(cls, raw_processes: List[Dict[str, Any]], quantum: int = 2) -> ScheduleResult:
        q = InputValidator.validate_quantum(quantum)
        processes = cls._create_processes(raw_processes)
        processes.sort(key=lambda p: (p.arrival_time, p.pid))

        ready_queue: List[Process] = []
        timeline: List[tuple[str, int, int]] = []
        current_time = 0
        idle_time = 0
        context_switches = 0
        last_pid = None

        unvisited = processes.copy()
        completed = []
        n = len(processes)

        while len(completed) < n:
            # Enqueue all processes that have arrived up to current_time
            arrived = [p for p in unvisited if p.arrival_time <= current_time]
            for p in arrived:
                ready_queue.append(p)
                unvisited.remove(p)

            if not ready_queue:
                if unvisited:
                    next_arr = min(p.arrival_time for p in unvisited)
                    timeline.append(("IDLE", current_time, next_arr))
                    idle_time += next_arr - current_time
                    current_time = next_arr
                    arrived = [p for p in unvisited if p.arrival_time <= current_time]
                    for p in arrived:
                        ready_queue.append(p)
                        unvisited.remove(p)
                else:
                    break

            curr_proc = ready_queue.pop(0)

            if curr_proc.response_time == -1:
                curr_proc.response_time = current_time - curr_proc.arrival_time

            if last_pid is not None and last_pid != curr_proc.pid and last_pid != "IDLE":
                context_switches += 1

            run_time = min(q, curr_proc.remaining_time)
            timeline.append((curr_proc.pid, current_time, current_time + run_time))
            current_time += run_time
            curr_proc.remaining_time -= run_time
            last_pid = curr_proc.pid

            # Enqueue newly arrived processes during this quantum execution
            arrived = [p for p in unvisited if p.arrival_time <= current_time]
            for p in arrived:
                ready_queue.append(p)
                unvisited.remove(p)

            if curr_proc.remaining_time > 0:
                ready_queue.append(curr_proc)
            else:
                curr_proc.completion_time = current_time
                completed.append(curr_proc)

        # Merge contiguous timeline segments
        merged_timeline: List[tuple[str, int, int]] = []
        for pid, st, en in timeline:
            if merged_timeline and merged_timeline[-1][0] == pid and merged_timeline[-1][2] == st:
                merged_timeline[-1] = (pid, merged_timeline[-1][1], en)
            else:
                merged_timeline.append((pid, st, en))

        return cls._compute_metrics(f"Round Robin (Q={q})", processes, merged_timeline, context_switches, current_time, idle_time)

