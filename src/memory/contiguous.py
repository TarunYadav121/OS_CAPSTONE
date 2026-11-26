"""Contiguous Memory Allocation Simulator.
Implements First Fit, Best Fit, and Worst Fit partition placement algorithms.
Tracks internal/external fragmentation, partition states, and allocation logs.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from src.utils.validator import InputValidator
from src.exceptions import MemoryAllocationError
from src.logger import app_logger


@dataclass
class MemoryBlock:
    block_id: int
    size: int
    original_size: int
    allocated_process: Optional[str] = None
    internal_frag: int = 0

    @property
    def is_free(self) -> bool:
        return self.allocated_process is None


class ContiguousMemoryManager:
    """Simulates contiguous partition memory allocation strategies."""

    def __init__(self, block_sizes: List[int]):
        valid_blocks = InputValidator.validate_memory_blocks(block_sizes)
        self.initial_block_sizes = valid_blocks.copy()
        self.blocks = [
            MemoryBlock(block_id=i + 1, size=sz, original_size=sz)
            for i, sz in enumerate(valid_blocks)
        ]

    def reset(self):
        """Resets memory state to initial unallocated partitions."""
        self.blocks = [
            MemoryBlock(block_id=i + 1, size=sz, original_size=sz)
            for i, sz in enumerate(self.initial_block_sizes)
        ]

    def allocate_first_fit(self, process_requests: List[Dict[str, Any]]) -> Dict[str, Any]:
        """First Fit: Allocates the first free hole large enough."""
        self.reset()
        allocations = []
        unallocated = []

        for req in process_requests:
            pid = req["pid"]
            req_size = int(req["size"])
            placed = False

            for block in self.blocks:
                if block.is_free and block.size >= req_size:
                    block.allocated_process = pid
                    block.internal_frag = block.size - req_size
                    allocations.append({
                        "pid": pid,
                        "size": req_size,
                        "block_id": block.block_id,
                        "block_size": block.size,
                        "internal_frag": block.internal_frag,
                        "status": "ALLOCATED"
                    })
                    placed = True
                    break

            if not placed:
                unallocated.append(pid)
                allocations.append({
                    "pid": pid,
                    "size": req_size,
                    "block_id": None,
                    "block_size": None,
                    "internal_frag": 0,
                    "status": "NOT ALLOCATED"
                })

        return self._build_report("First Fit", allocations, unallocated)

    def allocate_best_fit(self, process_requests: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Best Fit: Allocates the smallest free hole that is big enough."""
        self.reset()
        allocations = []
        unallocated = []

        for req in process_requests:
            pid = req["pid"]
            req_size = int(req["size"])

            # Candidate blocks
            candidates = [b for b in self.blocks if b.is_free and b.size >= req_size]
            if candidates:
                # Pick candidate with smallest size (minimal leftover)
                best_block = min(candidates, key=lambda b: (b.size, b.block_id))
                best_block.allocated_process = pid
                best_block.internal_frag = best_block.size - req_size
                allocations.append({
                    "pid": pid,
                    "size": req_size,
                    "block_id": best_block.block_id,
                    "block_size": best_block.size,
                    "internal_frag": best_block.internal_frag,
                    "status": "ALLOCATED"
                })
            else:
                unallocated.append(pid)
                allocations.append({
                    "pid": pid,
                    "size": req_size,
                    "block_id": None,
                    "block_size": None,
                    "internal_frag": 0,
                    "status": "NOT ALLOCATED"
                })

        return self._build_report("Best Fit", allocations, unallocated)

    def allocate_worst_fit(self, process_requests: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Worst Fit: Allocates the largest available hole."""
        self.reset()
        allocations = []
        unallocated = []

        for req in process_requests:
            pid = req["pid"]
            req_size = int(req["size"])

            candidates = [b for b in self.blocks if b.is_free and b.size >= req_size]
            if candidates:
                # Pick candidate with largest size
                worst_block = max(candidates, key=lambda b: (b.size, -b.block_id))
                worst_block.allocated_process = pid
                worst_block.internal_frag = worst_block.size - req_size
                allocations.append({
                    "pid": pid,
                    "size": req_size,
                    "block_id": worst_block.block_id,
                    "block_size": worst_block.size,
                    "internal_frag": worst_block.internal_frag,
                    "status": "ALLOCATED"
                })
            else:
                unallocated.append(pid)
                allocations.append({
                    "pid": pid,
                    "size": req_size,
                    "block_id": None,
                    "block_size": None,
                    "internal_frag": 0,
                    "status": "NOT ALLOCATED"
                })

        return self._build_report("Worst Fit", allocations, unallocated)

    def _build_report(self, algorithm: str, allocations: List[Dict[str, Any]], unallocated: List[str]) -> Dict[str, Any]:
        total_internal_frag = sum(b.internal_frag for b in self.blocks if not b.is_free)
        total_free_memory = sum(b.size for b in self.blocks if b.is_free)
        # External fragmentation exists if unallocated processes exist and total free memory >= request
        ext_frag = 0
        for pid in unallocated:
            req_sz = next((a["size"] for a in allocations if a["pid"] == pid), 0)
            if total_free_memory >= req_sz:
                ext_frag += total_free_memory
                break

        app_logger.info(
            f"Contiguous memory allocation [{algorithm}]: {len(allocations) - len(unallocated)}/{len(allocations)} allocated. Total Int Frag={total_internal_frag} KB, Ext Frag={ext_frag} KB."
        )

        return {
            "algorithm": algorithm,
            "allocations": allocations,
            "unallocated_processes": unallocated,
            "total_internal_fragmentation": total_internal_frag,
            "total_free_memory": total_free_memory,
            "external_fragmentation": ext_frag,
            "memory_state": [
                {
                    "block_id": b.block_id,
                    "size": b.size,
                    "allocated_to": b.allocated_process,
                    "internal_frag": b.internal_frag,
                }
                for b in self.blocks
            ]
        }

