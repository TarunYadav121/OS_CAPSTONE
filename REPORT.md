# Operating System Resource Management Simulation Suite: Technical Capstone Report

**Course/Context:** Operating Systems Capstone  
**Assessment Total:** 100 Marks (Phases 1 through 5)  
**Deliverable:** Integrated Python-and-Bash Software System, Technical Analysis, Testing Harness, and Demonstration  
**Version:** 1.0.0 (Release)  
**Status:** Complete, Verified, 38/38 Unit Tests Passed  

---

## Executive Summary

Modern multiprogramming operating systems rely on four interdependent resource-management pillars to maximize hardware utilization, maintain system responsiveness, and ensure operational integrity:
1. **CPU Process Scheduling:** Allocating processor time slices among competing threads.
2. **Memory Management:** Partitioning physical RAM and managing virtual memory address spaces.
3. **Deadlock Management:** Ensuring concurrent processes do not enter unresolvable circular wait deadlocks.
4. **Secondary Storage Scheduling:** Optimizing mechanical disk arm trajectories to minimize seek latency.

Rather than implementing disconnected educational toy programs, this Capstone presents a **unified, production-grade Operating System Resource Management Simulation Suite** implemented in Python 3.12 with deep Bash shell orchestration. The system features a centralized kernel architecture, an interactive terminal dashboard, non-interactive batch automation, persistent audit logging (`simulation.log`), an extensive 38-case PyTest test suite, and automated generation of publication-quality Matplotlib analytical charts.

---

## Phase 1: System Design and Planning (20 Marks)

### 1.1 Problem Statement and Context
Operating system concepts are inherently abstract and difficult to observe directly in monolithic kernels without kernel-space instrumentation. Students and systems engineers need an integrated software laboratory where scheduling heuristics, contiguous allocation policies, virtual page fault behaviors, deadlock avoidance algorithms, and disk head trajectories can be executed under controlled, deterministic workloads.

### 1.2 System Requirements
The platform was architected to satisfy the following core requirements:
* **Functional Integration:** All four OS resource management subsystems must run under a unified controller rather than separate disjoint scripts.
* **Algorithmic Breadth:**
  * CPU Scheduling: First-Come First-Served (FCFS), Shortest Job First (SJF), Shortest Remaining Time First (SRTF), Priority Scheduling, and Round Robin (RR).
  * Memory Management: Contiguous partitioning (First Fit, Best Fit, Worst Fit) and Virtual Memory paging (FIFO, LRU, Optimal).
  * Deadlock Management: Dijkstra's Banker's Algorithm (Safety & Resource-Request with rollback) and Wait-For Graph (WFG) cycle detection.
  * Secondary Storage: Disk arm scheduling (FCFS, SSTF, SCAN, C-SCAN, LOOK, C-LOOK).
* **Cross-Language Integration:** Python backend computing numerical simulation engines; Bash scripts handling host diagnostics, batch execution pipelines, and log parsing via standard Unix tools (`awk`, `grep`, `sed`).
* **Analytical Visualization:** Automated generation of comparative tables and high-resolution graphical plots.
* **Industrial Reliability:** Strict boundary validation, custom exception hierarchy, and centralized audit logging.

### 1.3 Modular Software Architecture

The software is organized into clean functional layers adhering to the Single Responsibility Principle:

```
+-----------------------------------------------------------------------------------+
|                              Presentation Layer                                   |
|  - main.py (Interactive CLI & Arguments Parser)                                   |
|  - run.sh (Unix/Linux Bash Master Menu)                                           |
|  - run.ps1 (Windows Native PowerShell Launcher)                                   |
+-----------------------------------------------------------------------------------+
                                          |
+-----------------------------------------------------------------------------------+
|                        System Support & Infrastructure                            |
|  - src.utils.validator (Input & Boundary Validation)                             |
|  - src.utils.formatting (ASCII Tables & Gantt Timeline Renders)                   |
|  - src.logger (Dual-target Thread-Safe Audit Logger)                              |
|  - src.exceptions (Custom Hierarchical Exceptions)                                |
+-----------------------------------------------------------------------------------+
                                          |
+-----------------------------------------------------------------------------------+
|                            Core Kernel Simulators                                 |
|  +--------------------+--------------------+--------------------+---------------+ |
|  |   CPU Scheduler    |   Memory Manager   |  Deadlock Manager  | Disk Scheduler| |
|  | - Process PCB      | - Contiguous Fit   | - Banker's Safety  | - FCFS / SSTF | |
|  | - FCFS, SJF, SRTF  | - FIFO / LRU / OPT | - Resource-Request | - SCAN / CSCAN| |
|  | - Priority, RR     | - Frag Analysis    | - WFG Detection    | - LOOK / CLOOK| |
|  +--------------------+--------------------+--------------------+---------------+ |
+-----------------------------------------------------------------------------------+
                                          |
+-----------------------------------------------------------------------------------+
|                        Analysis & Output Artifact Layer                           |
|  - src.analysis.benchmark (Standardized Workload Benchmarking Engine)             |
|  - src.analysis.visualizer (Matplotlib High-Resolution Chart Generator)           |
|  - output_traces/ (Formatted Text Artifacts)                                      |
|  - charts/ (Publication-Quality PNG Visualizations)                               |
+-----------------------------------------------------------------------------------+
```

