# 5. Processes, signals, and shell jobs

A **process** is a running program with its own address space and resources. A **thread** is an execution path within a process; threads share that process's memory and many resources. Linux schedules threads, so process-oriented tools may show one row per process or one row per thread depending on options. A PID is a temporary identifier, not a permanent identity: a process can exit and its PID can later be reused.

## Observe before acting

```bash
ps -eo pid,ppid,user,stat,etime,pcpu,rss,comm --sort=-pcpu
ps -T -p "$$" -o pid,tid,stat,comm
pgrep -a -x bash
```

`ps -e` selects all processes; `-o` chooses columns; `--sort=-pcpu` orders highest CPU first (procps syntax). `PPID` is parent PID, `STAT` is state, `ETIME` elapsed runtime, and `RSS` is resident memory, commonly displayed in KiB. CPU values are sampled/averaged according to the tool and interval; a single list is not a live diagnosis. `ps -T` shows threads for the selected process, with `TID` identifying a thread. `pgrep -x` matches the exact process name and `-a` prints its command line; command lines may expose secrets, so redact them before sharing.

Common first-letter states include `R` runnable/running, `S` interruptible sleep, `D` uninterruptible sleep (often waiting on I/O), and `Z` exited but not yet reaped. A sleeping process is often healthy. A zombie has already exited: sending it a signal cannot make it exit again; its parent must collect its status. The remaining `STAT` characters are modifiers.

## Signals and safe shutdown

A signal is a notification to a process, not a command to “kill” in the everyday sense. `SIGTERM` (15) requests termination and lets a program clean up; `SIGKILL` (9) cannot be caught and prevents cleanup. Start with observation, confirm the exact target and ownership, and prefer the application's documented shutdown method. PID reuse creates a race between looking up a PID and acting on it; do not paste a stale PID into `kill`.

This example targets only a child created in the same shell block:

```bash
(
    sleep 30 &
    child=$!
    ps -p "$child" -o pid,ppid,stat,comm
    kill -TERM "$child"
    wait "$child"
    printf 'child status: %s\n' "$?"
)
```

`$!` is the PID of the most recently started asynchronous command. `kill -TERM` requests a graceful stop; `wait` collects the child's status. Bash commonly reports 143 (128 + signal 15), but exact status presentation is shell-dependent. Do not escalate to `SIGKILL` just because a process is slow; a task in uninterruptible kernel sleep may not respond immediately, even to it.

## Jobs belong to a shell

```bash
sleep 2 &
job_pid=$!
jobs -l
wait "$job_pid"
printf 'exit status: %s\n' "$?"
```

`&` runs a command asynchronously; `jobs` lists jobs managed by this shell, not all host processes. In an interactive job-control shell, Ctrl+Z suspends a foreground job, `bg` resumes it in the background, and `fg` returns it to the foreground. Closing the terminal or shell can affect jobs; backgrounding is not a service manager or durable scheduler.

## Inspect process relationships and descriptors

```bash
ps -p "$$" -o pid,ppid,lstart,etime,comm
ls -l "/proc/$$/fd"
readlink "/proc/$$/cwd"
ulimit -n
```

`$$` is this shell's PID. `/proc/PID/fd` links show open descriptors (0, 1, and 2 normally represent standard input/output/error); access may be restricted. `readlink` reports the process working directory. `ulimit -n` reports this shell's soft open-file limit, not how many files are open and not necessarily a service's limit. Tools such as `pstree -p` can visualize parent/child relationships when installed; a tree does not imply that every descendant should be terminated.

## Practice

Start `sleep 5` in the background, inspect its PID and state, then `wait` for it. Explain why it is normally sleeping rather than using CPU. No signal is needed.

```bash
sleep 5 &
p=$!
ps -p "$p" -o pid,ppid,stat,comm
wait "$p"
```

[ps manual](https://man7.org/linux/man-pages/man1/ps.1.html) · [Linux signals](https://man7.org/linux/man-pages/man7/signal.7.html) · [wait](https://man7.org/linux/man-pages/man2/wait.2.html) · [Previous](04-users-and-access.md) · [Index](README.md) · [Next](06-memory-and-cpu.md)
