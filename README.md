# Linux Helpbook

A guided set of Linux notes for students and junior engineers learning to work
with servers. It covers the ideas behind the commands, then shows how to inspect
and change things safely in a lab. It is not an LPIC syllabus or a wall of flags.

## Learning path

Start with [Linux fundamentals](fundamentals/README.md). It begins with the kernel,
shell and files, then builds through permissions, processes, resources, services,
packages and networking. Each topic links to a separate quick reference or
troubleshooting note when you want more detail.

You can also go straight to a task:

- [Look up a command](commands/commands.md): what it is for, useful options and links to worked lessons.
- [Understand file permissions](fundamentals/permissions.md): owner/group/other, directory search and safe changes.
- [Write Bash scripts](shell-scripting/scripting.md): shell behavior, quoting, arguments, functions and error handling.
- [Investigate disk space](troubleshooting/disk-space.md): capacity, inodes and why `df` and `du` can disagree.
- [Investigate slow processes](troubleshooting/processes-and-memory.md): CPU, memory, waits and process state.
- [Trace a network failure](troubleshooting/network-connectivity.md): DNS, routes, listening sockets, TCP, TLS and HTTP.
- [Use Vim](vim/vim.md): a small editor reference for reading and editing text.

## How to use the examples

The guides explain what a command reads or changes, why its options matter, and
what the output can and cannot tell you. Some outputs vary by distribution,
version, permissions, workload and host configuration. Where a command is
interactive or mutates state, the guide says so.

A few lessons use fictional sample files. From the repository root, you can
create your own practice directory with:

```bash
source fundamentals/labs/setup.sh
printf '%s\n' "$LINUX_LAB"
```

The script creates new files in a private temporary directory and sets
`LINUX_LAB` for this shell. It does not install software or change existing
application files. Run it again in another terminal if needed. Examples that
need an optional tool, systemd host, administrator privileges or a second
terminal say so; a missing tool is not evidence that the system is broken.

Unless stated otherwise, commands assume Bash on Linux and common GNU/Linux
utilities. Some minimal containers omit tools and manuals; other Unix systems may
use different options. Run examples on a Linux VM, container or machine you
control. Do not experiment with service changes, deletion, mounts, package
installation or signals on production systems.

## Find your level

- **New to Linux:** source the practice files described above. Then read fundamentals in order, pausing to run commands and explain results in your own words. The [fundamentals index](fundamentals/README.md) has the setup steps.
- **Know the basics:** use the command reference, then pick a troubleshooting guide and follow its checks from the affected machine.
- **Preparing for interviews:** practice explaining why you chose a command, what its result proves, and what you would check next.

## Sources and verification

Each technical lesson links to relevant manuals or upstream documentation. The
[verification notes](VERIFICATION.md) state what was actually checked and what
was not. Syntax parsing, a successful local lab and a command that has only been
read in its manual are different kinds of evidence.

The named [Linux Tutorial](https://github.com/samankhalife/linux-Tutorial) is
another broad Linux learning resource. This repository uses its visible topic
organization as inspiration, but its explanations and examples here are
independently written.
