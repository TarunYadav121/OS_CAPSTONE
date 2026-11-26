"""Test Suite for Input Validation and Boundary Enforcement.
"""

import pytest
from src.utils.validator import InputValidator
from src.exceptions import (
    ProcessValidationError,
    MemoryAllocationError,
    DeadlockError,
    StorageError,
)


def test_validator_process_empty():
    with pytest.raises(ProcessValidationError):
        InputValidator.validate_processes([])


def test_validator_process_invalid_type():
    with pytest.raises(ProcessValidationError):
        InputValidator.validate_processes(["not-a-dict"])


def test_validator_quantum():
    assert InputValidator.validate_quantum(4) == 4
    with pytest.raises(ProcessValidationError):
        InputValidator.validate_quantum(-1)
    with pytest.raises(ProcessValidationError):
        InputValidator.validate_quantum("abc")


def test_validator_memory_blocks():
    assert InputValidator.validate_memory_blocks([100, 200]) == [100, 200]
    with pytest.raises(MemoryAllocationError):
        InputValidator.validate_memory_blocks([])
    with pytest.raises(MemoryAllocationError):
        InputValidator.validate_memory_blocks([100, 0])


def test_validator_page_references():
    pages, fc = InputValidator.validate_page_references([1, 2, 3], frame_count=3)
    assert pages == [1, 2, 3]
    assert fc == 3
    with pytest.raises(MemoryAllocationError):
        InputValidator.validate_page_references([], 3)
    with pytest.raises(MemoryAllocationError):
        InputValidator.validate_page_references([1, 2], 0)


def test_validator_disk_requests():
    reqs, h, tot = InputValidator.validate_disk_requests([10, 20], initial_head=5, total_cylinders=100)
    assert reqs == [10, 20]
    assert h == 5
    assert tot == 100
    with pytest.raises(StorageError):
        InputValidator.validate_disk_requests([], 5)
    with pytest.raises(StorageError):
        InputValidator.validate_disk_requests([10], initial_head=-1)
    with pytest.raises(StorageError):
        InputValidator.validate_disk_requests([105], initial_head=5, total_cylinders=100)

