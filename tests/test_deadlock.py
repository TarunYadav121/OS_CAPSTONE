"""Test Suite for Deadlock Management Module.
Validates Banker's Safety, Resource Request Algorithm, and Wait-For Graph Cycle Detection.
"""

import pytest
from src.deadlock.bankers import BankersAlgorithm
from src.deadlock.detection import DeadlockDetector
from src.exceptions import DeadlockError


@pytest.fixture
def standard_bankers_setup():
    return {
        "processes": ["P0", "P1", "P2", "P3", "P4"],
        "available": [3, 3, 2],
        "max_matrix": [
            [7, 5, 3],
            [3, 2, 2],
            [9, 0, 2],
            [2, 2, 2],
            [4, 3, 3],
        ],
        "allocation": [
            [0, 1, 0],
            [2, 0, 0],
            [3, 0, 2],
            [2, 1, 1],
            [0, 0, 2],
        ],
    }


def test_bankers_initial_safe_state(standard_bankers_setup):
    data = standard_bankers_setup
    bankers = BankersAlgorithm(data["processes"], data["available"], data["max_matrix"], data["allocation"])
    safety = bankers.is_safe_state()
    assert safety.is_safe is True
    assert len(safety.safe_sequence) == 5
    assert safety.safe_sequence[0] == "P1" or safety.safe_sequence[0] == "P3"


def test_bankers_safe_resource_request(standard_bankers_setup):
    data = standard_bankers_setup
    bankers = BankersAlgorithm(data["processes"], data["available"], data["max_matrix"], data["allocation"])
    # P1 requests [1, 0, 2]
    res = bankers.request_resources("P1", [1, 0, 2])
    assert res["granted"] is True
    assert res["safe_sequence"] is not None


def test_bankers_exceed_maximum_claim_error(standard_bankers_setup):
    data = standard_bankers_setup
    bankers = BankersAlgorithm(data["processes"], data["available"], data["max_matrix"], data["allocation"])
    # P1 max is [3, 2, 2], alloc is [2, 0, 0], remaining need is [1, 2, 2]
    # Requesting [2, 0, 0] exceeds remaining need for resource 0 (1)!
    with pytest.raises(DeadlockError):
        bankers.request_resources("P1", [2, 0, 0])


def test_bankers_request_leads_to_unsafe_denial():
    # Setup state where request causes unsafe state
    processes = ["P0", "P1"]
    available = [1]
    max_matrix = [[2], [2]]
    allocation = [[1], [0]]
    bankers = BankersAlgorithm(processes, available, max_matrix, allocation)
    # If P1 requests 1, available becomes 0, neither can finish
    res = bankers.request_resources("P1", [1])
    assert res["granted"] is False
    assert "UNSAFE" in res["reason"]


def test_wfg_cycle_detection():
    detector = DeadlockDetector(["P1", "P2", "P3"])
    detector.add_wait_dependency("P1", "P2")
    detector.add_wait_dependency("P2", "P3")
    detector.add_wait_dependency("P3", "P1")
    has_dl, cycles = detector.detect_deadlock()
    assert has_dl is True
    assert len(cycles) > 0


def test_wfg_no_deadlock():
    detector = DeadlockDetector(["P1", "P2", "P3"])
    detector.add_wait_dependency("P1", "P2")
    detector.add_wait_dependency("P2", "P3")
    has_dl, cycles = detector.detect_deadlock()
    assert has_dl is False
    assert len(cycles) == 0


def test_invalid_bankers_matrix_dimension():
    with pytest.raises(DeadlockError):
        BankersAlgorithm(
            processes=["P1"],
            available=[3, 3],
            max_matrix=[[7]],  # 1 resource instead of 2
            allocation=[[0, 1]],
        )

