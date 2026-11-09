# OS Lab Viva & Oral Examination Study Guide

This document prepares students for laboratory vivas, project defenses, and university examinations on Disk Scheduling and I/O Management.

---

### Q1: What are the three primary components of total disk access time?
**Answer**:
1. **Seek Time**: The physical mechanical time required for the actuator arm to position read/write heads over the target cylinder. (Dominant component, typically 3–10 ms).
2. **Rotational Latency**: The time spent waiting for the target sector on the spinning platter to rotate under the head. (On average, half a disk rotation).
3. **Transfer Time**: The electrical rate at which magnetic flux transitions are converted into digital data sent to the host controller buffer.

---

### Q2: Why is FCFS considered inefficient despite being fair?
**Answer**: FCFS respects arrival sequence but completely ignores physical disk head positioning. If requests alternate between inner and outer tracks (the "ping-pong" effect), the head constantly traverses the entire platter, multiplying seek times and degrading I/O throughput.

---

### Q3: What is "Arm Stickiness" in SSTF, and how do N-Step-SCAN and F-SCAN resolve it?
**Answer**:
- **Arm Stickiness**: In SSTF, if new requests continually arrive close to the current head cylinder, the head remains localized in that cluster. Distant requests wait indefinitely, leading to **starvation**.
- **N-Step-SCAN**: Buffers incoming requests into sub-batches of size $N$. When a batch is being serviced, incoming requests are deferred to subsequent batches, bounding wait times.
- **F-SCAN**: Employs two distinct queues (active and frozen). All requests arriving during an active sweep are locked into the frozen queue until the active sweep terminates.

---

### Q4: Why does C-SCAN provide more uniform waiting times than standard SCAN?
**Answer**: In standard SCAN, cylinders near the middle of the disk are serviced twice during a round-trip (once going up, once returning down), whereas cylinders near the ends are serviced only once per round-trip. C-SCAN services cylinders strictly in one direction, then immediately jumps back to cylinder 0 without serving on the return, equalizing waiting time expectation across all cylinders.

---

### Q5: What is the key difference between SCAN and LOOK?
**Answer**: SCAN always travels to the absolute physical edge of the disk (track 0 or track $C-1$) before reversing, regardless of where requests reside. LOOK inspects the queue and reverses immediately at the farthest pending request, avoiding wasted arm movement over empty outer tracks.

---

### Q6: What is Jain's Fairness Index, and why does OSInsight-AI calculate it?
**Answer**: Jain's fairness index is defined as:
$$\mathcal{J}(x_1, x_2, \dots, x_n) = \frac{\left(\sum_{i=1}^n x_i\right)^2}{n \cdot \sum_{i=1}^n x_i^2}$$
where $x_i$ is the waiting distance/time for request $i$. A value of $1.0$ indicates perfect equality across all requests. In OSInsight-AI, it quantifies whether an algorithm is favoring certain cylinders at the expense of others.

---

### Q7: Do modern Solid State Drives (SSDs) use elevator algorithms?
**Answer**: No. SSDs have NAND flash memory with electronic page addressing and zero mechanical moving parts. However, SSD controllers still employ internal queue scheduling (e.g. NVMe multi-queue, NCQ, wear leveling, write amplification reduction, garbage collection scheduling, and flash block channel parallelism).

---

### Q8: How does OSInsight-AI's AI Advisor avoid being an unexplainable "black box"?
**Answer**: Rather than relying on an opaque deep neural network with untraceable outputs, OSInsight-AI uses an **explainable multi-objective scoring formulation**:
$$\text{Score} = w_{\text{seek}} \cdot \left(1 - \frac{\text{Seek}}{\text{MaxSeek}}\right) + w_{\text{fair}} \cdot \text{Fairness} + w_{\text{lat}} \cdot \left(1 - \frac{\text{Wait}}{\text{MaxWait}}\right) + w_{\text{starv}} \cdot \left(1 - \frac{\text{MaxWait}}{\text{WorstWait}}\right)$$
Every recommendation is directly verifiable by inspecting the generated candidate scores.
