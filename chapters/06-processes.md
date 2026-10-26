# 6. Processes and signals

[Contents](../README.md) | [Previous: permissions](05-permissions.md) | [Next: resources](07-resources.md)

A process is a running instance of a program. The kernel assigns it a process ID (PID), tracks its state and schedules its work. A process can start child processes; those children may continue or exit independently.

## Inspect processes

```bash
ps -eo pid,ppid,user,stat,comm --sort=pid
```

On procps-ng systems, `ps` prints a snapshot of processes. `-e` selects all processes visible to you; `-o` chooses columns: PID, parent PID, user, state and command name. `--sort=pid` orders the rows by PID. Other `ps` implementations differ, so check `ps --help` or the local manual page. The output is a momentary view, not a live monitor.

For a live updating view, `top` displays process and system activity. Press `q` to exit. Its fields and key bindings vary. Do not assume a high CPU number alone identifies a problem: inspect the duration, workload and effect on users.

## Find one process carefully

```bash
pgrep -a ssh
```

`pgrep` searches process names; `-a` includes the full command line where supported. The pattern is matched against process names according to the implementation. It can return no matches with a nonzero status. A match identifies candidates, not necessarily the process you intend to act on. Verify the PID, user and command before any state-changing action.

`/proc` exposes kernel-provided process information on Linux. For example, `/proc/1234/status` contains fields for process 1234 if it exists and is visible. The number is only an example; replace it with a PID you have confirmed. Do not assume that a process will remain alive between inspection and a later command.

## Read state and control your shell's jobs

The `STAT` column can include `R` (running or runnable), `S` (interruptible sleep), `D` (uninterruptible sleep, often waiting on I/O), `T` (stopped), or `Z` (zombie). A zombie has exited but its parent has not yet collected its status; it is not a running process you can fix by sending it another termination signal. State is a snapshot, so repeated observations matter.

In an interactive Bash terminal, this starts a short-lived process in the background:

```bash
sleep 30 &
jobs
fg
```

`sleep 30` waits thirty seconds; `&` allows the shell to accept more input while it runs. `jobs` lists jobs belonging to this shell, not every process on the machine. `fg` brings the current job back to the foreground if it is still running. Ctrl+C normally sends an interrupt to the foreground process group. Ctrl+Z normally suspends a foreground job; `bg` resumes a stopped job in the background. These controls depend on interactive job control and the terminal settings, and are not a service-management system.

## Signals request behavior

A signal is a notification delivered to a process. `kill` sends a signal; despite its name, it does not always terminate the target. The default signal is `TERM`, a request to stop that the process may handle or ignore:

```bash
kill -TERM 1234
```

This changes process state. Replace `1234` only with a PID you have independently confirmed, and use this only for a process you own or are authorized to manage. The process may exit, refuse, or take time to finish. Check its state afterward rather than assuming the request worked.

`KILL` cannot be caught or ignored, so it prevents the process from performing its normal cleanup. Reserve it for cases where a verified target will not stop after a reasonable `TERM` period and you understand the consequences:

```bash
kill -KILL 1234
```

Never copy a numeric PID from an unrelated example. PIDs are reused, so a delayed command can target a different process. Prefer a supervisor's service-management command for a service process; killing only its child may cause an automatic restart or leave the service in an inconsistent state.

## Common confusion

- A process name match does not prove the target is the right one.
- `ps` is a snapshot; process state can change immediately afterward.
- `TERM` requests graceful shutdown; `KILL` prevents cleanup.
- PIDs are temporary identifiers and can be reused.
- A process being present does not establish that it is healthy or serving requests.

## Further reading

- [Linux man-pages: proc(5)](https://man7.org/linux/man-pages/man5/proc.5.html)
- [Linux man-pages: signal(7)](https://man7.org/linux/man-pages/man7/signal.7.html)
- [procps-ng manual](https://gitlab.com/procps-ng/procps)
