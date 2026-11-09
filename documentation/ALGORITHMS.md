# Disk Scheduling Algorithms: Theory & Comparative Analysis

Disk scheduling algorithms optimize the order in which pending I/O block requests are serviced by the disk arm. In mechanical magnetic disks, seek time (moving the actuator arm across concentric cylinders) is the single most expensive physical operation, consuming orders of magnitude more time than rotational latency or electronic data transfer.

---

## Algorithm Suite

### 1. FCFS (First-Come, First-Served)
- **Concept**: Serves incoming requests strictly in their arrival order without reordering.
- **Advantages**: Simple, completely starvation-free, fair in terms of request queuing order.
- **Disadvantages**: Suffers from excessive seek oscillation ("arm thrashing") across the platter surface, resulting in poor average seek times.
- **Time Complexity**: $O(N)$

### 2. SSTF (Shortest Seek Time First)
- **Concept**: Greedily selects the pending cylinder nearest to current head position at each step.
- **Advantages**: Significantly reduces total seek distance compared to FCFS.
- **Disadvantages**: Prone to **starvation** of distant requests when nearby requests continue to arrive (arm stickiness).
- **Time Complexity**: $O(N^2)$ naive, $O(N \log N)$ with balanced search trees.

### 3. SCAN (Elevator Algorithm)
- **Concept**: The disk arm moves continuously in one direction (e.g. up towards disk boundary), servicing all requests in that path, then reverses direction at the boundary cylinder ($0$ or $C-1$).
- **Advantages**: Provides bounded wait time, prevents indefinite starvation, maintains high throughput.
- **Disadvantages**: Favors requests located near the turnaround boundaries; middle cylinders receive service twice per round-trip while edge cylinders receive service once.
- **Time Complexity**: $O(N \log N)$

### 4. C-SCAN (Circular SCAN)
- **Concept**: Similar to SCAN, but only services requests in one direction. Upon reaching the end boundary, the arm returns immediately to the start boundary without serving requests on the return journey.
- **Advantages**: Uniform waiting time distribution across all tracks; middle and edge cylinders enjoy equal opportunity.
- **Disadvantages**: Incurs seek penalty on empty circular wrap from max cylinder to track zero.
- **Time Complexity**: $O(N \log N)$

### 5. LOOK
- **Concept**: Practical optimization of SCAN. The arm travels in one direction only as far as the last requested cylinder, reversing immediately without traveling to the physical disk edge.
- **Advantages**: Eliminates unnecessary travel to unused cylinder extremes.
- **Time Complexity**: $O(N \log N)$

### 6. C-LOOK (Circular LOOK)
- **Concept**: Combines LOOK turnaround with C-SCAN's unidirectional service. It reverses at the highest requested cylinder and jumps straight to the lowest requested cylinder.
- **Advantages**: Combines uniform wait time with zero unnecessary boundary travel.
- **Time Complexity**: $O(N \log N)$

### 7. N-Step-SCAN
- **Concept**: Partitions the pending request queue into discrete subqueues of size $N$. Each subsegment is serviced using SCAN. Requests arriving during a segment run are placed in the next batch.
- **Advantages**: Completely eliminates the arm stickiness problem of SSTF/SCAN under heavy localized load.
- **Time Complexity**: $O(N \log N)$

### 8. F-SCAN (Dual-Queue SCAN)
- **Concept**: Uses two distinct queues: the *active queue* and the *frozen/deferred queue*. During a scan pass, all new requests are locked into the deferred queue.
- **Advantages**: Guarantees zero latency degradation for current pass; complete starvation immunity.
- **Time Complexity**: $O(N \log N)$

---

## Complexity & Characteristics Matrix

| Policy | Seek Efficiency | Fairness | Starvation Immune? | Boundary Sweep? | Time Complexity |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **FCFS** | Low | High (arrival) | Yes | No | $O(N)$ |
| **SSTF** | High | Low | **No** (Arm Stickiness) | No | $O(N^2)$ |
| **SCAN** | Moderate-High | Moderate | Yes | Yes (Tracks $0, C-1$) | $O(N \log N)$ |
| **C-SCAN** | Moderate | High (spatial) | Yes | Yes (Tracks $0, C-1$) | $O(N \log N)$ |
| **LOOK** | High | Moderate | Yes | No (Active extreme) | $O(N \log N)$ |
| **C-LOOK** | High | High (spatial) | Yes | No (Active extreme) | $O(N \log N)$ |
| **N-Step-SCAN** | High | High | Yes (Anti-stickiness) | No (Sub-batch) | $O(N \log N)$ |
| **F-SCAN** | High | High | Yes (Dual-queue) | No (Sub-batch) | $O(N \log N)$ |
