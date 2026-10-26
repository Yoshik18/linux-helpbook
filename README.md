# Linux Helpbook

Linux command references and practical notes for students, junior DevOps/SRE
engineers and developers working with Linux servers. Use the references for a
quick lookup, or follow the path below to understand what to check and why.

## Start here

1. [Linux commands](commands/commands.md): navigation, files, processes and system inspection.
2. [File and directory permissions](fundamentals/permissions.md): understand access before changing modes.
3. [Shell scripting](shell-scripting/scripting.md): Bash constructs, arguments, error handling and reusable patterns.
4. [Disk-space troubleshooting](troubleshooting/disk-space.md): capacity, inodes, hidden files and deleted open files.
5. [Processes and memory](troubleshooting/processes-and-memory.md): distinguish busy, idle and waiting processes.
6. [Network connectivity](troubleshooting/network-connectivity.md): separate DNS, listening sockets, TCP, TLS and HTTP.

[Vim cheatsheet](vim/vim.md) is a separate lookup reference. You do not need to
learn every Vim command before working through the Linux notes.

## Before running examples

- Use a Linux lab, VM or container you control. The notes assume Bash and GNU
  utilities unless stated otherwise. Some features need Bash 4 or later.
- Tools such as `ss`, `dig`, `lsof`, `iostat` and `htop` may need packages. Package
  names and installation commands depend on the distribution.
- Systemd journal commands need a host with a working systemd journal; many
  containers do not have one. Process and network visibility can also be limited.
- Read-only checks are the starting point. Permission changes, signals, file
  removal, mounts and service changes need separate care. Do not try them against
  production infrastructure without authorization.
- Read the expected result and limitations beside each example. Redact private
  paths, addresses, credentials and application data before sharing output.

## How these notes are checked

[Verification notes](VERIFICATION.md) record the checks run for this update and
what remains untested. A command parsing successfully does not prove it is safe
or correct for your system. Sources are linked close to the relevant explanation.

For deeper infrastructure explanations, see [Uptime Engineer](https://uptime.engineer).
