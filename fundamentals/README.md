# Learn Linux by using it

Use this guide at a terminal. Each chapter shows a task, the commands to run,
what to look for and a small exercise. The examples share fictional practice
files so you can verify results without touching a real service.

## Start here

From this repository's root, review and source the setup script:

```bash
source fundamentals/labs/setup.sh
printf '%s\n' "$LINUX_LAB"
```

It creates a new private temporary directory and exports `LINUX_LAB` for this
shell. It does not install software, modify existing application files or delete
previous practice directories. Open a separate Bash terminal for experiments.
Use a non-root Linux VM or a container you control. GNU utilities are assumed;
BusyBox/macOS options can differ. Minimal containers may lack tools and manuals.

Run each section's setup before its examples. Do not concatenate a whole chapter
into a script: some examples deliberately return nonzero, remain interactive or
require a separate terminal. Commands using `sudo`, package installation or
service changes are clearly marked and are not part of the executed lab tests.

## Everyday command-line work

- [1. Terminal basics](01-how-linux-works.md): `uname`, `pwd`, `ls`, `cd`, `type`, `help`, `man`.
- [2. Files, paths and archives](02-filesystem-and-paths.md): `mkdir`, `touch`, `cp`, `mv`, `find`, `ln`, `tar`, `diff`.
- [3. Logs and text pipelines](03-shell-and-text.md): `grep`, `awk`, `cut`, `sed`, `sort`, `uniq`, `wc` and redirection.
- [4. Users and permissions](04-users-and-access.md): `id`, `getent`, `stat`, `chmod`, `umask`, `namei`.

## Investigate a running machine

- [5. Processes and jobs](05-processes-and-signals.md): `ps`, `pgrep`, `jobs`, `wait`, signals and `/proc`.
- [6. CPU and memory](06-memory-and-cpu.md): `uptime`, `free`, `top`, `vmstat`, process memory and pressure.
- [7. Disk usage and filesystems](07-storage-and-filesystems.md): `df`, `du`, `findmnt`, `lsblk`, sparse files and deleted-open files.
- [8. Services and logs](08-boot-services-and-logs.md): `systemctl`, `journalctl`, plain log files and schedules.

## Work with software, networks and limits

- [9. Software packages](09-packages-and-software.md): `apt-cache`, `dpkg-query`, RPM/DNF alternatives and library inspection.
- [10. Networking](10-networking.md): `ip`, `getent`, `dig`, `ss`, `curl` and a loopback HTTP lab.
- [11. Security and isolation](11-isolation-and-security.md): inspect credentials, permissions, namespaces, capabilities and limits.
- [12. Debugging tools](12-performance-and-debugging.md): choose between `ps`, `vmstat`, `pidstat`, `iostat`, `strace` and other evidence.
- [13. Practice investigations](13-practice-labs.md): reproduce misleading pipeline success, a deleted-open file and an HTTP error.

If Linux is new to you, finish chapters 1–4 before jumping to a debugging command
list. For interviews, practice choosing the next command and interpreting its
output, not just remembering a flag. For daily work, use the chapter matching
the task in front of you.

## Keep these nearby

- [Command reference](../commands/commands.md) for a quick lookup.
- [Shell scripting guide](../shell-scripting/scripting.md) for functions and script patterns.
- [Directory-permission lab](permissions.md), [disk checklist](../troubleshooting/disk-space.md),
  [process checklist](../troubleshooting/processes-and-memory.md) and
  [network checklist](../troubleshooting/network-connectivity.md) for shorter references.
- [Verification notes](../VERIFICATION.md) for executed checks and environment limits.

Some commands reveal private paths, arguments or logs. Check output before
sharing. Do not run installation, service changes, tracing, mount operations or
network capture against production just to finish a lesson. Leave an unavailable
command untested rather than disabling protections or guessing its output.

## More command-line practice

- [The Art of Command Line](https://github.com/jlevy/the-art-of-command-line): task-oriented command-line tips.
- [Linux Command Line Computing](https://github.com/learnbyexample/cli-computing): worked examples and exercises.
- [tldr pages](https://github.com/tldr-pages/tldr): short command examples for quick lookup.

These are additional learning resources, not substitutes for checking the local
manual and current software behavior. The fixtures and explanations here are
separate examples; each linked project retains its own license and attribution.

[Back to Linux Helpbook](../README.md)
