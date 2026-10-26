# 12. Performance and debugging

[Previous: Isolation and security](11-isolation-and-security.md) · [Index](README.md) · [Next: Practice labs](13-practice-labs.md)

## Start with a falsifiable question

“Linux is slow” does not identify a failing component. Record the symptom,
start time, duration, affected operations and scope: one request, process,
container, host or many hosts? Separate latency, throughput and failures. Compare
with a healthy interval and note recent changes without assuming they caused it.

Turn the observation into a hypothesis: “requests wait for CPU inside this
cgroup” is testable; “the server needs tuning” is not. Choose the cheapest
measurement that could disprove it. Preserve a small baseline, make one
controlled change only when authorized, then compare the same workload and time
window. A restart can remove evidence while only hiding the cause.

For each resource, distinguish **utilization** (how busy or occupied it is),
**saturation** (work waiting beyond available capacity) and **errors** (failed
operations). High utilization can be productive. Low host utilization can hide
a single saturated CPU, an application lock or a restrictive container quota.

## Three practical interpretation blocks

### 1. Sample over time, and keep the denominator

On systems with procps tools:

```bash
vmstat 1 3
```

This requests three reports with one-second spacing. The first report's rate
fields summarize time since boot; later reports describe sampling intervals.
Process and memory fields are snapshots. Do not compare the first row with a
one-second application spike as if their windows matched. [vmstat.8](https://man7.org/linux/man-pages/man8/vmstat.8.html)

Repeatedly elevated `r` means runnable work; compare it with CPUs actually
available to the workload, including affinity and quotas. Rising blocked work
and I/O activity suggest a different path. CPU `wa` is not a direct measure of
one application's disk latency. Confirm with device and application evidence.

Counters need differences over an interval: a large lifetime error count could
be old. Record units, timestamps and scope; resets or restarts can invalidate
subtraction. A rate without its sampling interval can conceal bursts.

### 2. Look for waiting, not just occupied memory

This reads available system pressure interfaces without changing them:

```bash
python3 - <<'PY'
from pathlib import Path
for resource in ('cpu', 'memory', 'io'):
    path = Path('/proc/pressure') / resource
    try:
        print(resource, path.read_text(), sep='\n', end='')
    except OSError as error:
        print(resource, type(error).__name__)
PY
```

PSI's `some` reports time when at least some tasks are stalled on the resource;
`full` describes simultaneous stalls of all non-idle tasks. The averages cover
ten, sixty and three hundred seconds, while `total` is cumulative stall time in
microseconds. System-level CPU `full` is not a useful all-CPU saturation measure;
the kernel documents it as undefined and reports zero for compatibility. [psi](https://docs.kernel.org/accounting/psi.html)

Memory pressure can implicate reclaim or swapping, not merely a low “free”
number. I/O pressure indicates lost progress but does not identify a device.
Absent files may mean unsupported or disabled PSI, not zero pressure.

For containers, first inspect `/proc/self/cgroup` as in
[the isolation chapter](11-isolation-and-security.md). In the correctly resolved
cgroup v2 directory, `cpu.stat` exposes throttling counters, `memory.events`
records events such as limit pressure and OOM, and resource `*.pressure` files
narrow pressure to that group. Parent limits still matter. File availability
and counter semantics depend on kernel version and controller configuration. [cgroup-v2](https://docs.kernel.org/admin-guide/cgroup-v2.html)

### 3. Trace only a small workload you own

`strace` observes system calls; it does not show every function or explain all
CPU time. If already installed, this launches a short Python process rather
than attaching to an existing service:

```bash
if command -v strace >/dev/null 2>&1; then
    strace -e trace=write python3 -c 'print("trace-lab")'
else
    printf '%s\n' 'strace unavailable; tracing example not run'
fi
```

The filter selects `write` calls; successful output should include a write to
standard output and the program's exit. Trace formatting varies. Tracing was
**not run in this validation environment** because `strace` was unavailable. [strace.1](https://man7.org/linux/man-pages/man1/strace.1.html)

Tracing changes timing and can expose paths, arguments or payloads. Filters
reduce output, not all overhead or disclosure risk. Ptrace restrictions,
seccomp and permissions may prohibit even child tracing; do not weaken them
just to finish a lab. Never treat an arbitrary `ENOENT` during a program's
normal search as the root cause without context.

## Escalate according to evidence

For CPU-bound work, profiling may identify expensive stacks; `perf` requires
compatible tooling, supported events and appropriate permissions. Sampling
has overhead and may capture sensitive execution data; no perf recording is
performed here. [perf-security](https://docs.kernel.org/admin-guide/perf-security.html) For I/O, compare latency and queues rather than treating
device busy percentage as universal capacity. For memory, correlate reclaim,
faults and limits. For networking, correlate retransmission/error deltas with
request timing; an old counter does not locate current packet loss.

Continue with existing [process and memory troubleshooting](../troubleshooting/processes-and-memory.md)
and [network troubleshooting](../troubleshooting/network-connectivity.md) rather
than applying speculative kernel tuning.

## Check your understanding

- How can an idle-looking host contain a CPU-starved application?
- Why is a cumulative error counter insufficient to explain this minute's failures?
- What can a syscall trace miss, and what sensitive information can it reveal?
