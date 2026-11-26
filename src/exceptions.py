"""Custom Exception Hierarchy for Operating System Resource Management Suite.
Enables fine-grained error identification, validation enforcement, and graceful fault recovery.
"""


class OSSimulationError(Exception):
    """Base exception for all OS simulation errors."""
    def __init__(self, message: str, module_name: str = "Core"):
        super().__init__(f"[{module_name} Error] {message}")
        self.message = message
        self.module_name = module_name


class InvalidInputError(OSSimulationError):
    """Raised when user inputs, configuration files, or parameters fail validation."""
    def __init__(self, message: str, module_name: str = "Validator"):
        super().__init__(message, module_name)


class ProcessValidationError(InvalidInputError):
    """Raised when process configuration attributes (PID, arrival, burst, priority) are invalid."""
    def __init__(self, message: str):
        super().__init__(message, "ProcessScheduler")


class MemoryAllocationError(OSSimulationError):
    """Raised when memory allocation or paging operations fail."""
    def __init__(self, message: str):
        super().__init__(message, "MemoryManager")


class InsufficientMemoryError(MemoryAllocationError):
    """Raised when available memory blocks cannot satisfy the request."""
    def __init__(self, requested_size: int, available_size: int):
        super().__init__(
            f"Cannot allocate {requested_size} KB. Max contiguous or total free is {available_size} KB."
        )


class DeadlockError(OSSimulationError):
    """Base exception for deadlock-related faults."""
    def __init__(self, message: str):
        super().__init__(message, "DeadlockManager")


class UnsafeStateError(DeadlockError):
    """Raised by Banker's algorithm when an allocation results in an unsafe system state."""
    def __init__(self, process_id: str, request_vector: list):
        super().__init__(
            f"Denying request {request_vector} by Process '{process_id}': System would enter an UNSAFE state."
        )


class DeadlockDetectedError(DeadlockError):
    """Raised when cycle detection in Wait-For Graph confirms deadlock occurrence."""
    def __init__(self, deadlocked_processes: list):
        super().__init__(
            f"Deadlock detected involving processes: {', '.join(deadlocked_processes)}"
        )


class StorageError(OSSimulationError):
    """Raised when disk cylinder requests violate boundary constraints."""
    def __init__(self, message: str):
        super().__init__(message, "DiskScheduler")

