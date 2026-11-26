"""Input Validation and Constraint Checking Utilities.
Ensures rigorous boundary, type, and semantic validation across all simulation modules.
"""

from typing import List, Dict, Any, Union
from src.exceptions import (
    ProcessValidationError,
    InvalidInputError,
    MemoryAllocationError,
    DeadlockError,
    StorageError,
)


class InputValidator:
    """Validates user and file inputs with strict boundary enforcement."""

    @staticmethod
    def validate_processes(processes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validates process specification list.
        Each process requires: 'pid' (str), 'arrival_time' (int >= 0), 'burst_time' (int > 0).
        Optional: 'priority' (int >= 0).
        """
        if not processes:
            raise ProcessValidationError("Process list cannot be empty.")

        seen_pids = set()
        validated = []

        for idx, p in enumerate(processes):
            if not isinstance(p, dict):
                raise ProcessValidationError(f"Process entry at index {idx} must be a dictionary.")

            pid = str(p.get("pid", "")).strip()
            if not pid:
                raise ProcessValidationError(f"Missing or empty 'pid' at index {idx}.")
            if pid in seen_pids:
                raise ProcessValidationError(f"Duplicate process ID detected: '{pid}'. PIDs must be unique.")
            seen_pids.add(pid)

            # Arrival time
            try:
                arrival = int(p.get("arrival_time", 0))
            except (ValueError, TypeError):
                raise ProcessValidationError(f"Process '{pid}' has non-integer arrival time.")
            if arrival < 0:
                raise ProcessValidationError(f"Process '{pid}' arrival time cannot be negative ({arrival}).")

            # Burst time
            try:
                burst = int(p.get("burst_time", 0))
            except (ValueError, TypeError):
                raise ProcessValidationError(f"Process '{pid}' has non-integer burst time.")
            if burst <= 0:
                raise ProcessValidationError(f"Process '{pid}' burst time must be strictly positive (> 0, got {burst}).")

            # Priority
            priority = 0
            if "priority" in p:
                try:
                    priority = int(p["priority"])
                except (ValueError, TypeError):
                    raise ProcessValidationError(f"Process '{pid}' has non-integer priority.")
                if priority < 0:
                    raise ProcessValidationError(f"Process '{pid}' priority cannot be negative ({priority}).")

            validated.append({
                "pid": pid,
                "arrival_time": arrival,
                "burst_time": burst,
                "priority": priority,
            })

        return validated

    @staticmethod
    def validate_quantum(quantum: Union[int, float]) -> int:
        """Validates round-robin time quantum."""
        try:
            q = int(quantum)
        except (ValueError, TypeError):
            raise ProcessValidationError(f"Round Robin quantum must be an integer, got: {quantum}")
        if q <= 0:
            raise ProcessValidationError(f"Round Robin quantum must be > 0, got: {q}")
        return q

    @staticmethod
    def validate_memory_blocks(blocks: List[int]) -> List[int]:
        """Validates initial contiguous memory partition sizes."""
        if not blocks:
            raise MemoryAllocationError("Memory partition blocks list cannot be empty.")
        validated = []
        for i, b in enumerate(blocks):
            try:
                val = int(b)
            except (ValueError, TypeError):
                raise MemoryAllocationError(f"Block at index {i} is non-integer ({b}).")
            if val <= 0:
                raise MemoryAllocationError(f"Block size at index {i} must be > 0 ({val}).")
            validated.append(val)
        return validated

    @staticmethod
    def validate_page_references(pages: List[int], frame_count: int) -> tuple[List[int], int]:
        """Validates page reference string and number of physical frames."""
        if not pages:
            raise MemoryAllocationError("Page reference string cannot be empty.")
        clean_pages = []
        for i, pg in enumerate(pages):
            try:
                val = int(pg)
            except (ValueError, TypeError):
                raise MemoryAllocationError(f"Page reference at index {i} is non-integer ({pg}).")
            if val < 0:
                raise MemoryAllocationError(f"Page number cannot be negative at index {i} ({val}).")
            clean_pages.append(val)

        try:
            fc = int(frame_count)
        except (ValueError, TypeError):
            raise MemoryAllocationError(f"Frame count must be an integer, got {frame_count}.")
        if fc <= 0:
            raise MemoryAllocationError(f"Frame count must be at least 1, got {fc}.")

        return clean_pages, fc

    @staticmethod
    def validate_bankers_data(
        processes: List[str],
        available: List[int],
        max_matrix: List[List[int]],
        allocation: List[List[int]],
    ) -> None:
        """Validates Banker's Algorithm data structures for dimension and invariant consistency."""
        num_p = len(processes)
        if num_p == 0:
            raise DeadlockError("Process list for Banker's algorithm cannot be empty.")
        num_r = len(available)
        if num_r == 0:
            raise DeadlockError("Available resources vector cannot be empty.")

        for i, av in enumerate(available):
            if int(av) < 0:
                raise DeadlockError(f"Available resource R{i} cannot be negative ({av}).")

        if len(max_matrix) != num_p:
            raise DeadlockError(f"Max matrix row count ({len(max_matrix)}) does not match process count ({num_p}).")
        if len(allocation) != num_p:
            raise DeadlockError(f"Allocation matrix row count ({len(allocation)}) does not match process count ({num_p}).")

        for i in range(num_p):
            if len(max_matrix[i]) != num_r:
                raise DeadlockError(f"Max matrix row {i} length ({len(max_matrix[i])}) != resource types ({num_r}).")
            if len(allocation[i]) != num_r:
                raise DeadlockError(f"Allocation matrix row {i} length ({len(allocation[i])}) != resource types ({num_r}).")
            for j in range(num_r):
                m_val = int(max_matrix[i][j])
                a_val = int(allocation[i][j])
                if m_val < 0 or a_val < 0:
                    raise DeadlockError(f"Matrix values cannot be negative at P{i}, R{j}.")
                if a_val > m_val:
                    raise DeadlockError(
                        f"Allocation ({a_val}) exceeds Claimed Max ({m_val}) for Process '{processes[i]}' at Resource R{j}."
                    )

    @staticmethod
    def validate_disk_requests(
        requests: List[int], initial_head: int, total_cylinders: int = 200
    ) -> tuple[List[int], int, int]:
        """Validates disk track requests, initial head position, and disk geometry."""
        try:
            tot = int(total_cylinders)
        except (ValueError, TypeError):
            raise StorageError(f"Total cylinders must be an integer, got {total_cylinders}.")
        if tot <= 1:
            raise StorageError(f"Total cylinders must be > 1, got {tot}.")

        try:
            init_h = int(initial_head)
        except (ValueError, TypeError):
            raise StorageError(f"Initial head position must be an integer, got {initial_head}.")
        if not (0 <= init_h < tot):
            raise StorageError(f"Initial head {init_h} outside cylinder range [0, {tot - 1}].")

        if not requests:
            raise StorageError("Disk track request queue cannot be empty.")

        clean_reqs = []
        for i, r in enumerate(requests):
            try:
                val = int(r)
            except (ValueError, TypeError):
                raise StorageError(f"Disk request at index {i} is non-integer ({r}).")
            if not (0 <= val < tot):
                raise StorageError(f"Disk request {val} at index {i} is out of cylinder bounds [0, {tot - 1}].")
            clean_reqs.append(val)

        return clean_reqs, init_h, tot