### 1.4 Data Structures Design

Each subsystem operates over strongly-typed, immutable or encapsulated data structures:

1. **Process Control Block (`Process` dataclass):**
   * `pid: str` - Unique process identifier.
   * `arrival_time: int` - Time $t$ when job enters ready queue ($t \ge 0$).
   * `burst_time: int` - Total CPU execution units required ($BT > 0$).
   * `remaining_time: int` - Dynamic counter of remaining execution cycles.
   * `priority: int` - Static priority level (lower value = higher priority).
   * `completion_time: int` - Timestamp when process terminates.
   * `turnaround_time: int` - Total residence time in system ($TAT = CT - AT$).
   * `waiting_time: int` - Idle queue time spent waiting ($WT = TAT - BT$).
   * `response_time: int` - Latency from arrival until first CPU acquisition.

2. **Memory Allocation Structures (`MemoryBlock` & `PageStepTrace`):**
   * `MemoryBlock`: Models physical memory holes with `block_id`, `size`, `allocated_process`, and `internal_frag`.
   * `PageStepTrace`: Captures virtual memory snapshots containing `step`, `page`, `frames: List[Optional[int]]`, `status: {"HIT", "FAULT"}`, and `evicted_page`.

3. **Deadlock Matrices (`BankersAlgorithm`):**
   * Available Vector: $\text{Available}[j] \in \mathbb{N}^m$, available instances of resource $R_j$.
   * Max Matrix: $\text{Max}[i][j] \in \mathbb{N}^{n \times m}$, maximum claim of process $P_i$ for resource $R_j$.
   * Allocation Matrix: $\text{Allocation}[i][j] \in \mathbb{N}^{n \times m}$, resources currently allocated.
   * Need Matrix: $\text{Need}[i][j] = \text{Max}[i][j] - \text{Allocation}[i][j]$.

4. **Disk Scheduling Structures (`DiskScheduleResult`):**
   * Encapsulates `seek_sequence: List[int]`, `total_head_movements: int`, `average_seek_distance: float`, and `direction: {"LEFT", "RIGHT", "DYNAMIC"}`.

---

## Phase 2: Core Resource-Management Modules Implementation (20 Marks)

All four primary resource-management modules, along with reporting and Unix shell integration, were implemented in Python and Bash.

### 2.1 Module 1: CPU Process Scheduling (`src/scheduler/`)
The scheduling engine implements five core algorithms:

* **First-Come, First-Served (FCFS):** Processes are dispatched in strict ascending order of arrival time:
  $$\text{Sort by } (AT_i, PID_i)$$
* **Shortest Job First (SJF - Non-Preemptive):** When the CPU becomes idle, the scheduler dispatches the arrived process with the minimum CPU burst time:
  $$P^* = \arg\min_{P_i \in \text{Ready}(t)} (BT_i, AT_i)$$
* **Shortest Remaining Time First (SRTF - Preemptive SJF):** Evaluated at every unit time quantum $t$. If a new process arrives with remaining burst time smaller than the currently executing process, a preemption context switch occurs:
  $$P^*(t) = \arg\min_{P_i \in \text{Ready}(t)} (\text{RemainingTime}_i(t))$$
* **Priority Scheduling (Non-Preemptive):** Selects the waiting job with the highest priority (numerical minimum):
  $$P^* = \arg\min_{P_i \in \text{Ready}(t)} (\text{Priority}_i)$$
* **Round Robin (RR):** Each process executes for a maximum time slice quantum $q$. If $BT_i > q$, the process is preempted and pushed to the tail of the ready queue. Newly arrived processes at time $t$ are queued immediately before preempted processes.

