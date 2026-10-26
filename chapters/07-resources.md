# 7. CPU, memory and load

[Contents](../README.md) | [Previous: processes](06-processes.md) | [Next: storage](08-storage.md)

A slow system can be waiting on CPU, memory, storage, a network service or an application lock. A single percentage rarely explains the cause. Compare measurements over time and connect them to the workload and symptoms.

## CPU use and load average

`top` displays a changing view of processes and system activity. On many systems, its header includes CPU use and load averages. A load average is an estimate of runnable and uninterruptible tasks, averaged over different time windows; it is not a CPU percentage. A load of 4 can mean different things on a 2-CPU machine and a 64-CPU machine.

```bash
uptime
```

`uptime` prints how long the system has run, the number of users, and load averages. Its format varies. Compare those averages with the number of available CPUs, but remember that tasks blocked on I/O can also contribute to load. The result alone does not tell you which process or resource is responsible.

```bash
nproc
```

`nproc` reports processing units available to the current process according to its implementation and constraints. It may differ from the physical CPU count or the number visible to the host if the process is in a container or restricted by a control group.

## Memory fields

```bash
free -h
```

`free` summarizes memory. `-h` asks for human-readable units. On Linux, the `available` estimate is often more useful than the raw `free` column because the kernel uses otherwise idle memory for caches that can be reclaimed. Field names and output formatting depend on the procps version.

Memory pressure is not proven by one low `free` value. Check whether the available estimate is falling, whether swap activity is occurring, and whether applications report allocation failures or latency. A machine can have low free memory and still operate normally because caches are reclaimable.

## Sample activity over time

Where procps supplies `vmstat`, take a bounded sample:

```bash
vmstat 1 5
```

`1` requests a one-second interval and `5` limits the number of reports. On Linux, the first report's activity figures generally summarize time since boot; later activity reports cover the sampling intervals. Do not compare the first row with a later row as if both covered one second.

Important columns include `r` (runnable processes), `b` (blocked processes), `si` and `so` (swap input/output rates), and CPU time fields such as `us` (user), `sy` (system), `id` (idle) and `wa` (I/O wait). Check the installed manual for units and field variations. Sustained swap traffic together with latency and falling available memory is stronger evidence of pressure than merely seeing allocated swap. I/O wait is a CPU-accounting measure, not the latency or utilization of a specific disk.

## Relate symptoms to evidence

Take repeated measurements under the same workload. If CPU use is high, identify which process is using it and whether that use is expected. If memory availability falls, look for a growing process or workload change. If both look normal, expand the investigation to disk waits, network latency and application-level queues rather than forcing a CPU or memory explanation.

Do not run stress generators on a shared or production host to see what happens. Resource pressure can affect every workload on the machine. Use a specifically approved disposable environment for experiments, and keep production diagnosis read-only unless you have a reviewed change plan.

## Common confusion

- Load average is not CPU utilization.
- Low `free` memory alone does not mean the machine is out of memory.
- A process's resident memory is not necessarily its unique contribution; memory can be shared.
- Container and control-group limits can make process-visible resources differ from host totals.
- One snapshot cannot establish a trend or root cause.

## Further reading

- [Linux man-pages: proc(5)](https://man7.org/linux/man-pages/man5/proc.5.html)
- [procps-ng: free](https://man7.org/linux/man-pages/man1/free.1.html)
- [Linux kernel documentation: PSI](https://docs.kernel.org/accounting/psi.html)
- [procps-ng: vmstat(8)](https://man7.org/linux/man-pages/man8/vmstat.8.html)
