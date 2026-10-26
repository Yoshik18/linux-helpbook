# Linux fundamentals: a path from first commands to production debugging

Linux becomes easier to understand when you can connect the pieces: a shell
starts a process, the process asks the kernel for a file or socket, permissions
and resource limits shape what happens, and tools expose part of that state.
This guide follows those connections rather than asking you to memorize commands.

It is written for students, junior DevOps/SRE engineers and developers moving
into infrastructure. You can start without server experience. You should be
comfortable reading small code examples and willing to try them in a lab.

## How to use the guide

Read the first four chapters in order if Linux is new to you. After that, follow
the path or choose the part you need. Each chapter explains the mechanism, shows
what to inspect and ends with questions you should be able to reason through.
You do not need to finish every chapter before doing useful work.

### Stage 1: build the mental model

- [1. How Linux works](01-how-linux-works.md): kernel, user space, distributions, terminals and system calls.
- [2. Filesystems and paths](02-filesystem-and-paths.md): directories, links, inodes, mounts and open files.
- [3. The shell and text](03-shell-and-text.md): quoting, expansion, input/output, pipes and exit status.
- [4. Users and access](04-users-and-access.md): identities, groups, modes, umask and privilege boundaries.

**You are ready to move on when:** you can explain who runs a command, which
program the shell starts, how it finds a file and why an operation can be denied.

### Stage 2: understand a running machine

- [5. Processes and signals](05-processes-and-signals.md): process trees, threads, lifecycle, signals and job control.
- [6. Memory and CPU](06-memory-and-cpu.md): virtual memory, resident pages, caches, scheduling, load and pressure.
- [7. Storage and filesystems](07-storage-and-filesystems.md): devices, partitions, filesystems, allocation and I/O.
- [8. Boot, services and logs](08-boot-services-and-logs.md): startup, PID 1, systemd units and journal investigation.

**You are ready to move on when:** you can follow a service from startup to its
process, describe where its memory and files live, and choose a useful first
observation when it stops responding.

### Stage 3: connect and constrain services

- [9. Packages and software](09-packages-and-software.md): repositories, dependencies, updates, executable lookup and libraries.
- [10. Networking](10-networking.md): interfaces, routing, name resolution, sockets and application connections.
- [11. Isolation and security](11-isolation-and-security.md): namespaces, cgroups, capabilities, seccomp and access policy.
- [12. Performance and debugging](12-performance-and-debugging.md): hypotheses, measurements, tracing and safe investigation.

**You are ready to move on when:** you can separate a name-resolution error from a
connection error, explain why a container is not a VM, and identify what evidence
would support or disprove your first debugging hypothesis.

### Stage 4: put it together

- [13. Practice investigations](13-practice-labs.md): explain shell failures, inspect a deleted open file and investigate a local HTTP service.

Try to describe your observations before reading the explanation. A good answer
includes what the observation proves, what it does not prove and the next check.
This is more useful for interviews than reciting a command from memory.

## Prepare a safe environment

Use a Linux VM or disposable container you control, as an ordinary user. A
container is enough for shell, file and many process labs. It may not have a
working systemd journal, a full boot sequence, a package manager or permission to
inspect host processes and network state. Use a disposable VM when those matter.

Examples assume Bash and common GNU utilities unless a chapter states otherwise.
Advanced Bash features in the separate scripting guide need Bash 4 or later.
Python labs need Python 3. Minimal images may lack `ip`, `ss`, `dig`, `lsof`,
`vmstat`, `strace` or manual pages. Check availability rather than assuming a
missing command means Linux is broken.

```bash
uname -sr
bash --version
command -v python3
```

A path, interface name, PID, unit name or address in an example is not a target on
your machine. Substitute your own only after inspecting it. Do not run package
upgrades, change mounts, alter real service permissions or trace production
processes as a side effect of following this guide.

Lab files belong in a temporary directory. `mktemp` failure must stop a script,
not leave it operating on an empty path. In interactive examples, `exit 1` also
exits the current shell if creation fails; use a separate lab shell if needed.
Python's temporary-directory helpers honor `TMPDIR` when set. Check lab paths
before cleaning up. Never print a whole environment, credential file or private
application log just to debug one value.

## Keep these references nearby

- [Command reference](../commands/commands.md) for quick lookups.
- [Bash scripting guide](../shell-scripting/scripting.md) for automation patterns.
- [File-permission lab](permissions.md) for directory access and safe mode changes.
- [Disk-space investigation](../troubleshooting/disk-space.md),
  [processes and memory](../troubleshooting/processes-and-memory.md), and
  [network connectivity](../troubleshooting/network-connectivity.md) for shorter incident-oriented checklists.

The chapters link to primary documentation. Software versions, distribution
choices, security policy and container restrictions affect results. Examples
label environment-dependent or untested paths rather than promising universal
behavior. Syntax checks are useful, but they are not execution tests.

[Back to Linux Helpbook](../README.md)
