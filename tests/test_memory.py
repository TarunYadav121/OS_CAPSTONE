"""Test Suite for Memory Management Module.
Validates Contiguous Allocation (First/Best/Worst Fit) and Virtual Memory Paging (FIFO, LRU, Optimal).
"""

import pytest
from src.memory.contiguous import ContiguousMemoryManager
from src.memory.paging import PageReplacementSimulator
from src.exceptions import MemoryAllocationError
# --- Contiguous Allocation Tests ---
def test_contiguous_best_fit():
    blocks = [100, 500, 200, 300, 600]
    requests = [
        {"pid": "P1", "size": 212},
        {"pid": "P2", "size": 417},
        {"pid": "P3", "size": 112},
        {"pid": "P4", "size": 426},
    ]
    mgr = ContiguousMemoryManager(blocks)
    res = mgr.allocate_best_fit(requests)

    # In Best Fit:
    # P1 (212) -> Block 4 (300)
    # P2 (417) -> Block 2 (500)
    # P3 (112) -> Block 3 (200)
    # P4 (426) -> Block 5 (600)
    assert len(res["unallocated_processes"]) == 0
    p1_alloc = next(a for a in res["allocations"] if a["pid"] == "P1")
    assert p1_alloc["block_id"] == 4
    assert p1_alloc["internal_frag"] == 300 - 212


def test_contiguous_unallocated_process():
    blocks = [100, 100]
    requests = [{"pid": "P1", "size": 250}]
    mgr = ContiguousMemoryManager(blocks)
    res = mgr.allocate_first_fit(requests)
    assert "P1" in res["unallocated_processes"]


def test_contiguous_invalid_block_size():
    with pytest.raises(MemoryAllocationError):
        ContiguousMemoryManager([100, -50, 200])

# --- Page Replacement Tests ---

def test_page_replacement_fifo():
    pages = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2]
    res = PageReplacementSimulator.fifo(pages, frame_count=3)
    assert res.total_references == len(pages)
    assert res.page_faults > 0
    assert res.page_hits > 0
    assert res.page_faults + res.page_hits == len(pages)

def test_beladys_anomaly_demonstration():
    """Belady's Anomaly: FIFO with 3 frames has 9 faults, but with 4 frames has 10 faults!"""
    pages = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]
    fifo_3 = PageReplacementSimulator.fifo(pages, frame_count=3)
    fifo_4 = PageReplacementSimulator.fifo(pages, frame_count=4)

    assert fifo_3.page_faults == 9
    assert fifo_4.page_faults == 10  # Faults increased with larger memory!

def test_optimal_performance_superiority():
    """Optimal must produce less or equal faults compared to FIFO and LRU."""
    pages = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]
    fifo_res = PageReplacementSimulator.fifo(pages, frame_count=4)
    opt_res = PageReplacementSimulator.optimal(pages, frame_count=4)
    assert opt_res.page_faults <= fifo_res.page_faults
    assert opt_res.page_faults == 6

def test_boundary_single_frame():
    pages = [1, 2, 1, 3]
    res = PageReplacementSimulator.lru(pages, frame_count=1)
    assert res.page_faults == 4  # every reference with 1 frame is a fault here

def test_invalid_negative_frame_count():
    with pytest.raises(MemoryAllocationError):
        PageReplacementSimulator.fifo([1, 2, 3], frame_count=-1)

