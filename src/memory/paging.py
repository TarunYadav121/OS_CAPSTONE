"""Paging and Virtual Memory Page Replacement Simulator.
Implements First-In First-Out (FIFO), Least Recently Used (LRU), and Optimal (OPT) algorithms.
Captures step-by-step frame state, hits, faults, and performance statistics.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from src.utils.validator import InputValidator
from src.logger import app_logger


@dataclass
class PageStepTrace:
    step: int
    page: int
    frames: List[Optional[int]]
    status: str  # "HIT" or "FAULT"
    evicted_page: Optional[int] = None


@dataclass
class PageReplacementResult:
    algorithm_name: str
    reference_string: List[int]
    frame_count: int
    total_references: int
    page_faults: int
    page_hits: int
    fault_ratio: float
    hit_ratio: float
    traces: List[PageStepTrace]

    def get_summary_table(self) -> tuple[List[str], List[List[Any]]]:
        headers = ["Step", "Page", "Frames State", "Event", "Evicted"]
        rows = []
        for t in self.traces:
            frame_str = "[" + ", ".join(str(f) if f is not None else "-" for f in t.frames) + "]"
            rows.append([
                t.step,
                t.page,
                frame_str,
                t.status,
                str(t.evicted_page) if t.evicted_page is not None else "None",
            ])
        return headers, rows


class PageReplacementSimulator:
    """Simulates page replacement strategies for virtual memory systems."""

    @classmethod
    def fifo(cls, pages: List[int], frame_count: int) -> PageReplacementResult:
        """First-In First-Out Page Replacement."""
        valid_pages, fc = InputValidator.validate_page_references(pages, frame_count)
        frames: List[Optional[int]] = [None] * fc
        queue: List[int] = []
        traces: List[PageStepTrace] = []
        faults = 0
        hits = 0

        for step, page in enumerate(valid_pages, start=1):
            if page in frames:
                hits += 1
                traces.append(PageStepTrace(step=step, page=page, frames=frames.copy(), status="HIT"))
            else:
                faults += 1
                evicted = None
                if None in frames:
                    # Place in first empty slot
                    empty_idx = frames.index(None)
                    frames[empty_idx] = page
                    queue.append(page)
                else:
                    # Evict oldest page from queue
                    evicted = queue.pop(0)
                    evict_idx = frames.index(evicted)
                    frames[evict_idx] = page
                    queue.append(page)
                traces.append(PageStepTrace(step=step, page=page, frames=frames.copy(), status="FAULT", evicted_page=evicted))

        total = len(valid_pages)
        fault_ratio = (faults / total * 100.0) if total > 0 else 0.0
        hit_ratio = (hits / total * 100.0) if total > 0 else 0.0

        app_logger.info(f"Page replacement [FIFO]: Frames={fc}, Faults={faults}, Hits={hits}, Hit Ratio={hit_ratio:.2f}%")

        return PageReplacementResult(
            algorithm_name="FIFO",
            reference_string=valid_pages,
            frame_count=fc,
            total_references=total,
            page_faults=faults,
            page_hits=hits,
            fault_ratio=fault_ratio,
            hit_ratio=hit_ratio,
            traces=traces,
        )

    @classmethod
    def lru(cls, pages: List[int], frame_count: int) -> PageReplacementResult:
        """Least Recently Used Page Replacement."""
        valid_pages, fc = InputValidator.validate_page_references(pages, frame_count)
        frames: List[Optional[int]] = [None] * fc
        recent_usage: Dict[int, int] = {}
        traces: List[PageStepTrace] = []
        faults = 0
        hits = 0

        for step, page in enumerate(valid_pages, start=1):
            recent_usage[page] = step
            if page in frames:
                hits += 1
                traces.append(PageStepTrace(step=step, page=page, frames=frames.copy(), status="HIT"))
            else:
                faults += 1
                evicted = None
                if None in frames:
                    empty_idx = frames.index(None)
                    frames[empty_idx] = page
                else:
                    # Find least recently used page in frames
                    evicted = min(frames, key=lambda p: recent_usage.get(p, 0))
                    evict_idx = frames.index(evicted)
                    frames[evict_idx] = page
                traces.append(PageStepTrace(step=step, page=page, frames=frames.copy(), status="FAULT", evicted_page=evicted))

        total = len(valid_pages)
        fault_ratio = (faults / total * 100.0) if total > 0 else 0.0
        hit_ratio = (hits / total * 100.0) if total > 0 else 0.0

        app_logger.info(f"Page replacement [LRU]: Frames={fc}, Faults={faults}, Hits={hits}, Hit Ratio={hit_ratio:.2f}%")

        return PageReplacementResult(
            algorithm_name="LRU",
            reference_string=valid_pages,
            frame_count=fc,
            total_references=total,
            page_faults=faults,
            page_hits=hits,
            fault_ratio=fault_ratio,
            hit_ratio=hit_ratio,
            traces=traces,
        )

    @classmethod
    def optimal(cls, pages: List[int], frame_count: int) -> PageReplacementResult:
        """Optimal Page Replacement (Belady's Optimal). Evicts page not used for longest time in future."""
        valid_pages, fc = InputValidator.validate_page_references(pages, frame_count)
        frames: List[Optional[int]] = [None] * fc
        traces: List[PageStepTrace] = []
        faults = 0
        hits = 0
        n = len(valid_pages)

        for step, page in enumerate(valid_pages, start=1):
            if page in frames:
                hits += 1
                traces.append(PageStepTrace(step=step, page=page, frames=frames.copy(), status="HIT"))
            else:
                faults += 1
                evicted = None
                if None in frames:
                    empty_idx = frames.index(None)
                    frames[empty_idx] = page
                else:
                    # Look ahead into future references
                    future_refs = valid_pages[step:]  # step is 1-based, so valid_pages[step:] is slice after current
                    best_evict_page = None
                    furthest_index = -1

                    for f_page in frames:
                        if f_page not in future_refs:
                            best_evict_page = f_page
                            break
                        else:
                            next_use = future_refs.index(f_page)
                            if next_use > furthest_index:
                                furthest_index = next_use
                                best_evict_page = f_page

                    evicted = best_evict_page
                    evict_idx = frames.index(evicted)
                    frames[evict_idx] = page
                traces.append(PageStepTrace(step=step, page=page, frames=frames.copy(), status="FAULT", evicted_page=evicted))

        total = len(valid_pages)
        fault_ratio = (faults / total * 100.0) if total > 0 else 0.0
        hit_ratio = (hits / total * 100.0) if total > 0 else 0.0

        app_logger.info(f"Page replacement [Optimal]: Frames={fc}, Faults={faults}, Hits={hits}, Hit Ratio={hit_ratio:.2f}%")

        return PageReplacementResult(
            algorithm_name="Optimal",
            reference_string=valid_pages,
            frame_count=fc,
            total_references=total,
            page_faults=faults,
            page_hits=hits,
            fault_ratio=fault_ratio,
            hit_ratio=hit_ratio,
            traces=traces,
        )