**Gantt Chart Generation:**  
The scheduler maintains an event interval vector `timeline: List[Tuple[str, int, int]]` capturing `(PID, start_time, end_time)`. This vector is dynamically rendered into formatted ASCII ruler charts and multi-colored Matplotlib timelines.

### 2.2 Module 2: Memory Management (`src/memory/`)
The memory subsystem covers both contiguous partition placement and virtual memory page replacement:

* **Contiguous Placement Policies:**
  * **First Fit:** Traverses physical partitions sequentially and allocates the first hole satisfying $\text{Size}_k \ge \text{ReqSize}_i$.
  * **Best Fit:** Evaluates all available partitions and selects the hole that minimizes internal fragmentation:
    $$k^* = \arg\min_{k \in \text{FreeBlocks}, \text{Size}_k \ge \text{ReqSize}} (\text{Size}_k - \text{ReqSize})$$
  * **Worst Fit:** Allocates the largest free hole, leaving behind the largest possible residual fragment.
* **Virtual Memory Page Replacement:**
  * **FIFO:** Manages a first-in, first-out queue of resident page frames.
  * **LRU:** Maintains access timestamps $U(p)$ for each referenced page and evicts $p^* = \arg\min_{p \in \text{Frames}} U(p)$.
  * **Optimal (OPT):** Scans the future reference string $S[t+1 \dots N]$ and selects the resident page whose next reference occurs furthest in the future, or never again.
  * **Belady's Anomaly Detection:** Implements automated verification showing FIFO page fault count increases when expanding physical frame capacity from 3 to 4 frames.

### 2.3 Module 3: Deadlock Management (`src/deadlock/`)
* **Banker's Safety Algorithm:**
  1. Let $\text{Work} = \text{Available}$ and $\text{Finish}[i] = \text{False}$ for $i = 0 \dots n-1$.
  2. Find an index $i$ such that:
     $$\text{Finish}[i] == \text{False} \quad \land \quad \text{Need}[i] \le \text{Work}$$
  3. If found:
     $$\text{Work} = \text{Work} + \text{Allocation}[i], \quad \text{Finish}[i] = \text{True}$$
     Append $P_i$ to Safe Sequence, repeat step 2.
  4. If all $\text{Finish}[i] == \text{True}$, system is in a **Safe State**. Otherwise, system is **Unsafe**.
* **Resource-Request Algorithm with Automatic Rollback:**
  When process $P_i$ issues request vector $\mathbf{Y}$:
  1. If $\mathbf{Y} > \text{Need}[i]$, raise `DeadlockError` (process exceeded maximum claim).
  2. If $\mathbf{Y} > \text{Available}$, process must wait (insufficient physical resources).
  3. Tentatively allocate resources:
     $$\text{Available} \gets \text{Available} - \mathbf{Y}, \quad \text{Alloc}[i] \gets \text{Alloc}[i] + \mathbf{Y}, \quad \text{Need}[i] \gets \text{Need}[i] - \mathbf{Y}$$
  4. Run Safety Algorithm. If safe, commit allocation. If unsafe, **revert state atomically** and deny the request with diagnostic justification.
* **Wait-For Graph (WFG) Deadlock Detection:**
  Processes and dependencies are modeled as a directed graph $G = (V, E)$. The cycle-detection engine uses Depth-First Search with recursion stacks to detect and isolate circular wait loops ($P_a \to P_b \to \dots \to P_a$).

### 2.4 Module 4: Disk Storage Scheduling (`src/storage/`)
* **FCFS:** Traverses requests in exact arrival order.
* **SSTF:** Greedily selects the nearest cylinder: $\min_{c \in \text{Queue}} |c - \text{Head}|$.
* **SCAN (Elevator):** Arm sweeps toward boundary track ($199$), servicing all requests, then reverses direction.
* **C-SCAN:** Arm sweeps in one direction to the boundary track ($199$), then wraps around directly to cylinder $0$ without servicing requests on the return trip.
* **LOOK / C-LOOK:** Enhanced variants of SCAN/C-SCAN that travel only as far as the highest and lowest requested cylinders, eliminating redundant head travel to track boundaries.

