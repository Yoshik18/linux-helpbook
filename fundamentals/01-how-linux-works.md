# 1. Understand the Linux system and your command line

Linux is the kernel: it schedules processes, manages memory and devices, and enforces access controls. A distribution combines that kernel with user-space programs, libraries, package tools, defaults, and release metadata. The shell is one user-space program; it reads commands and starts other programs. This distinction helps explain why a container may identify as Debian but use its host's kernel.

## Identify the environment

```bash
uname -sr
uname -m
cat /etc/os-release
whoami
id
printf 'shell=%s version=%s\n' "$SHELL" "$BASH_VERSION"
```

`uname -s` is the kernel name, `-r` its release; `-m` reports machine architecture. `/etc/os-release` describes the installed distribution's user space, not necessarily the host kernel. `cat` writes that text to standard output. `whoami` prints the effective username; `id` shows effective numeric/user identity and groups. `$SHELL` is often the configured login shell, while `$BASH_VERSION` is set only in Bash—an empty value can mean this is another shell. Output varies by machine; do not treat versions as expected answers.

## A command's lifecycle

At a prompt, the shell parses words and operators, expands variables and patterns, then runs a builtin/function or searches `PATH` for an executable. It supplies arguments and environment to the process, waits when appropriate, and records an exit status. `cd` must be a shell builtin because a child process cannot change its parent's current directory.

```bash
type cd
type ls
command -v bash
command -v not-a-real-command
printf 'status=%s\n' "$?"
```

`type` reports how this shell resolves a name (builtin, alias, function, or executable). `command -v` prints the resolved command path/name when found; the deliberately absent name prints nothing and returns nonzero. `$?` is the previous command's status; zero conventionally means success. Save it immediately because the next command replaces it. A missing command is not evidence of a broken subsystem.

## Navigate and inspect

```bash
pwd
ls
ls -lah
cd /etc
pwd
cd -
pwd
```

`pwd` prints the working directory. `ls -l` shows a detailed listing, `-a` includes dot-names, and `-h` makes sizes human-readable (with `-l`). `cd /etc` changes this shell's directory; an absolute path begins at `/`. `cd -` returns to the previous directory and prints it. `cd` without an operand goes to your home directory. A relative path is interpreted from the current directory.

## Get help at the right layer

```bash
help cd
help printf
ls --help
man 1 ls
man 5 passwd
```

Bash `help` covers builtins; many external programs implement `--help`. `man 1 ls` is the user-command manual section; `man 5 passwd` describes a file format, not the `passwd` program. In the common `less` viewer, `/word` searches, `n` advances to another match, and `q` exits. Minimal systems may omit manuals or a pager.

## Prepare the shared practice files

From the repository root:

```bash
source fundamentals/labs/setup.sh
printf '%s\n' "$LINUX_LAB"
ls -la "$LINUX_LAB"
```

`source` runs the setup in this shell so its exported `LINUX_LAB` variable remains available. The script creates a new private temporary fixture directory; it does not install software or modify application files. Each run creates a different directory and honors `TMPDIR`. Run it again in a new terminal before later chapter examples.

**Try it:** Determine whether `printf` is a builtin, locate Bash, and list hidden fixture entries. The hidden `.practice` name is omitted unless `ls` receives `-a`.

```bash
type printf
command -v bash
ls -la "$LINUX_LAB"
```

[Manual: Bash](https://man7.org/linux/man-pages/man1/bash.1.html) · [uname](https://man7.org/linux/man-pages/man1/uname.1.html) · [Guide index](README.md) · [Next: filesystem and paths](02-filesystem-and-paths.md)
