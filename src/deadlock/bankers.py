"""Banker's Algorithm for Deadlock Avoidance.
Implements the Safety Algorithm and Resource-Request Algorithm with complete rollback capability.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple
import copy
from src.utils.validator import InputValidator
from src.exceptions import DeadlockError, UnsafeStateError
from src.logger import app_logger


@dataclass
class SafetyCheckResult:
    is_safe: bool
    safe_sequence: List[str]
    step_traces: List[Dict[str, Any]]
    work_states: List[List[int]]


class BankersAlgorithm:
    """Simulates Dijkstra's Banker's algorithm for deadlock avoidance."""

    def __init__(
        self,
        processes: List[str],
        available: List[int],
        max_matrix: List[List[int]],
        allocation: List[List[int]],
        resource_names: Optional[List[str]] = None,
    ):
        InputValidator.validate_bankers_data(processes, available, max_matrix, allocation)
        self.processes = [str(p) for p in processes]
        self.num_processes = len(self.processes)
        self.num_resources = len(available)
        self.resource_names = (
            resource_names if resource_names and len(resource_names) == self.num_resources
            else [f"R{i}" for i in range(self.num_resources)]
        )

        self.available = [int(x) for x in available]
        self.max_matrix = [[int(x) for x in row] for row in max_matrix]
        self.allocation = [[int(x) for x in row] for row in allocation]

        # Compute Need matrix: Need = Max - Allocation
        self.need = [
            [self.max_matrix[i][j] - self.allocation[i][j] for j in range(self.num_resources)]
            for i in range(self.num_processes)
        ]

    def compute_need_matrix(self) -> List[List[int]]:
        return copy.deepcopy(self.need)

    def is_safe_state(self) -> SafetyCheckResult:
        """Executes the Banker's Safety Algorithm."""
        work = self.available.copy()
        finish = [False] * self.num_processes
        safe_sequence: List[str] = []
        step_traces: List[Dict[str, Any]] = []
        work_states: List[List[int]] = [work.copy()]

        while len(safe_sequence) < self.num_processes:
            found = False
            for i in range(self.num_processes):
                if not finish[i]:
                    # Check if Need[i] <= Work
                    can_allocate = all(self.need[i][j] <= work[j] for j in range(self.num_resources))
                    if can_allocate:
                        prev_work = work.copy()
                        for j in range(self.num_resources):
                            work[j] += self.allocation[i][j]

                        finish[i] = True
                        p_name = self.processes[i]
                        safe_sequence.append(p_name)
                        work_states.append(work.copy())
                        found = True

                        step_traces.append({
                            "process": p_name,
                            "need": self.need[i].copy(),
                            "prev_work": prev_work,
                            "allocation": self.allocation[i].copy(),
                            "new_work": work.copy(),
                            "step": len(safe_sequence)
                        })
                        break

            if not found:
                # System is in unsafe state
                app_logger.warning("Banker's Algorithm: System is in an UNSAFE state. No safe sequence exists.")
                return SafetyCheckResult(
                    is_safe=False,
                    safe_sequence=[],
                    step_traces=step_traces,
                    work_states=work_states,
                )

        app_logger.info(f"Banker's Algorithm: SAFE state confirmed. Sequence: {' -> '.join(safe_sequence)}")
        return SafetyCheckResult(
            is_safe=True,
            safe_sequence=safe_sequence,
            step_traces=step_traces,
            work_states=work_states,
        )

    def request_resources(self, process_id: str, request_vector: List[int]) -> Dict[str, Any]:
        """Resource-Request Algorithm with automatic state rollback on unsafe detection."""
        if process_id not in self.processes:
            raise DeadlockError(f"Process '{process_id}' not found in system processes.")

        p_idx = self.processes.index(process_id)
        if len(request_vector) != self.num_resources:
            raise DeadlockError(
                f"Request vector length ({len(request_vector)}) does not match resource count ({self.num_resources})."
            )

        req = [int(x) for x in request_vector]

        # Condition 1: Request[i] <= Need[i]
        for j in range(self.num_resources):
            if req[j] < 0:
                raise DeadlockError(f"Request quantity cannot be negative: {req[j]}")
            if req[j] > self.need[p_idx][j]:
                raise DeadlockError(
                    f"Error: Process '{process_id}' requested {req[j]} of {self.resource_names[j]}, which exceeds remaining need ({self.need[p_idx][j]})."
                )

        # Condition 2: Request[i] <= Available
        for j in range(self.num_resources):
            if req[j] > self.available[j]:
                return {
                    "granted": False,
                    "reason": f"Resources unavailable. Process '{process_id}' must wait for {self.resource_names[j]} (requested {req[j]}, available {self.available[j]}).",
                    "safe_sequence": None,
                }

        # Tentative allocation (Simulate state transition)
        orig_available = self.available.copy()
        orig_allocation = [row.copy() for row in self.allocation]
        orig_need = [row.copy() for row in self.need]

        for j in range(self.num_resources):
            self.available[j] -= req[j]
            self.allocation[p_idx][j] += req[j]
            self.need[p_idx][j] -= req[j]

        # Check safety of tentative state
        safety_check = self.is_safe_state()

        if safety_check.is_safe:
            app_logger.info(f"Resource request for '{process_id}' GRANTED: System remains SAFE.")
            return {
                "granted": True,
                "reason": f"Request granted. System maintains safe sequence: {' -> '.join(safety_check.safe_sequence)}",
                "safe_sequence": safety_check.safe_sequence,
                "new_available": self.available.copy(),
            }
        else:
            # ROLLBACK to previous state
            self.available = orig_available
            self.allocation = orig_allocation
            self.need = orig_need
            app_logger.warning(f"Resource request for '{process_id}' DENIED: Would lead to UNSAFE state. Rolled back.")
            return {
                "granted": False,
                "reason": f"Request DENIED. Allocating resources to '{process_id}' results in an UNSAFE state (potential deadlock). State rolled back.",
                "safe_sequence": None,
            }

