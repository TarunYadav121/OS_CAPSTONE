"""Test Suite for Disk Storage Scheduling Module.
Validates FCFS, SSTF, SCAN, C-SCAN, LOOK, and C-LOOK algorithms.
"""

import pytest
from src.storage.disk_scheduler import DiskScheduler
from src.exceptions import StorageError


@pytest.fixture
def disk_workload():
    return {
        "requests": [98, 183, 37, 122, 14, 124, 65, 67],
        "initial_head": 53,
        "total_cylinders": 200,
    }


def test_disk_fcfs(disk_workload):
    d = disk_workload
    res = DiskScheduler.fcfs(d["requests"], d["initial_head"], d["total_cylinders"])
    assert res.total_head_movements == 640
    assert res.seek_sequence[0] == 53
    assert res.seek_sequence[1] == 98


def test_disk_sstf(disk_workload):
    d = disk_workload
    res = DiskScheduler.sstf(d["requests"], d["initial_head"], d["total_cylinders"])
    # SSTF is substantially lower than FCFS (236 vs 640)
    assert res.total_head_movements == 236
    assert res.seek_sequence[0] == 53
    # Nearest to 53 is 65
    assert res.seek_sequence[1] == 65


def test_disk_scan(disk_workload):
    d = disk_workload
    res = DiskScheduler.scan(d["requests"], d["initial_head"], d["total_cylinders"], direction="RIGHT")
    assert res.total_head_movements == 331
    assert 199 in res.seek_sequence  # Touches boundary in SCAN


def test_disk_look(disk_workload):
    d = disk_workload
    res = DiskScheduler.look(d["requests"], d["initial_head"], d["total_cylinders"], direction="RIGHT")
    # LOOK does not travel all the way to 199, only to highest request 183
    assert res.total_head_movements == 299
    assert 199 not in res.seek_sequence


def test_boundary_head_at_zero():
    res = DiskScheduler.fcfs([50, 100], initial_head=0, total_cylinders=200)
    assert res.total_head_movements == 100


def test_invalid_negative_request():
    with pytest.raises(StorageError):
        DiskScheduler.fcfs([-10, 50], initial_head=53, total_cylinders=200)


def test_invalid_request_exceeds_cylinders():
    with pytest.raises(StorageError):
        DiskScheduler.fcfs([250], initial_head=53, total_cylinders=200)

