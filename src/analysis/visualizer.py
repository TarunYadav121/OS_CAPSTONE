"""Visualization Generator for OS Resource Management Simulation.
Creates presentation-quality comparison charts using Matplotlib and saves them as high-res PNGs.
"""

import os
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend suitable for headless execution
import matplotlib.pyplot as plt
import numpy as np
from typing import List, Dict, Any
from src.analysis.benchmark import BenchmarkSuite
from src.logger import app_logger

OUTPUT_DIR = "charts"


class SystemVisualizer:
    """Generates analytical charts and visual traces for performance metrics."""

    @classmethod
    def ensure_output_dir(cls):
        os.makedirs(OUTPUT_DIR, exist_ok=True)

    @classmethod
    def plot_process_scheduling(cls, benchmark_data: List[Dict[str, Any]] = None) -> str:
        """Plots Waiting Time and Turnaround Time comparisons across scheduling algorithms."""
        cls.ensure_output_dir()
        if benchmark_data is None:
            benchmark_data = BenchmarkSuite.benchmark_process_scheduling()

        algorithms = [d["Algorithm"] for d in benchmark_data]
        avg_wt = [d["Avg WT (ms)"] for d in benchmark_data]
        avg_tat = [d["Avg TAT (ms)"] for d in benchmark_data]

        x = np.arange(len(algorithms))
        width = 0.35

        fig, ax = plt.subplots(figsize=(11, 6), dpi=300)
        rects1 = ax.bar(x - width / 2, avg_wt, width, label="Avg Waiting Time (ms)", color="#3498db")
        rects2 = ax.bar(x + width / 2, avg_tat, width, label="Avg Turnaround Time (ms)", color="#e74c3c")

        ax.set_ylabel("Time (milliseconds)", fontsize=12, fontweight="bold")
        ax.set_title("CPU Process Scheduling Algorithm Performance Comparison", fontsize=14, fontweight="bold", pad=15)
        ax.set_xticks(x)
        ax.set_xticklabels(algorithms, rotation=15, ha="right", fontsize=10)
        ax.legend(fontsize=11)
        ax.grid(axis="y", linestyle="--", alpha=0.7)

        # Value labels on bars
        for rect in rects1:
            height = rect.get_height()
            ax.annotate(f"{height:.1f}", xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontsize=9)
        for rect in rects2:
            height = rect.get_height()
            ax.annotate(f"{height:.1f}", xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontsize=9)

        plt.tight_layout()
        save_path = os.path.join(OUTPUT_DIR, "process_scheduling_comparison.png")
        plt.savefig(save_path)
        plt.close()
        app_logger.info(f"Saved process scheduling chart to {save_path}")
        return save_path

    @classmethod
    def plot_gantt_timelines(cls, benchmark_data: List[Dict[str, Any]] = None) -> str:
        """Plots stacked horizontal Gantt charts for CPU scheduling algorithms."""
        cls.ensure_output_dir()
        if benchmark_data is None:
            benchmark_data = BenchmarkSuite.benchmark_process_scheduling()

        fig, ax = plt.subplots(figsize=(13, 7), dpi=300)
        algorithms = [d["Algorithm"] for d in benchmark_data]

        color_palette = {
            "P1": "#3498db",
            "P2": "#2ecc71",
            "P3": "#e67e22",
            "P4": "#9b59b6",
            "P5": "#e74c3c",
            "IDLE": "#95a5a6",
        }

        y_positions = np.arange(len(algorithms))

        for idx, d in enumerate(benchmark_data):
            res = d["_raw_result"]
            for pid, start, end in res.timeline:
                col = color_palette.get(pid, "#34495e")
                duration = end - start
                ax.barh(idx, duration, left=start, height=0.55, align="center", color=col, edgecolor="black", alpha=0.9)
                # Label on segment
                if duration >= 1.5:
                    ax.text(start + duration / 2, idx, pid, ha="center", va="center", color="white", fontweight="bold", fontsize=9)

        ax.set_yticks(y_positions)
        ax.set_yticklabels(algorithms, fontsize=11, fontweight="bold")
        ax.set_xlabel("Simulation Clock Time (ms)", fontsize=12, fontweight="bold")
        ax.set_title("Comparative Gantt Execution Timelines Across Scheduling Algorithms", fontsize=14, fontweight="bold", pad=15)
        ax.invert_yaxis()
        ax.grid(axis="x", linestyle="--", alpha=0.7)

        # Add custom legend
        handles = [
            plt.Rectangle((0, 0), 1, 1, color=color_palette[p], ec="black")
            for p in ["P1", "P2", "P3", "P4", "P5", "IDLE"]
        ]
        labels = ["P1", "P2", "P3", "P4", "P5", "CPU Idle"]
        ax.legend(handles, labels, loc="upper right", ncol=6, fontsize=10)

        plt.tight_layout()
        save_path = os.path.join(OUTPUT_DIR, "process_gantt_chart.png")
        plt.savefig(save_path)
        plt.close()
        app_logger.info(f"Saved Gantt chart to {save_path}")
        return save_path

    @classmethod
    def plot_page_replacement(cls, benchmark_data: List[Dict[str, Any]] = None) -> str:
        """Plots page faults and Belady's anomaly comparison."""
        cls.ensure_output_dir()
        if benchmark_data is None:
            benchmark_data = BenchmarkSuite.benchmark_page_replacement()

        # Group by algorithm and frame count
        algs = ["FIFO", "LRU", "Optimal"]
        frames_3_faults = [next(d["Page Faults"] for d in benchmark_data if d["Algorithm"] == a and d["Frames"] == 3) for a in algs]
        frames_4_faults = [next(d["Page Faults"] for d in benchmark_data if d["Algorithm"] == a and d["Frames"] == 4) for a in algs]

        x = np.arange(len(algs))
        width = 0.35

        fig, ax = plt.subplots(figsize=(9, 5.5), dpi=300)
        r1 = ax.bar(x - width / 2, frames_3_faults, width, label="3 Physical Frames", color="#f39c12")
        r2 = ax.bar(x + width / 2, frames_4_faults, width, label="4 Physical Frames", color="#27ae60")

        ax.set_ylabel("Page Faults Count (Total: 12)", fontsize=12, fontweight="bold")
        ax.set_title("Page Replacement Comparison & Belady's Anomaly Detection", fontsize=14, fontweight="bold", pad=15)
        ax.set_xticks(x)
        ax.set_xticklabels(algs, fontsize=11, fontweight="bold")
        ax.legend(fontsize=11)
        ax.grid(axis="y", linestyle="--", alpha=0.7)

        for rect in r1:
            h = rect.get_height()
            ax.annotate(f"{h}", xy=(rect.get_x() + rect.get_width() / 2, h), xytext=(0, 3),
                        textcoords="offset points", ha="center", va="bottom", fontsize=10, fontweight="bold")
        for rect in r2:
            h = rect.get_height()
            ax.annotate(f"{h}", xy=(rect.get_x() + rect.get_width() / 2, h), xytext=(0, 3),
                        textcoords="offset points", ha="center", va="bottom", fontsize=10, fontweight="bold")

        # Belady's anomaly annotation on FIFO
        ax.annotate("Belady's Anomaly:\nFaults increased from 9 to 10\ndespite adding more frames!",
                    xy=(0 + width / 2, 10), xytext=(0.3, 11),
                    arrowprops=dict(facecolor="red", shrink=0.08, width=1.5, headwidth=8),
                    fontsize=9, color="#c0392b", fontweight="bold")

        plt.tight_layout()
        save_path = os.path.join(OUTPUT_DIR, "page_replacement_faults.png")
        plt.savefig(save_path)
        plt.close()
        app_logger.info(f"Saved page replacement chart to {save_path}")
        return save_path

    @classmethod
    def plot_disk_scheduling(cls, benchmark_data: List[Dict[str, Any]] = None) -> str:
        """Plots total head movements and seek trajectory graphs for disk algorithms."""
        cls.ensure_output_dir()
        if benchmark_data is None:
            benchmark_data = BenchmarkSuite.benchmark_disk_scheduling()

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6), dpi=300)

        # 1. Total Head Movements Bar Chart
        algs = [d["Algorithm"] for d in benchmark_data]
        movements = [d["Total Movement"] for d in benchmark_data]
        colors = ["#3498db", "#2ecc71", "#e67e22", "#9b59b6", "#1abc9c", "#d35400"]

        bars = ax1.bar(algs, movements, color=colors, edgecolor="black", alpha=0.85)
        ax1.set_ylabel("Total Head Movement (Cylinders)", fontsize=11, fontweight="bold")
        ax1.set_title("Total Seek Overhead by Algorithm", fontsize=12, fontweight="bold")
        ax1.set_xticks(range(len(algs)))
        ax1.set_xticklabels(algs, rotation=25, ha="right", fontsize=9)
        ax1.grid(axis="y", linestyle="--", alpha=0.7)

        for b in bars:
            h = b.get_height()
            ax1.annotate(f"{h}", xy=(b.get_x() + b.get_width() / 2, h), xytext=(0, 3),
                         textcoords="offset points", ha="center", va="bottom", fontsize=9, fontweight="bold")

        # 2. Seek Trajectory Graph for representative algorithms
        for d in benchmark_data:
            res = d["_raw_result"]
            steps = list(range(len(res.seek_sequence)))
            ax2.plot(res.seek_sequence, steps, marker="o", label=d["Algorithm"], linewidth=1.8, markersize=5)

        ax2.set_xlabel("Cylinder Track (0 - 199)", fontsize=11, fontweight="bold")
        ax2.set_ylabel("Sequential Seek Order Step", fontsize=11, fontweight="bold")
        ax2.set_title("Disk Arm Trajectory Seek Path", fontsize=12, fontweight="bold")
        ax2.invert_yaxis()
        ax2.legend(fontsize=8, loc="lower right")
        ax2.grid(True, linestyle="--", alpha=0.7)

        plt.suptitle("Disk Storage Arm Scheduling Performance Benchmark", fontsize=15, fontweight="bold", y=1.02)
        plt.tight_layout()
        save_path = os.path.join(OUTPUT_DIR, "disk_seek_comparison.png")
        plt.savefig(save_path)
        plt.close()
        app_logger.info(f"Saved disk scheduling chart to {save_path}")
        return save_path

    @classmethod
    def plot_memory_allocation(cls, benchmark_data: List[Dict[str, Any]] = None) -> str:
        """Plots memory allocation fragmentation and free capacity."""
        cls.ensure_output_dir()
        if benchmark_data is None:
            benchmark_data = BenchmarkSuite.benchmark_memory_allocation()

        algs = [d["Algorithm"] for d in benchmark_data]
        int_frag = [d["Internal Frag (KB)"] for d in benchmark_data]
        rem_free = [d["Remaining Free (KB)"] for d in benchmark_data]

        x = np.arange(len(algs))
        width = 0.35

        fig, ax = plt.subplots(figsize=(8.5, 5.5), dpi=300)
        b1 = ax.bar(x - width / 2, int_frag, width, label="Total Internal Fragmentation (KB)", color="#e67e22")
        b2 = ax.bar(x + width / 2, rem_free, width, label="Remaining Free Memory (KB)", color="#3498db")

        ax.set_ylabel("Memory (Kilobytes)", fontsize=11, fontweight="bold")
        ax.set_title("Contiguous Memory Partition Allocation Analysis", fontsize=13, fontweight="bold", pad=15)
        ax.set_xticks(x)
        ax.set_xticklabels(algs, fontsize=11, fontweight="bold")
        ax.legend(fontsize=10)
        ax.grid(axis="y", linestyle="--", alpha=0.7)

        for rect in b1:
            h = rect.get_height()
            ax.annotate(f"{h} KB", xy=(rect.get_x() + rect.get_width() / 2, h), xytext=(0, 3),
                        textcoords="offset points", ha="center", va="bottom", fontsize=9)
        for rect in b2:
            h = rect.get_height()
            ax.annotate(f"{h} KB", xy=(rect.get_x() + rect.get_width() / 2, h), xytext=(0, 3),
                        textcoords="offset points", ha="center", va="bottom", fontsize=9)

        plt.tight_layout()
        save_path = os.path.join(OUTPUT_DIR, "memory_allocation_stats.png")
        plt.savefig(save_path)
        plt.close()
        app_logger.info(f"Saved memory allocation chart to {save_path}")
        return save_path

    @classmethod
    def generate_all_charts(cls) -> Dict[str, str]:
        """Generates the full suite of analytical charts."""
        return {
            "process_comparison": cls.plot_process_scheduling(),
            "process_gantt": cls.plot_gantt_timelines(),
            "page_replacement": cls.plot_page_replacement(),
            "disk_scheduling": cls.plot_disk_scheduling(),
            "memory_allocation": cls.plot_memory_allocation(),
        }
