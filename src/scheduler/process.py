"""Process Control Block (PCB) and Scheduling Metrics Representation.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class Process:
    """Represents an operating system process with scheduling metadata."""
    pid: str
    arrival_time: int
    burst_time: int
    priority: int = 0
    remaining_time: int = 0
    start_time: Optional[int] = None
    completion_time: int = 0
    waiting_time: int = 0
    turnaround_time: int = 0
    response_time: int = -1

    def __post_init__(self):
        self.remaining_time = self.burst_time

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pid": self.pid,
            "arrival_time": self.arrival_time,
            "burst_time": self.burst_time,
            "priority": self.priority,
            "completion_time": self.completion_time,
            "turnaround_time": self.turnaround_time,
            "waiting_time": self.waiting_time,
            "response_time": self.response_time,
        }


@dataclass
class ScheduleResult:
    """Encapsulates the output of a process scheduling algorithm run."""
    algorithm_name: str
    processes: List[Process]
    timeline: List[tuple[str, int, int]]  # (pid, start, end)
    context_switches: int
    total_time: int
    idle_time: int
    cpu_utilization: float
    avg_waiting_time: float
    avg_turnaround_time: float
    avg_response_time: float

    def get_summary_table(self) -> tuple[List[str], List[List[Any]]]:
        headers = ["PID", "Arrival", "Burst", "Priority", "Completion", "Turnaround", "Waiting", "Response"]
        rows = []
        for p in sorted(self.processes, key=lambda x: x.pid):
            rows.append([
                p.pid,
                p.arrival_time,
                p.burst_time,
                p.priority,
                p.completion_time,
                p.turnaround_time,
                p.waiting_time,
                p.response_time,
            ])
        return headers, rows

