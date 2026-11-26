"""Test Suite for Process Scheduling Module.
Validates FCFS, SJF, SRTF, Priority, and Round Robin under normal, boundary, and error conditions.
"""

import pytest
from src.scheduler.algorithms import ProcessScheduler
from src.exceptions import ProcessValidationError


@pytest.fixture
def sample_processes():
    return [
        {"pid": "P1", "arrival_time": 0, "burst_time": 5, "priority": 2},
        {"pid": "P2", "arrival_time": 1, "burst_time": 3, "priority": 1},
        {"pid": "P3", "arrival_time": 2, "burst_time": 8, "priority": 3},
    ]


def test_fcfs_correctness(sample_processes):
    result = ProcessScheduler.fcfs(sample_processes)
    assert result.algorithm_name == "FCFS"
    assert result.total_time == 16
    assert result.idle_time == 0
    # P1: start 0, comp 5, tat 5, wt 0
    p1 = next(p for p in result.processes if p.pid == "P1")
    assert p1.completion_time == 5
    assert p1.waiting_time == 0
    assert p1.turnaround_time == 5


def test_sjf_non_preemptive(sample_processes):
    result = ProcessScheduler.sjf_non_preemptive(sample_processes)
    # At t=0, P1 starts and finishes at 5. At t=5, P2 and P3 are waiting. P2 has burst 3, P3 has burst 8.
    # P2 runs next (5 to 8), then P3 (8 to 16).
    p2 = next(p for p in result.processes if p.pid == "P2")
    p3 = next(p for p in result.processes if p.pid == "P3")
    assert p2.completion_time == 8
    assert p3.completion_time == 16
    assert result.avg_waiting_time < 6.0


def test_srtf_preemption(sample_processes):
    result = ProcessScheduler.srtf_preemptive(sample_processes)
    # P1 runs 0->1 (rem 4). At t=1, P2 arrives with burst 3 < 4, preempts P1!
    # P2 runs 1->4 (comp 4). Then P1 finishes 4->8. Then P3 8->16.
    p2 = next(p for p in result.processes if p.pid == "P2")
    assert p2.completion_time == 4
    assert p2.waiting_time == 0


def test_priority_non_preemptive(sample_processes):
    result = ProcessScheduler.priority_non_preemptive(sample_processes)
    # P1 runs first (0->5). At t=5, P2 (priority 1) has higher priority than P3 (priority 3).
    p2 = next(p for p in result.processes if p.pid == "P2")
    assert p2.completion_time == 8


def test_round_robin_quantum(sample_processes):
    result = ProcessScheduler.round_robin(sample_processes, quantum=2)
    assert result.total_time == 16
    assert result.context_switches > 0
    for p in result.processes:
        assert p.completion_time <= 16
        assert p.waiting_time >= 0


def test_boundary_single_process():
    single = [{"pid": "P1", "arrival_time": 5, "burst_time": 10}]
    result = ProcessScheduler.fcfs(single)
    assert result.idle_time == 5
    assert result.total_time == 15
    p1 = result.processes[0]
    assert p1.waiting_time == 0
    assert p1.turnaround_time == 10


def test_invalid_negative_burst():
    invalid = [{"pid": "P1", "arrival_time": 0, "burst_time": -5}]
    with pytest.raises(ProcessValidationError):
        ProcessScheduler.fcfs(invalid)


def test_invalid_negative_arrival():
    invalid = [{"pid": "P1", "arrival_time": -2, "burst_time": 5}]
    with pytest.raises(ProcessValidationError):
        ProcessScheduler.fcfs(invalid)


def test_invalid_duplicate_pid():
    duplicates = [
        {"pid": "P1", "arrival_time": 0, "burst_time": 5},
        {"pid": "P1", "arrival_time": 1, "burst_time": 3},
    ]
    with pytest.raises(ProcessValidationError):
        ProcessScheduler.fcfs(duplicates)


def test_invalid_empty_process_list():
    with pytest.raises(ProcessValidationError):
        ProcessScheduler.fcfs([])

