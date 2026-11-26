"""Wait-For Graph (WFG) Deadlock Detection Engine.
Constructs process dependency graphs and isolates deadlocked process cycles using Depth-First Search.
"""

from typing import List, Dict, Set, Optional, Tuple
from src.logger import app_logger


class DeadlockDetector:
    """Detects cycles in Wait-For Graphs to identify active deadlocks."""

    def __init__(self, processes: List[str]):
        self.processes = processes
        # Adjacency list: P_i -> [P_j, P_k] where P_i waits for P_j
        self.graph: Dict[str, List[str]] = {p: [] for p in processes}

    def add_wait_dependency(self, waiting_process: str, holding_process: str):
        """Adds a directed edge: waiting_process -> holding_process."""
        if waiting_process not in self.graph:
            self.graph[waiting_process] = []
        if holding_process not in self.graph:
            self.graph[holding_process] = []
        if holding_process not in self.graph[waiting_process]:
            self.graph[waiting_process].append(holding_process)

    def detect_deadlock(self) -> Tuple[bool, List[List[str]]]:
        """Detects if any circular wait cycles exist in the graph.
        Returns (has_deadlock, list_of_cycles).
        """
        visited: Set[str] = set()
        rec_stack: Set[str] = set()
        parent_path: List[str] = []
        detected_cycles: List[List[str]] = []

        def dfs(node: str):
            visited.add(node)
            rec_stack.add(node)
            parent_path.append(node)

            for neighbor in self.graph.get(node, []):
                if neighbor not in visited:
                    dfs(neighbor)
                elif neighbor in rec_stack:
                    # Cycle detected: slice parent_path from neighbor to end
                    cycle_start = parent_path.index(neighbor)
                    cycle = parent_path[cycle_start:] + [neighbor]
                    detected_cycles.append(cycle)

            parent_path.pop()
            rec_stack.remove(node)

        for p in self.processes:
            if p not in visited:
                dfs(p)

        has_deadlock = len(detected_cycles) > 0
        if has_deadlock:
            app_logger.warning(f"Deadlock detected! Cycles found: {detected_cycles}")
        else:
            app_logger.info("Deadlock detection complete: No circular wait cycles detected.")

        return has_deadlock, detected_cycles

