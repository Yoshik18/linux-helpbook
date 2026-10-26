# 6. Check CPU, memory and resource pressure

These commands inspect existing activity. Do not create a CPU or memory stress
workload on a shared host just to make the output more interesting.

## Get a first view

```bash
uptime
free -h
ps -eo pid,comm,pcpu,rss --sort=-pcpu
ps -eo pid,comm,pcpu,rss --sort=-rss
```

`uptime` includes load averages, not CPU percentages. On Linux load includes
runnable work and tasks in uninterruptible sleep. `free` distinguishes free,
used and available memory. Low free memory alone can simply reflect useful
caches. Compare available memory, workload behavior and repeated observations.

## Sample instead of trusting one snapshot

```bash
vmstat 1 5
```

`1` is the interval in seconds; `5` is the report count. Watch `r` for runnable
work, `b` for blocked work, `si`/`so` for swap traffic and CPU columns such as
`us`, `sy`, `id` and `wa`. The first row's rate fields normally summarize time
since boot; later rows describe intervals. Memory/process counts are snapshots.
High `wa` does not identify which application or device caused a delay.

For an interactive view, run `top` and press `q` to exit. In procps top, `P`
sorts by CPU and `M` by memory. Avoid interpreting every tool's 100% as the same
thing: per-process normalization, threads and allowed CPUs affect the denominator.

## Inspect one process, not the entire environment

```bash
ps -p "$$" -o pid,comm,vsz,rss,pcpu
awk '/^(VmSize|VmRSS|Threads):/ {print}' "/proc/$$/status"
```

VSZ is the virtual address-space size; RSS counts resident pages. They need not
grow together. Shared pages can be counted in multiple processes' RSS, so adding
all RSS values overcounts some memory. A high value is not itself evidence of a
leak; compare the same workload over time.

## Check whether a container's budget differs from the host

```bash
cat "/proc/$$/cgroup"
findmnt -t cgroup,cgroup2
```

These show membership and mounted hierarchy information. On a correctly resolved
cgroup v2 directory, useful files include `memory.current`, `memory.max`,
`memory.events`, `cpu.max` and `cpu.stat`. Do not blindly append a membership path
to `/sys/fs/cgroup`: namespace and mount roots can change the mapping. Parent
limits apply too. Cgroup v1 uses different interfaces.

A container can be killed for exceeding its memory limit while host `free`
looks healthy. `max` at a leaf does not prove ancestors impose no restriction.

## Read pressure counters when available

```bash
for resource in cpu memory io; do
    file="/proc/pressure/$resource"
    if [ -r "$file" ]; then
        printf '\n%s\n' "$resource"
        cat "$file"
    fi
done
```

PSI reports time work is stalled. `avg10`, `avg60` and `avg300` are percentages
over those windows; `total` is cumulative microseconds. A lifetime total needs
a difference over time to show current behavior. Missing files can mean unsupported
or disabled PSI, not zero stalls. System CPU `full` has special semantics; do not
use it as a universal all-CPU saturation metric.

## Practice

Capture three `vmstat` reports, then show RSS and thread count for your shell.
Write down which numbers are snapshots and which describe an interval.

<details>
<summary>One answer</summary>

```bash
vmstat 1 3
awk '/^(VmRSS|Threads):/ {print}' "/proc/$$/status"
```

</details>

[Manual: vmstat](https://man7.org/linux/man-pages/man8/vmstat.8.html)
· [proc memory fields](https://man7.org/linux/man-pages/man5/proc_meminfo.5.html)
· [cgroup v2](https://docs.kernel.org/admin-guide/cgroup-v2.html)
· [PSI](https://docs.kernel.org/accounting/psi.html)
· [Previous](05-processes-and-signals.md) · [Index](README.md) · [Next](07-storage-and-filesystems.md)
