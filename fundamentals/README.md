# Linux fundamentals: a practical learning path

These chapters teach Linux by connecting a task to the model behind it. Start at a terminal in an unprivileged Linux VM or a container you control. Examples assume Bash and mostly GNU utilities; options can differ on BusyBox or other systems. Read each command as an action: identify its operands, what it reads or changes, and how to interpret output or status.

## Set up the shared practice files

From this repository's root, inspect and source the setup script:

```bash
source fundamentals/labs/setup.sh
printf '%s\n' "$LINUX_LAB"
ls -la "$LINUX_LAB"
```

`source` runs in the current shell, retaining the exported `LINUX_LAB` path for later examples. The script creates a new private temporary directory with fictional notes, configuration, and logs. It does not install software or modify existing application files; it honors `TMPDIR`. Each setup run makes a fresh directory. Source it again in another terminal before using chapter examples.

Run examples a section at a time. Do not paste a whole chapter into a script: a few examples intentionally return nonzero, wait for input, or need a separate terminal. Commands requiring `sudo`, installation, or service changes are not part of these unprivileged labs. If a tool is absent, check its local manual/package source rather than assuming its output.

## Learning path

### Foundations: orient, manage, investigate

1. [Understand Linux and the command line](01-how-linux-works.md) — kernel versus distribution/user space, command lookup and lifecycle, environment, navigation, help.
2. [Understand the filesystem and paths](02-filesystem-and-paths.md) — absolute and relative paths, file operations, links, search, archives.
3. [Run shell commands and process text](03-shell-and-text.md) — arguments, quoting, globbing, streams, redirection, pipelines, status, text filters.
4. [Understand users, groups, and access](04-users-and-access.md) — identities, mode bits, directory traversal, umask, ACLs.

### Investigate a running machine

- **5.** [Processes and jobs](05-processes-and-signals.md) — `ps`, `pgrep`, jobs, `wait`, signals, `/proc`.
- **6.** [CPU and memory](06-memory-and-cpu.md) — `uptime`, `free`, `top`, `vmstat`, process memory and pressure.
- **7.** [Storage and filesystems](07-storage-and-filesystems.md) — `df`, `du`, `findmnt`, `lsblk`, sparse files, deleted-open files.
- **8.** [Boot, services, and logs](08-boot-services-and-logs.md) — `systemctl`, `journalctl`, log files, schedules.

### Work with software, networks, and limits

- **9.** [Packages and software](09-packages-and-software.md) — `apt-cache`, `dpkg-query`, RPM/DNF alternatives, libraries.
- **10.** [Networking](10-networking.md) — `ip`, `getent`, `dig`, `ss`, `curl`, loopback HTTP lab.
- **11.** [Isolation and security](11-isolation-and-security.md) — credentials, permissions, namespaces, capabilities, limits.
- **12.** [Performance and debugging](12-performance-and-debugging.md) — choose evidence from `ps`, `vmstat`, `pidstat`, `iostat`, `strace`, and related tools.
- **13.** [Practice investigations](13-practice-labs.md) — misleading pipeline success, deleted-open files, HTTP errors.

## Use a chapter as a reference

Each chapter groups commands by task rather than alphabetically. Follow the examples in order when they share fixture state. For quick lookup, use the [command reference](../commands/commands.md); for reusable functions and script patterns, see the [shell scripting guide](../shell-scripting/scripting.md). The [directory-permission lab](permissions.md) expands the chapter 4 path-traversal model.

When a result surprises you, check the command's manual and the actual machine state. Compare fields and status codes, not copied sample versions. Some commands disclose private paths, arguments, or logs; review output before sharing. Do not run installation, service changes, tracing, mount operations, or network capture on production just to complete a lesson.

## Further command-line practice

- [The Art of Command Line](https://github.com/jlevy/the-art-of-command-line) — task-oriented command-line tips.
- [Linux Command Line Computing](https://github.com/learnbyexample/cli-computing) — worked examples and exercises.
- [tldr pages](https://github.com/tldr-pages/tldr) — concise examples for quick lookup.

These supplement, but do not replace, local manuals and checking behavior on your system. The examples here are independently written; linked projects retain their own content and licenses.

[Verification notes](../VERIFICATION.md) · [Back to Linux Helpbook](../README.md)
