"""Disk Storage Scheduling Simulator.
Implements FCFS, SSTF, SCAN, C-SCAN, LOOK, and C-LOOK disk arm scheduling algorithms.
Calculates total head movements, seek trajectories, and average seek times.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Tuple
from src.utils.validator import InputValidator
from src.logger import app_logger


@dataclass
class DiskScheduleResult:
    algorithm_name: str
    initial_head: int
    total_cylinders: int
    seek_sequence: List[int]
    total_head_movements: int
    average_seek_distance: float
    direction: str

    def get_summary_table(self) -> tuple[List[str], List[List[Any]]]:
        headers = ["Step", "From Cylinder", "To Cylinder", "Seek Distance"]
        rows = []
        for i in range(len(self.seek_sequence) - 1):
            c_from = self.seek_sequence[i]
            c_to = self.seek_sequence[i + 1]
            dist = abs(c_to - c_from)
            rows.append([i + 1, c_from, c_to, dist])
        return headers, rows


class DiskScheduler:
    """Simulates hard disk drive head movement optimization algorithms."""

    # 1. FCFS
    @classmethod
    def fcfs(cls, requests: List[int], initial_head: int, total_cylinders: int = 200) -> DiskScheduleResult:
        reqs, head, tot = InputValidator.validate_disk_requests(requests, initial_head, total_cylinders)
        sequence = [head] + reqs
        total_mov = sum(abs(sequence[i + 1] - sequence[i]) for i in range(len(sequence) - 1))
        avg_dist = total_mov / len(reqs) if reqs else 0.0

        app_logger.info(f"Disk Scheduling [FCFS]: Total Movement={total_mov}, Avg Seek={avg_dist:.2f}")
        return DiskScheduleResult(
            algorithm_name="FCFS",
            initial_head=head,
            total_cylinders=tot,
            seek_sequence=sequence,
            total_head_movements=total_mov,
            average_seek_distance=avg_dist,
            direction="N/A",
        )

    # 2. SSTF (Shortest Seek Time First)
    @classmethod
    def sstf(cls, requests: List[int], initial_head: int, total_cylinders: int = 200) -> DiskScheduleResult:
        reqs, head, tot = InputValidator.validate_disk_requests(requests, initial_head, total_cylinders)
        sequence = [head]
        current = head
        pool = reqs.copy()
        total_mov = 0

        while pool:
            nearest = min(pool, key=lambda x: (abs(x - current), x))
            dist = abs(nearest - current)
            total_mov += dist
            current = nearest
            sequence.append(current)
            pool.remove(nearest)

        avg_dist = total_mov / len(reqs) if reqs else 0.0
        app_logger.info(f"Disk Scheduling [SSTF]: Total Movement={total_mov}, Avg Seek={avg_dist:.2f}")

        return DiskScheduleResult(
            algorithm_name="SSTF",
            initial_head=head,
            total_cylinders=tot,
            seek_sequence=sequence,
            total_head_movements=total_mov,
            average_seek_distance=avg_dist,
            direction="DYNAMIC",
        )

    # 3. SCAN (Elevator Algorithm)
    @classmethod
    def scan(
        cls, requests: List[int], initial_head: int, total_cylinders: int = 200, direction: str = "RIGHT"
    ) -> DiskScheduleResult:
        reqs, head, tot = InputValidator.validate_disk_requests(requests, initial_head, total_cylinders)
        sequence = [head]
        dir_upper = direction.upper()
        left = sorted([r for r in reqs if r < head])
        right = sorted([r for r in reqs if r >= head])

        if dir_upper == "RIGHT":
            # Go right up to tot - 1, then reverse left
            sequence.extend(right)
            if right and right[-1] != tot - 1:
                sequence.append(tot - 1)
            sequence.extend(reversed(left))
        else:
            # Go left down to 0, then reverse right
            sequence.extend(reversed(left))
            if left and left[0] != 0:
                sequence.append(0)
            sequence.extend(right)

        total_mov = sum(abs(sequence[i + 1] - sequence[i]) for i in range(len(sequence) - 1))
        avg_dist = total_mov / len(reqs) if reqs else 0.0

        app_logger.info(f"Disk Scheduling [SCAN {dir_upper}]: Total Movement={total_mov}")
        return DiskScheduleResult(
            algorithm_name=f"SCAN ({dir_upper})",
            initial_head=head,
            total_cylinders=tot,
            seek_sequence=sequence,
            total_head_movements=total_mov,
            average_seek_distance=avg_dist,
            direction=dir_upper,
        )

    # 4. C-SCAN (Circular SCAN)
    @classmethod
    def c_scan(
        cls, requests: List[int], initial_head: int, total_cylinders: int = 200, direction: str = "RIGHT"
    ) -> DiskScheduleResult:
        reqs, head, tot = InputValidator.validate_disk_requests(requests, initial_head, total_cylinders)
        sequence = [head]
        dir_upper = direction.upper()
        left = sorted([r for r in reqs if r < head])
        right = sorted([r for r in reqs if r >= head])

        if dir_upper == "RIGHT":
            sequence.extend(right)
            if right and right[-1] != tot - 1:
                sequence.append(tot - 1)
            sequence.append(0)
            sequence.extend(left)
        else:
            sequence.extend(reversed(left))
            if left and left[0] != 0:
                sequence.append(0)
            sequence.append(tot - 1)
            sequence.extend(reversed(right))

        total_mov = sum(abs(sequence[i + 1] - sequence[i]) for i in range(len(sequence) - 1))
        avg_dist = total_mov / len(reqs) if reqs else 0.0

        app_logger.info(f"Disk Scheduling [C-SCAN {dir_upper}]: Total Movement={total_mov}")
        return DiskScheduleResult(
            algorithm_name=f"C-SCAN ({dir_upper})",
            initial_head=head,
            total_cylinders=tot,
            seek_sequence=sequence,
            total_head_movements=total_mov,
            average_seek_distance=avg_dist,
            direction=dir_upper,
        )

    # 5. LOOK
    @classmethod
    def look(
        cls, requests: List[int], initial_head: int, total_cylinders: int = 200, direction: str = "RIGHT"
    ) -> DiskScheduleResult:
        reqs, head, tot = InputValidator.validate_disk_requests(requests, initial_head, total_cylinders)
        sequence = [head]
        dir_upper = direction.upper()
        left = sorted([r for r in reqs if r < head])
        right = sorted([r for r in reqs if r >= head])

        if dir_upper == "RIGHT":
            sequence.extend(right)
            sequence.extend(reversed(left))
        else:
            sequence.extend(reversed(left))
            sequence.extend(right)

        total_mov = sum(abs(sequence[i + 1] - sequence[i]) for i in range(len(sequence) - 1))
        avg_dist = total_mov / len(reqs) if reqs else 0.0

        app_logger.info(f"Disk Scheduling [LOOK {dir_upper}]: Total Movement={total_mov}")
        return DiskScheduleResult(
            algorithm_name=f"LOOK ({dir_upper})",
            initial_head=head,
            total_cylinders=tot,
            seek_sequence=sequence,
            total_head_movements=total_mov,
            average_seek_distance=avg_dist,
            direction=dir_upper,
        )

    # 6. C-LOOK
    @classmethod
    def c_look(
        cls, requests: List[int], initial_head: int, total_cylinders: int = 200, direction: str = "RIGHT"
    ) -> DiskScheduleResult:
        reqs, head, tot = InputValidator.validate_disk_requests(requests, initial_head, total_cylinders)
        sequence = [head]
        dir_upper = direction.upper()
        left = sorted([r for r in reqs if r < head])
        right = sorted([r for r in reqs if r >= head])

        if dir_upper == "RIGHT":
            sequence.extend(right)
            sequence.extend(left)
        else:
            sequence.extend(reversed(left))
            sequence.extend(reversed(right))

        total_mov = sum(abs(sequence[i + 1] - sequence[i]) for i in range(len(sequence) - 1))
        avg_dist = total_mov / len(reqs) if reqs else 0.0

        app_logger.info(f"Disk Scheduling [C-LOOK {dir_upper}]: Total Movement={total_mov}")
        return DiskScheduleResult(
            algorithm_name=f"C-LOOK ({dir_upper})",
            initial_head=head,
            total_cylinders=tot,
            seek_sequence=sequence,
            total_head_movements=total_mov,
            average_seek_distance=avg_dist,
            direction=dir_upper,
        )

