"""Formatting and Visualization Utilities for Console Output.
Provides ASCII Gantt charts, formatted tabular reporting, and colored output.
"""

from typing import List, Dict, Any, Tuple


class TextFormatter:
    """Renders textual tables, Gantt charts, and formatted status summaries."""

    @staticmethod
    def render_table(headers: List[str], rows: List[List[Any]], title: str = "") -> str:
        """Formats data into a clean text table."""
        if not headers:
            return ""

        col_widths = [len(h) for h in headers]
        str_rows = []
        for r in rows:
            s_row = [str(cell) for cell in r]
            str_rows.append(s_row)
            for i, val in enumerate(s_row):
                if i < len(col_widths):
                    col_widths[i] = max(col_widths[i], len(val))

        # Build borders
        sep = "+-" + "-+-".join("-" * w for w in col_widths) + "-+"
        head_line = "| " + " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers)) + " |"

        lines = []
        if title:
            lines.append(f"\n=== {title.upper()} ===")
        lines.append(sep)
        lines.append(head_line)
        lines.append(sep)
        for r in str_rows:
            row_line = "| " + " | ".join(r[i].ljust(col_widths[i]) if i < len(r) else "".ljust(col_widths[i]) for i in range(len(col_widths))) + " |"
            lines.append(row_line)
        lines.append(sep)
        return "\n".join(lines)

    @staticmethod
    def render_gantt_chart(timeline: List[Tuple[str, int, int]]) -> str:
        """Renders an ASCII horizontal Gantt chart from a timeline of (PID, start_time, end_time)."""
        if not timeline:
            return "No timeline intervals to display."

        bar_segments = []
        time_markers = [str(timeline[0][1])]

        for pid, start, end in timeline:
            duration = end - start
            width = max(len(pid) + 2, duration * 3)
            segment_text = pid.center(width)
            bar_segments.append(segment_text)
            time_markers.append(str(end).rjust(width))

        bar_line = "|" + "|".join(bar_segments) + "|"
        
        # Build timeline ruler
        ruler_chars = list(str(timeline[0][1]))
        current_col = len(ruler_chars)

        for pid, start, end in timeline:
            duration = end - start
            width = max(len(pid) + 2, duration * 3)
            end_str = str(end)
            # Fill with spaces until position
            target_pos = current_col + width
            spaces_needed = target_pos - len(ruler_chars) - len(end_str) + 1
            if spaces_needed > 0:
                ruler_chars.extend([" "] * spaces_needed)
            ruler_chars.extend(list(end_str))
            current_col = target_pos

        ruler_line = "".join(ruler_chars)

        return (
            "\n--- GANTT TIMELINE TRACE ---\n"
            + bar_line + "\n"
            + ruler_line + "\n"
        )