### 2.5 Bash & Shell Integration Suite (`bash_scripts/`)
* `run.sh`: Master interactive menu script with ANSI color-coding and automated Python environment detection.
* `bash_scripts/system_diagnostic.sh`: Host diagnostic utility inspecting CPU topology (`lscpu`/`/proc/cpuinfo`), memory allocations (`free`/`/proc/meminfo`), and filesystem capacity (`df`).
* `bash_scripts/batch_runner.sh`: Executes multi-dataset batch simulations, measures wall-clock execution time, and routes output streams.
* `bash_scripts/log_analyzer.sh`: Parses `simulation.log` using standard Unix tools (`awk`, `grep`, `sed`, `sort`, `uniq`) to output severity distributions and error events.
* `bash_scripts/run_all_tests.sh`: Automated test runner executing PyTest and checking exit codes.
* `run.ps1`: Native Windows PowerShell runner providing parity for Windows environments.

---

## Phase 3: Analysis and Comparison (20 Marks)

Standardized benchmark workloads were evaluated across all four modules. The quantitative results and technical observations are detailed below.

### 3.1 CPU Process Scheduling Performance Analysis

**Standard Workload:** 5 Processes with varied arrival times, burst times, and priorities:
* $P_1$: Arrival = 0, Burst = 8, Priority = 3
* $P_2$: Arrival = 1, Burst = 4, Priority = 1
* $P_3$: Arrival = 2, Burst = 9, Priority = 4
* $P_4$: Arrival = 3, Burst = 5, Priority = 2
* $P_5$: Arrival = 4, Burst = 2, Priority = 5

#### Comparative Quantitative Metrics
| Algorithm | Avg Waiting Time (ms) | Avg Turnaround Time (ms) | Avg Response Time (ms) | Context Switches | CPU Utilization (%) |
|---|:---:|:---:|:---:|:---:|:---:|
| **FCFS** | 11.40 | 17.00 | 11.40 | 4 | 100.0% |
| **SJF (Non-Preemptive)** | 8.20 | 13.80 | 8.20 | 4 | 100.0% |
| **SRTF (Preemptive)** | **6.60** | **12.20** | 4.40 | 5 | 100.0% |
| **Priority (Non-Preemptive)**| 10.60 | 16.20 | 10.60 | 4 | 100.0% |
| **Round Robin ($Q=2$)** | 13.00 | 18.60 | **2.80** | 13 | 100.0% |
| **Round Robin ($Q=4$)** | 13.00 | 18.60 | 6.00 | 8 | 100.0% |

#### Analytical Observations
1. **Optimal Waiting Time:** **SRTF** achieved the lowest average waiting time (6.60 ms) and turnaround time (12.20 ms), outperforming FCFS by **42.1%**. Preempting $P_1$ when shorter jobs $P_2$ and $P_5$ arrived prevented long tasks from blocking short tasks.
2. **Convoy Effect in FCFS:** In FCFS, $P_1$ (burst 8) arrived at $t=0$ and monopolized the CPU, forcing $P_5$ (burst 2) to wait 22 ms despite needing only 2 ms of computation.
3. **Round Robin Trade-Offs:** Round Robin ($Q=2$) produced the fastest average response time (**2.80 ms**), ensuring excellent interactivity, but incurred **13 context switches**, introducing scheduling overhead. Increasing the quantum to $Q=4$ reduced context switches to 8 while maintaining turnaround time parity.

---

### 3.2 Contiguous Memory Allocation Analysis

**Physical Partitions:** `[100 KB, 500 KB, 200 KB, 300 KB, 600 KB]` (Total: 1700 KB)  
**Process Requests:** $P_1$: 212 KB, $P_2$: 417 KB, $P_3$: 112 KB, $P_4$: 426 KB (Total: 1167 KB)

#### Comparative Metrics Table
| Algorithm | Allocation Success | Internal Fragmentation | External Fragmentation | Remaining Free Memory | Unallocated Processes |
|---|:---:|:---:|:---:|:---:|:---:|
| **First Fit** | 3 / 4 (75%) | 559 KB | 0 KB | 400 KB | $P_4$ |
| **Best Fit** | **4 / 4 (100%)** | **433 KB** | **0 KB** | **100 KB** | **None** |
| **Worst Fit** | 3 / 4 (75%) | 659 KB | 0 KB | 300 KB | $P_4$ |

#### Analytical Observations
* **Best Fit Superiority:** Best Fit successfully accommodated all 4 processes by pairing requests with minimally sized blocks ($P_1 \to 300$ KB, $P_2 \to 500$ KB, $P_3 \to 200$ KB, $P_4 \to 600$ KB), resulting in the lowest internal fragmentation (**433 KB**).
* **Worst Fit Suboptimality:** Worst Fit placed $P_1$ (212 KB) into the largest block (600 KB), leaving only 388 KB in that block. When $P_4$ (426 KB) arrived, no single remaining block was large enough, leaving $P_4$ unallocated despite having 300 KB of total unused memory.

