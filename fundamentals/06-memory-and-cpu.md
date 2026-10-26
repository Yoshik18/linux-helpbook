# 6. Read CPU and memory pressure

Begin with observation, then compare samples. Do not create a stress workload on a shared host just to produce dramatic numbers.

## Load is not CPU percentage

```bash
uptime
ps -eo pid,comm,pcpu,rss --sort=-pcpu
```

`uptime` reports load averages: Linux counts runnable work and tasks in uninterruptible sleep, averaged over 1, 5, and 15 minutes. Load is not a percentage, and its meaning depends on available CPU capacity. A high value can reflect CPU contention, blocked I/O, or both. `ps` shows a process-oriented CPU figure; its time window and normalization differ from an instantaneous host-wide measure. Use repeated samples and correlate with symptoms.

## Memory: free, available, cache, and swap

```bash
free -h
vmstat 1 5
```

`free -h` prints human-readable totals. Linux uses otherwise idle RAM for caches; “free” alone is therefore not a useful health verdict. `available` estimates memory usable for new work without swapping, but it is an estimate. `vmstat 1 5` samples every second for five reports. Its first rate row commonly reflects averages since boot; later rows describe intervals. `r` is runnable work, `b` blocked tasks, `si`/`so` swap-in/swap-out rates, and `us`, `sy`, `id`, `wa` summarize CPU time in user, kernel, idle, and I/O-wait categories. Swap usage is not equivalent to active swap pressure: sustained `si`/`so` is more informative than allocated swap alone. High `wa` does not identify a particular disk or process.

For an interactive view, run `top`, then press `q` to quit. In procps `top`, `P` sorts by CPU and `M` by memory. CPU percentages can be normalized differently across tools, cores, and threads; check the tool's mode before comparing values.

## Per-process memory is not additive

```bash
ps -p "$$" -o pid,comm,vsz,rss
awk '/^(VmSize|VmRSS|Threads):/ {print}' "/proc/$$/status"
```

`VSZ`/`VmSize` is virtual address space; `RSS`/`VmRSS` is resident physical memory. They measure different things. RSS may count shared pages in multiple processes, so summing RSS can overstate physical use. `Threads` reports the process thread count. A single high reading does not prove a leak; compare the same workload over time and consider workload size.

## Container limits and cgroups

```bash
cat "/proc/$$/cgroup"
findmnt -t cgroup,cgroup2
```

The first reports cgroup membership; the second lists visible cgroup mounts. A container can hit its own memory or CPU limit while host-level `free` looks normal. With cgroup v2, files such as `memory.current`, `memory.max`, `memory.events`, `cpu.max`, and `cpu.stat` expose usage, limits, events, and throttling. Locate the correct cgroup directory using the actual mount and namespace layout; do not blindly append a membership path to `/sys/fs/cgroup`. Ancestor limits also apply, and cgroup v1 uses different files.

## Sample pressure, not just totals

```bash
for resource in cpu memory io; do
    file="/proc/pressure/$resource"
    if [ -r "$file" ]; then
        printf '\n%s\n' "$resource"
        cat "$file"
    fi
done
```

Pressure Stall Information (PSI) estimates time work is stalled. `avg10`, `avg60`, and `avg300` are rolling percentages; `total` is cumulative microseconds, so compare two readings to infer recent stalls. Missing files can mean the kernel or configuration does not provide PSI, not that pressure is zero. CPU `full` has special system-level semantics and is not a universal saturation gauge.

## Practice

Run `vmstat 1 3`, then inspect your shell's RSS and thread count. Label which values are interval rates and which are point-in-time measurements. Avoid changing swap or cgroup settings as a beginner exercise.

[vmstat manual](https://man7.org/linux/man-pages/man8/vmstat.8.html) · [proc memory information](https://man7.org/linux/man-pages/man5/proc_meminfo.5.html) · [cgroup v2](https://docs.kernel.org/admin-guide/cgroup-v2.html) · [PSI](https://docs.kernel.org/accounting/psi.html) · [Previous](05-processes-and-signals.md) · [Index](README.md) · [Next](07-storage-and-filesystems.md)
