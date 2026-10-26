# 5. Find processes and manage your own jobs

Start with observation. A copied PID can eventually belong to a different
process; do not signal a service merely because its name looks familiar.

## List processes with the fields you need

```bash
ps -eo pid,ppid,user,stat,pcpu,pmem,comm --sort=-pcpu
ps -eo pid,ppid,user,stat,rss,comm --sort=-rss
ps -p "$$" -o pid,ppid,stat,comm
```

`PID` identifies a process, `PPID` its parent, and `COMM` the command name.
`RSS` is resident memory in KiB here. CPU percentage is averaged over the
process's lifetime, not an instantaneous sample. Sorting depends on procps `ps`.

The first STAT character matters: `R` is runnable/running, `S` interruptible
sleep, `D` uninterruptible sleep, and `Z` a zombie already waiting to be reaped.
A sleeping process is not automatically stuck. Extra STAT letters are modifiers.

## Find a process by name, then inspect it

```bash
pgrep -a -x bash
ps -p "$$" -o pid,ppid,lstart,etime,comm
```

`pgrep -x` matches the exact process name and `-a` includes its command line.
Arguments can contain secrets, so redact before sharing. `lstart` shows the
start time and `etime` elapsed runtime. If installed, `pstree -p` helps show
parent/child relationships; it is a view, not a reason to kill a whole tree.

## Start a short job and collect its exit status

```bash
sleep 2 &
child=$!
ps -p "$child" -o pid,ppid,stat,comm
jobs -l
wait "$child"
printf 'wait status: %s\n' "$?"
```

`&` starts a background job, `$!` captures its PID and `wait` collects its exit
status. Expect zero for this sleep. On a slow terminal it can finish before
`ps` inspects it. `jobs` lists this shell's jobs, not every process on the host.
In an interactive job-control shell, Ctrl+Z stops a foreground job, `bg` resumes
it in the background and `fg` brings it back. Backgrounding is not supervision.

## Send SIGTERM only to a child created in this block

```bash
(
    set +e
    sleep 30 &
    child=$!
    ps -p "$child" -o pid,ppid,comm
    kill -TERM "$child"
    wait "$child"
    printf 'terminated child status: %s\n' "$?"
)
```

This deliberately terminates only its own new sleep. Bash normally reports 143
for SIGTERM (128 + signal 15); other shells/programs may present termination
differently. SIGTERM gives an application a chance to handle shutdown. SIGKILL
cannot be caught and skips application cleanup; do not make it the first step.
A zombie has already exited, and a task stuck in a kernel wait may not disappear
immediately even after a fatal signal.

## Inspect your shell's files and limits

```bash
ls -l "/proc/$$/fd"
readlink "/proc/$$/cwd"
ulimit -n
```

Descriptors 0, 1 and 2 normally correspond to stdin/stdout/stderr. Other entries
may be files, pipes or sockets. `ulimit -n` shows this shell's soft open-file
limit; it is not a count of files currently open, nor proof of a service's limit.
Permissions can restrict `/proc` inspection.

## Practice

Start a five-second sleep, capture its PID, inspect its parent and state, then
wait for it without sending a signal. Explain why a normal sleep appears idle.

<details>
<summary>One answer</summary>

```bash
sleep 5 &
child=$!
ps -p "$child" -o pid,ppid,stat,comm
wait "$child"
```

</details>

[Manual: ps](https://man7.org/linux/man-pages/man1/ps.1.html)
· [signals](https://man7.org/linux/man-pages/man7/signal.7.html)
· [wait](https://man7.org/linux/man-pages/man2/wait.2.html)
· [Previous](04-users-and-access.md) · [Index](README.md) · [Next](06-memory-and-cpu.md)
