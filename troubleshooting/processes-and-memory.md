# A slow host: separate CPU, memory and waiting

A slow response is a symptom, not a diagnosis. Record when it started, which
service is affected and whether the problem is one request, one process or the
whole host. Take several observations before restarting anything.

## Find the busy processes

These commands assume Linux with procps tools. `ps --sort` is not portable to all
Unix systems.

```bash
uptime
ps -eo pid,ppid,stat,pcpu,pmem,rss,comm --sort=-pcpu
ps -eo pid,ppid,stat,pcpu,pmem,rss,comm --sort=-rss
```

`ps` CPU percentage is an average over the process's lifetime, not an immediate
sample. Use `top` for repeated samples and watch for short bursts or many workers.
`rss` is resident memory in KiB in this `ps` output. Adding RSS across processes
can overcount shared pages.

Load average includes runnable tasks and tasks in uninterruptible sleep on
Linux. It is not a CPU percentage. A high load with idle CPU can point toward
waiting rather than computation, but it does not identify the device or cause.

## Understand the process state

In the `STAT` field, the first character is the base state; extra letters are
modifiers. Common base states:

- `R`: running or runnable.
- `S`: interruptible sleep, common for healthy idle services.
- `D`: uninterruptible sleep, often related to I/O, but not proof of a disk fault.
- `Z`: zombie; the process has exited but its parent has not collected its status.

Do not treat every sleeping process as stuck. A zombie cannot be fixed by sending
it another kill signal; investigate its parent and the reaping behavior.

## Check memory pressure

```bash
free -h
vmstat 1 5
```

`available` estimates memory usable for new applications without swapping, taking
reclaimable memory into account. Low `free` memory alone is not a problem: Linux
uses otherwise idle memory for caches. Swap being occupied alone does not prove
current memory pressure. In `vmstat`, watch repeated samples of swap-in/out and
other activity; the first report is generally averages since boot, while later
reports cover the interval.

For one process, replace `1234` with the PID you observed:

```bash
pid=1234
cat "/proc/$pid/status"
ls -l "/proc/$pid/fd"
```

Inspect memory fields and file descriptors. Access can be restricted, the process
may exit between commands, and descriptor targets can reveal private paths.
High memory usage does not by itself establish a leak. Compare over time and
against workload. Container/cgroup memory limits may cause an OOM even when the
host has spare memory; host-level `free` is not the container's allowance.

## Logs and signals

On a systemd host, substitute the real service unit for this example:

```bash
journalctl -u example.service --since '15 minutes ago' --no-pager
```

The unit may not exist and journal permissions vary. This command cannot be
validated on a host without a working systemd journal. Correlate logs with the
symptom time; do not paste unredacted logs into a public issue.

If a termination is approved, confirm the PID still belongs to the right process.
SIGTERM lets the application handle shutdown. SIGKILL cannot be caught and skips
application cleanup; it is not the default troubleshooting step. Neither signal
repairs the underlying cause.

## Try it yourself

Start `sleep 60` in one terminal. In another, use `ps -C sleep -o pid,stat,comm`
to find it. You will usually see a sleeping state, even though nothing is wrong.
Let it finish or stop your own foreground command with Ctrl+C. Do not signal
unrelated processes.

## Interview takeaway

- Why can load average be high while CPU usage is low?
- Why can an application hit its memory limit while the host has free memory?

## Further reading

- [`ps(1)`](https://man7.org/linux/man-pages/man1/ps.1.html)
- [`vmstat(8)`](https://man7.org/linux/man-pages/man8/vmstat.8.html)
- [`proc_pid_status(5)`](https://man7.org/linux/man-pages/man5/proc_pid_status.5.html)
- [systemd `journalctl`](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html)

[Back to the learning path](../README.md)
