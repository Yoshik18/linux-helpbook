# 5. Processes and signals

[Previous: Users and access](04-users-and-access.md) · [Index](README.md) · [Next: Memory and CPU](06-memory-and-cpu.md)

A program is executable code; a process is a running instance with memory,
credentials and open resources. Two terminals running the same editor normally
have different processes. A process ID (PID) identifies a process within a PID
namespace, not forever: Linux reuses IDs after processes disappear.

## Starting a program is two different operations

The classic shell model is **fork, then exec**. `fork()` creates a child with its
own PID and a parent PID (PPID). Its address space initially resembles the
parent's, but Linux uses copy-on-write: most private pages need not be physically
copied until somebody modifies them. [fork.2](https://man7.org/linux/man-pages/man2/fork.2.html)

`execve()` replaces the calling process's program image. It does **not** create
another process or change its PID. This distinction explains why a shell can
prepare redirections in a child, then turn that child into another program.
Shell built-ins and implementations using other creation interfaces mean not
every command literally follows that sequence. [execve.2](https://man7.org/linux/man-pages/man2/execve.2.html)

A thread is an execution stream within a process. Threads have separate stacks
and scheduling identities but share resources such as the address space and
usually the file descriptor table. Linux schedules threads; one busy thread does
not imply every thread in that process is busy. [pthreads.7](https://man7.org/linux/man-pages/man7/pthreads.7.html)

## File descriptors connect programs

A file descriptor is a small integer indexing an open resource, not necessarily
a disk file. Conventionally, 0 is standard input, 1 standard output and 2 standard
error. Pipes and sockets also use descriptors. Redirection changes what these
numbers refer to; the receiving program can keep writing to descriptor 1 without
knowing whether it leads to a terminal or a file.

After fork, corresponding descriptors refer to the same underlying open file
description, so they can share a file offset. Across exec, descriptors normally
remain open unless marked close-on-exec. This is how a pipeline survives replacing
the child shell with the requested executable. [fork.2](https://man7.org/linux/man-pages/man2/fork.2.html) [execve.2](https://man7.org/linux/man-pages/man2/execve.2.html)

## Signals request an action, not always termination

A signal notifies a process or thread about an event. Its default action might
terminate, stop, continue or do nothing. Programs can handle or ignore many
signals. `SIGTERM` requests termination and gives a cooperating application a
chance to finish work. `SIGKILL` cannot be caught, blocked or ignored; it offers
no application cleanup. Neither is a promise that unfinished data becomes
consistent. [signal.7](https://man7.org/linux/man-pages/man7/signal.7.html)

Do not treat `kill -9` as a first troubleshooting step. Confirm ownership,
identity and consequences before signaling anything; an old copied PID can now
belong to a different process. For managed applications, coordinate with the
service owner rather than fighting a supervisor that will start another copy.

In an interactive shell, Ctrl-C normally sends `SIGINT` to the foreground
process group. Ctrl-Z normally stops it. `jobs` shows that shell's jobs, not all
processes; a pipeline can be one job containing several processes. `fg` resumes
a job in the foreground. Background execution does not make a command a managed
service.

## Read the state before deciding what is wrong

In procps `ps`, `R` means running or runnable; `S` is interruptible sleep, often
normal waiting. `D` means uninterruptible sleep, usually an I/O-related kernel
wait. A task in such a wait may not finish exiting even after `SIGKILL` until the
wait resolves. Investigate the blocked resource rather than escalating signals
repeatedly. [ps.1](https://man7.org/linux/man-pages/man1/ps.1.html)

A `Z` zombie has **already exited**. The kernel retains a small record so the
parent can collect its exit status with a wait operation. Another kill cannot
make a dead process exit again. Persistent zombies suggest a parent or supervisor
is not reaping children; they are not running copies consuming CPU. [wait.2](https://man7.org/linux/man-pages/man2/wait.2.html)

## Safe observation: your own short-lived child

Run this in Bash with procps `ps`; no root access or signaling is needed:

```bash
sleep 2 &
child=$!
ps -p "$child" -o pid,ppid,stat,comm
jobs -l
wait "$child"
printf 'Child exit status: %s\n' "$?"
```

Usually `sleep` appears in `S`, its PPID matches the shell, and `wait` returns 0.
On a slow session it may exit before `ps` runs; that is a timing difference, not
a failure. Tested in a Linux container; interactive job-control behavior was not
tested. Never substitute a PID from another session into a termination experiment.

## Check your understanding

1. Why can exec change the program name without changing the PID?
2. How does an inherited descriptor let output redirection survive exec?
3. Why are a zombie and a task in `D` different troubleshooting problems?
