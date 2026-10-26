# 1. How a Linux system fits together

[Contents](../README.md) | [Next: shell](02-shell.md)

Linux is the kernel at the center of a larger operating system. It schedules work on the CPU, manages memory, and mediates access to devices. A distribution adds the programs, libraries, package manager and defaults people use to operate that kernel. Debian, Fedora and Ubuntu are distributions; Linux is the kernel they use.

This distinction matters when you inspect a machine. The kernel reports its own name and release. The distribution publishes separate release information. In a container, that information usually describes the container's user-space files, while the kernel is shared with the host.

## Inspect the running environment

`uname` asks the running kernel for identifying details:

```bash
uname -srm
```

The options request the kernel name (`-s`), release (`-r`) and machine hardware name (`-m`). A typical result might resemble:

```text
Linux 6.8.0-xx-generic x86_64
```

The exact release and architecture differ. This output identifies the running kernel, not every kernel installed on disk, whether updates are available, or the physical machine model.

Distribution information lives in `/etc/os-release`:

```bash
cat /etc/os-release
```

`cat` prints the named file. Look for `PRETTY_NAME`, `ID` and `VERSION_ID`; distributions may add their own fields. Treat these as data, not as commands to run. The file describes the user space visible in this environment. The format and fallback rules are documented by the [os-release specification](https://www.freedesktop.org/software/systemd/man/latest/os-release.html).

## Where programs fit

Most everyday commands are user-space programs. The shell reads your input and either handles it itself or starts another program. Those programs request kernel services through system calls. The kernel enforces boundaries between processes and controls access to hardware.

A simplified request path looks like this:

```text
person -> shell -> program -> kernel -> device or filesystem
```

This is a teaching model, not a complete description of every request. Programs can use libraries, communicate with other services, and make many kernel requests before producing output.

## The directories you will encounter

The directory tree combines persistent files, temporary data and kernel-provided views. These are common conventions, not a promise that every distribution lays out files identically:

- `/etc` holds system-wide configuration. Reading it is different from changing it.
- `/home` usually contains ordinary users' home directories; `/root` is commonly the administrator account's home.
- `/usr` contains much of the installed user-space software and shared data. On many modern distributions, `/bin` and `/sbin` are links into `/usr`.
- `/var` holds changing data such as logs, package records and application state.
- `/tmp` holds temporary files. Do not assume they survive reboot or scheduled cleanup.
- `/run` holds runtime state for the current boot.
- `/dev` exposes device interfaces; `/proc` and `/sys` expose kernel information and controls rather than ordinary stored documents.

Do not edit a file under `/proc` or `/sys` merely because it looks like text: writing to some entries changes kernel or device behavior. Later chapters distinguish inspection from configuration.

## Read command results carefully

A command produces more than printed text. It also returns an exit status to the shell. Conventionally, `0` means success and a nonzero value reports some kind of failure. A successful identity command only means it answered the identity question; it does not prove the machine is healthy or secure.

```bash
printf 'shell=%s\n' "$SHELL"
```

`printf` formats and prints its arguments. `\n` starts a new line; `$SHELL` is an environment variable that often names the configured login shell. It may not tell you which shell is currently interpreting commands. Bash sets `$BASH_VERSION` when the current shell is Bash:

```bash
printf 'bash=%s\n' "${BASH_VERSION:-not Bash}"
```

The `${name:-fallback}` form substitutes the fallback when the variable is unset or empty. The command only prints values; it changes no configuration.

## Common confusion

- `uname -r` is the running kernel release, not the distribution release.
- `/etc/os-release` identifies the environment's user space. In a container it need not identify the host distribution.
- A kernel version alone does not prove that security updates are installed.
- `$SHELL` can name your login shell even when another shell started the current session.

## Further reading

- [Linux kernel documentation](https://docs.kernel.org/)
- [os-release specification](https://www.freedesktop.org/software/systemd/man/latest/os-release.html)
- [GNU coreutils: uname](https://www.gnu.org/software/coreutils/manual/html_node/uname-invocation.html)
- [Linux man-pages: file-hierarchy(7)](https://man7.org/linux/man-pages/man7/file-hierarchy.7.html)
