"""Memory Management Module."""
from src.memory.contiguous import ContiguousMemoryManager, MemoryBlock
from src.memory.paging import PageReplacementSimulator, PageReplacementResult, PageStepTrace

__all__ = [
    "ContiguousMemoryManager",
    "MemoryBlock",
    "PageReplacementSimulator",
    "PageReplacementResult",
    "PageStepTrace",
]

