# 12. Debug with evidence, not guesses

A performance number is useful only with its scope and time window. Start with the affected operation, start/end time, host or container, and what changed. Preserve logs and counters before restarting or tuning. Use low-impact observations first; tracing and profiling may need permissions, add overhead, or expose sensitive data.

## 1. Is the symptom current and broad?

```bash
uptime
vmstat 1 5
```

`uptime` reports load averages over 1, 5 and 15 minutes, not CPU percent. Linux load includes runnable tasks and some uninterruptible waits; compare it with CPU count and workload. In `vmstat 1 5`, `1` is the interval in seconds and `5` the report count. The first report commonly summarizes since boot; subsequent rows describe intervals. `r` is runnable work, `b` blocked tasks, `si`/`so` swap activity and CPU fields include user/system/idle/wait. A high value is a clue, not a diagnosis; `wa` does not identify a device or process.

If installed, `top` provides an interactive view (`q` exits); `P` and `M` sort by CPU and memory in procps top. Tool versions differ. Avoid interpreting a single sample or comparing percentages with different CPU normalization.

## 2. Which process and resource changed?

```bash
ps -eo pid,ppid,stat,pcpu,rss,nlwp,comm --sort=-pcpu
ps -eo pid,stat,pcpu,rss,nlwp,comm --sort=-rss
```

These procps `ps` reports rank by CPU or resident memory. `RSS` is resident memory, commonly shown in KiB; `NLWP` is thread count. Lifetime-averaged CPU can hide recent spikes; sample again or use `pidstat -p PID 1 5` if sysstat is installed. Replace `PID` with a process you are authorized to inspect. RSS sums can double-count shared pages. Growth over repeated comparable workload samples is stronger evidence than one large number, but does not by itself prove a leak.

For your own process, narrow `/proc` output:

```bash
awk '/^(VmRSS|VmSize|Threads|voluntary_ctxt_switches|nonvoluntary_ctxt_switches):/ {print}' "/proc/$$/status"
```

These are process counters/snapshots. Context-switch totals are cumulative, not rates. A low host CPU figure does not exclude one hot thread, a CPU quota, lock contention, or work waiting elsewhere.

## 3. Is storage or memory pressure correlated?

For a path that fails to accept writes:

```bash
df -h /path/of/interest
df -i /path/of/interest
```

`df -h` checks filesystem byte capacity; `df -i` checks inode capacity. Use the actual affected path. A full filesystem may not be the only cause: quotas, permissions and read-only mounts can also block writes. To narrow directory usage, `du -x -h --max-depth=1 /path` stays on one filesystem, but a broad scan costs I/O and can be incomplete without permission. Preview a narrow, approved target; do not delete files based on size alone.

For repeated memory-pressure evidence, compare `free -h`, `vmstat` swap/reclaim activity, and—inside a container—the resolved cgroup's `memory.events` and current/max values. Parent limits apply. A host-wide free-memory snapshot cannot establish the budget or pressure in a container.

If PSI exists, read only relevant pressure files:

```bash
for r in cpu memory io; do [ -r "/proc/pressure/$r" ] && { printf '%s\n' "$r"; cat "/proc/pressure/$r"; }; done
```

`avg10/60/300` summarize stall time over windows; `total` accumulates microseconds since boot. Compare totals at two timestamps for an interval. Missing files may mean unsupported or disabled PSI, not zero pressure.

## 4. Escalate only when a hypothesis needs it

If installed, `iostat -xz 1 3` samples device statistics and adds extended fields; `-z` omits inactive devices. Compare latency, queue and throughput in the same interval as the application symptom. `%util` is not a universal saturation score, especially for parallel devices. `pidstat` and `iostat` are from sysstat and may not be installed.

For a tiny command you own, `strace -e trace=write printf 'hello\n'` launches a command and reports selected write syscalls. It is not a CPU profiler and does not explain code that runs without syscalls. Tracing may be blocked by ptrace policy and can add overhead or reveal data. Do not attach to a live service or loosen security settings to complete a lesson. `perf` is architecture/kernel/permission dependent; use only in an authorized disposable lab and read local help first.

## A practical decision sequence

1. Reproduce or timestamp the symptom; define affected scope.
2. Sample broad pressure (`vmstat`) and identify whether CPU, memory, I/O, network or a single process fits the symptom.
3. Choose one narrow measurement that can falsify the leading hypothesis; capture a second sample over the same workload.
4. Correlate application latency/logs with the measurement window. Record alternatives and uncertainty.
5. Change one thing only with authorization and rollback; measure again. Do not restart first if it would erase useful evidence.

For example, “CPU is idle” only weakens host-wide CPU saturation as a hypothesis. It does not establish network health or rule out a quota, lock, remote dependency or a single request waiting on I/O.

[Manual: vmstat](https://man7.org/linux/man-pages/man8/vmstat.8.html) · [pidstat](https://man7.org/linux/man-pages/man1/pidstat.1.html) · [iostat](https://man7.org/linux/man-pages/man1/iostat.1.html) · [Previous](11-isolation-and-security.md) · [Index](README.md) · [Next](13-practice-labs.md)
