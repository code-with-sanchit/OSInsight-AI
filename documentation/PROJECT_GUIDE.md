# Project Guide

## Demonstration sequence

1. Use the default queue or select **Generate realistic workload**.
2. State the disk geometry, initial head, and direction.
3. Select **Balanced**, **Performance**, or **Fairness** as the AI objective.
4. Run the recommendation and compare every policy in the result table.
5. Explain the selected service path and export the PDF report.

## Metrics

| Metric | Meaning |
| --- | --- |
| Total seek | Total cylinder movement by the disk head. Lower is more efficient. |
| Average seek | Total seek divided by queued requests. |
| Fairness | Jain's fairness index over estimated request waits; 1.0 is most even. |
| Average wait | Mean distance travelled before service, used as a latency proxy. |
| Throughput | Requests serviced per movement unit in this abstract model. |

## Limitations

The simulator models cylinder movement rather than real device firmware. Modern SSDs do not have a moving head, but these algorithms remain essential for operating-systems education and for understanding queueing policy design.