---

### 3.3 Virtual Memory Page Replacement & Belady's Anomaly

**Reference String:** `[1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]` (12 page references)

#### Comparative Page Fault Metrics
| Algorithm | Physical Frames | Page Faults | Page Hits | Hit Ratio (%) | Fault Ratio (%) |
|---|:---:|:---:|:---:|:---:|:---:|
| **FIFO** | 3 | 9 | 3 | 25.00% | 75.00% |
| **FIFO** | **4** | **10** (Anomaly!) | 2 | 16.67% | 83.33% |
| **LRU** | 3 | 10 | 2 | 16.67% | 83.33% |
| **LRU** | 4 | 8 | 4 | 33.33% | 66.67% |
| **Optimal** | 3 | 7 | 5 | 41.67% | 58.33% |
| **Optimal** | **4** | **6** (Min Faults)| 6 | **50.00%** | **50.00%** |

#### Analytical Observations
1. **Empirical Verification of Belady's Anomaly:** With FIFO, expanding physical memory from 3 frames to 4 frames **increased** page faults from 9 to 10. This occurs because FIFO does not belong to the class of stack algorithms, meaning the set of pages resident with $m$ frames is not necessarily a subset of pages resident with $m+1$ frames.
2. **Stack Algorithm Stability in LRU:** In contrast to FIFO, LRU demonstrated strictly monotonic improvement, reducing faults from 10 to 8 when frame capacity increased.
3. **Optimal Benchmark:** The Optimal algorithm established the theoretical lower bound (6 faults, 50% hit ratio with 4 frames).

---

### 3.4 Secondary Storage Disk Scheduling Analysis

**Workload:** Request Queue: `[98, 183, 37, 122, 14, 124, 65, 67]`, Initial Head: `53`, Disk Bounds: `[0, 199]`, Sweep Direction: `RIGHT`.

#### Comparative Seek Overhead
| Algorithm | Total Head Movement (Cylinders) | Average Seek Distance | Arm Trajectory Characteristics |
|---|:---:|:---:|---|
| **FCFS** | 640 | 80.00 | Unoptimized, high arm oscillation across platters |
| **SSTF** | **236** | **29.50** | Lowest seek distance; susceptible to starvation |
| **LOOK (RIGHT)** | 299 | 37.38 | Reverses at highest request (183); no waste |
| **C-LOOK (RIGHT)**| 322 | 40.25 | Unidirectional fairness; jumps directly to 14 |
| **SCAN (RIGHT)** | 331 | 41.38 | Sweeps all the way to boundary cylinder 199 |
| **C-SCAN (RIGHT)**| 382 | 47.75 | Sweeps to 199, jumps to 0, services remaining |

#### Analytical Observations
* **SSTF vs FCFS:** SSTF reduced mechanical arm travel from 640 cylinders down to 236 cylinders—a **63.1% reduction in head movement**.
* **LOOK vs SCAN Optimization:** SCAN incurred 32 cylinders of unnecessary arm movement by traveling from the highest pending request (183) all the way to the end of the disk (199). LOOK eliminated this overhead by immediately reversing at cylinder 183, reducing total seek movement from 331 to 299 cylinders.
* **C-SCAN & C-LOOK Fairness:** While SSTF minimizes instantaneous distance, it starves requests far from the head. C-LOOK provides uniform wait time bounds with modest overhead (322 cylinders).

---

## Phase 4: Testing, Reliability & Exception Handling (20 Marks)

### 4.1 Test Suite Breakdown
The suite includes **38 automated PyTest cases** categorized across all subsystems:

| Test Module | Test Count | Focus Areas & Edge Cases Covered | Pass Rate |
|---|:---:|---|:---:|
| `tests/test_scheduler.py` | 10 | FCFS, SJF, SRTF preemption, Priority, RR quantum slicing, single process, negative burst/arrival, duplicate PIDs, empty process lists. | **100% (10/10)** |
| `tests/test_memory.py` | 7 | First/Best/Worst fit placement, unallocated requests, FIFO/LRU/Optimal paging, Belady's anomaly verification, single frame boundary, negative frames. | **100% (7/7)** |
| `tests/test_deadlock.py` | 7 | Banker's safe state, safe request granting, claim exceedance errors, unsafe request denial and rollback, WFG cycle detection, matrix mismatch. | **100% (7/7)** |
| `tests/test_storage.py` | 7 | FCFS, SSTF, SCAN, LOOK, head at track 0, cylinder boundary requests, negative cylinder, out-of-range track errors. | **100% (7/7)** |
| `tests/test_validation.py`| 7 | `InputValidator` comprehensive type checking, non-dict payloads, zero block sizes, non-integer values. | **100% (7/7)** |
| **Total** | **38** | **Full system coverage across normal, boundary, and error conditions** | **100% (38/38)** |

