# 6. Memory and CPU

[Previous: Processes and signals](05-processes-and-signals.md) · [Index](README.md) · [Next: Storage and filesystems](07-storage-and-filesystems.md)

First ask what a resource number measures, which workload it covers, and whether
useful work is waiting. This chapter assumes Linux with virtual memory, `/proc`
and procps utilities. Minimal containers may lack some tools or files.

## Virtual memory is a map, not a RAM bill

Each process uses virtual addresses. Page tables connect those addresses to
physical memory and enforce access rules. Some mapped regions have no resident
physical pages yet; others map files or pages shared with other processes.
Consequently, virtual size (VSZ) is not the amount of RAM the program currently
occupies. Resident set size (RSS) counts resident pages, including shared pages;
adding every process's RSS can count the same physical pages repeatedly. [Linux memory concepts](https://docs.kernel.org/admin-guide/mm/concepts.html)

A **page fault** means an access needs kernel attention to establish or repair a
mapping, or reject an invalid access. It does not automatically mean a crash.
Minor faults can be resolved without loading a page from storage, such as when
establishing a mapping to an already cached page. Major faults require I/O.
Interpret their rate alongside workload activity, not as isolated bad counters. [getrusage.2](https://man7.org/linux/man-pages/man2/getrusage.2.html)

## Free memory is not the same as available memory

Linux uses otherwise idle RAM for caches, including the page cache of file
contents. Clean cached pages can often be reclaimed; dirty pages need writeback
before their storage can be reused. Low `MemFree` alone therefore says little.
`MemAvailable`, exposed since Linux 3.14, estimates how much memory could support
new applications without swapping. It is an estimate, not a reservation or a
promise that every cache page is immediately reclaimable. [Linux memory concepts](https://docs.kernel.org/admin-guide/mm/concepts.html) [proc_meminfo.5](https://man7.org/linux/man-pages/man5/proc_meminfo.5.html)

Swap provides backing for eligible memory pages outside their current RAM
location. It may use disk or a configured compressed-memory device. Some swap in
use can reflect old inactivity, not current distress. Sustained swap traffic
combined with stalls is more concerning than a nonzero used-swap total. A host
can also have no swap configured; do not enable it or force pressure for this
exercise.

## A container's limit is not the host's total

`free` usually reads `/proc/meminfo`. In containers, those numbers may describe
the host rather than the application's enforced budget. Cgroups account and
limit groups of processes separately. On cgroup v2, relevant interfaces include
`memory.current`, `memory.max`, `memory.events`, `cpu.max` and `cpu.stat`.
Ancestor limits also apply; `max` at the leaf does not prove unlimited access.
A group may hit its memory limit while the host still has available RAM. [cgroup-v2](https://docs.kernel.org/admin-guide/cgroup-v2.html)

Read `/proc/$$/cgroup` to identify the shell's membership, but do not blindly
append its path to `/sys/fs/cgroup`: mount roots and cgroup namespaces can change
what is visible. Cgroup v1 uses different interfaces. Learn the runtime's actual
mount layout before interpreting or changing any limit.

## CPU time, queues and pressure answer different questions

The scheduler chooses runnable threads for the CPUs they are allowed to use.
Threads blocked on an event are not continuously executing. Affinity and cgroup
quotas can restrict capacity even when other host CPUs look idle. A process's
CPU percentage also depends on the tool's sampling interval and normalization;
some tools allow a multithreaded process to exceed 100%.

Linux load averages summarize runnable tasks **and** tasks in uninterruptible
sleep over roughly 1, 5 and 15 minutes. They are not percentages. High load with
idle CPU can reflect blocked I/O rather than a need for more processors. [proc_loadavg.5](https://man7.org/linux/man-pages/man5/proc_loadavg.5.html)
Pressure Stall Information (PSI), when enabled, reports time tasks are stalled
on CPU, memory or I/O. `/proc/pressure/` availability and cgroup visibility depend
on kernel configuration and permissions. [psi](https://docs.kernel.org/accounting/psi.html)

## Read-only observation

Run in Bash; it examines the shell and samples existing activity, without
allocating a stress workload:

```bash
ps -p "$$" -o pid,comm,vsz,rss,%cpu
grep -E '^(VmSize|VmRSS|Threads):' "/proc/$$/status"
free -h
vmstat 1 3
cat /proc/loadavg
cat "/proc/$$/cgroup"
if [ -r /proc/pressure/memory ]; then
    cat /proc/pressure/memory
fi
```

VSZ and RSS normally differ. `vmstat` reports runnable tasks (`r`), blocked tasks
(`b`), swap-in/out rates (`si`/`so`) and CPU categories. Its first row's rate and
CPU fields summarize time since boot; subsequent rows cover the sample interval.
Memory and process counts are instantaneous in either case. [vmstat.8](https://man7.org/linux/man-pages/man8/vmstat.8.html)

Tested in a Linux container. Actual values change during collection. `/proc`
fields can be approximate, restricted or absent; `/proc/self` refers to whichever
process opens it, so `cat /proc/self/status` describes `cat`, not your shell.

## Check your understanding

1. Why can VSZ rise without an equal rise in RSS?
2. Why can low free memory coexist with a healthy host?
3. What could explain a container stalling while host CPU utilization stays low?
