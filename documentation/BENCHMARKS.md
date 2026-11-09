# Benchmark Methodology and Workload Analysis

## Objective

In real operating systems (Linux elevator schedulers, Windows I/O subsystems, database block managers), disk workloads do not conform to simplistic uniform random distributions. To rigorously evaluate scheduling policies, OSInsight-AI models five discrete synthetic workload profiles.

---

## Workload Profiles

### 1. Uniform Random (`uniform`)
- **Characteristics**: Cylinders chosen with uniform probability across $[0, C-1]$.
- **Real-World Equivalent**: General multitasking desktop operating system with diverse applications.
- **Top Performers**: **LOOK** and **SCAN** routinely outperform FCFS by 60–75% while maintaining balanced fairness.

### 2. Localized Cluster (`localized`)
- **Characteristics**: Cylinders distributed normally around a cluster centroid ($\sigma \approx 10\text{–}15$ cylinders).
- **Real-World Equivalent**: Heavy file editing, localized directory traversals, or contiguous media loading.
- **Top Performers**: **SSTF** and **LOOK** minimize seek distance dramatically. Starvation risk is low because all requests are clustered in the same cylinder zone.

### 3. Sequential Streaming (`sequential`)
- **Characteristics**: Ordered or monotonically strided requests with small delta ($\Delta c = 1 \text{ or } 2$).
- **Real-World Equivalent**: Video streaming playback, large sequential file writes, continuous log dumping.
- **Top Performers**: All algorithms perform identically when the queue is already sequential. FCFS is optimal due to zero sorting overhead.

### 4. Database OLTP (`database_oltp`)
- **Characteristics**: High-frequency cluster on table and index tracks, interspersed with distant writes to transaction journal/WAL near platter boundaries.
- **Real-World Equivalent**: PostgreSQL / MySQL transaction processing with WAL logging.
- **Top Performers**: **LOOK** and **C-LOOK** balance rapid servicing of the transactional hot zone with timely flushing of log blocks.

### 5. Ping-Pong Stress (`ping_pong`)
- **Characteristics**: Strictly alternating requests between inner tracks ($< 8\%$) and outer tracks ($> 92\%$).
- **Real-World Equivalent**: Worst-case disk arm oscillation stress test.
- **Key Insight**: FCFS produces massive arm thrashing ($> 2,500$ cylinder seeks), whereas SCAN/LOOK complete the run in under 300 seeks (an order-of-magnitude 10x improvement).

---

## Reproducing the Benchmark Suite

Run the headless benchmark CLI to reproduce empirical results:

```powershell
python -m scheduling.cli --benchmark --cylinders 200 --count 16
```