### 4.2 Boundary and Fault Injection Testing
* **Empty Workloads:** Submitting empty process lists, page strings, or disk queues immediately triggers explicit validation errors rather than unexpected `IndexError` or division-by-zero crashes.
* **Single Element Boundaries:** The scheduler correctly processes single-job workloads, computing 0 ms waiting time and maintaining consistent utilization percentages.
* **Resource Request Rollback:** When an allocation would lead to an unsafe state, Banker's algorithm temporarily modifies matrices, detects the absence of a safe sequence, rolls back `Available`, `Allocation`, and `Need` vectors to their original values, and denies the request with a clear diagnostic message.

### 4.3 Activity Audit Logging
Every kernel action is recorded in `simulation.log` with microsecond-accurate timestamps, severity levels (`INFO`, `WARNING`, `ERROR`), component identifiers, and diagnostic payloads. The shell script `bash_scripts/log_analyzer.sh` leverages `awk`, `grep`, and `sed` to summarize log distributions.

---

## Phase 5: Documentation, Demonstration & Artifacts (20 Marks)

### 5.1 Generated Artifacts Repository
The simulation generates persistent output artifacts across multiple formats:

1. **Analytical Matplotlib Visualizations (`charts/`):**
   * `process_scheduling_comparison.png`: Dual-bar comparative chart of Average Waiting Time and Turnaround Time.
   * `process_gantt_chart.png`: Stacked horizontal Gantt timeline comparing execution intervals across algorithms.
   * `page_replacement_faults.png`: Comparative bar chart demonstrating Belady's Anomaly between 3 and 4 physical frames.
   * `disk_seek_comparison.png`: Combined bar chart of head movements and 2D trajectory path plots.
   * `memory_allocation_stats.png`: Internal vs external fragmentation comparison across contiguous allocation policies.
2. **Detailed Execution Traces (`output_traces/`):**
   * `process_schedule_trace.txt`: ASCII Gantt charts, process metrics, and context switch counts.
   * `memory_trace.txt`: Contiguous memory partition states and step-by-step page reference trace tables.
   * `deadlock_trace.txt`: Allocation, Max, and Need matrices alongside step-by-step work vector derivations.
   * `disk_trace.txt`: Sequential cylinder-by-cylinder seek distances and trajectory steps.
3. **Console Interface Evidence (`screenshots/`):**
   * `terminal_menu_screen.png`: High-resolution terminal capture of the interactive menu interface.
   * `pytest_execution_screen.png`: Terminal capture showing 38 passing unit tests.

### 5.2 Reproducibility and Verification Commands
To reproduce all results, traces, and visual charts:

```bash
# 1. Clone/enter project directory
cd "c:\Users\Tarun\OneDrive\Desktop\OS Capstone"

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run complete verification suite (38 tests)
pytest -v

# 4. Execute complete integrated benchmark and export all traces & charts
python main.py --all

# 5. Run Bash diagnostics and log parser (on Linux/WSL/Git Bash)
bash bash_scripts/system_diagnostic.sh
bash bash_scripts/log_analyzer.sh
```

---

## Conclusion

This Capstone project delivers a comprehensive, production-ready operating system resource-management simulation suite. By implementing all four major OS subsystems—CPU Scheduling, Memory Management, Deadlock Management, and Storage Scheduling—within an integrated software architecture, the system provides both quantitative rigor and practical insight into OS kernel mechanisms.

The project demonstrates:
* **Algorithmic Correctness:** Full implementation of 14 operating system algorithms verified across 38 automated test cases.
* **Empirical Analysis:** Concrete verification of classical theoretical phenomena, including the Convoy Effect, Belady's Anomaly, and disk seek optimization.
* **Production Engineering Standards:** Clean object-oriented design, custom exception handling, structured audit logging, cross-platform Bash and PowerShell wrappers, and publication-ready analytical visualizations.

