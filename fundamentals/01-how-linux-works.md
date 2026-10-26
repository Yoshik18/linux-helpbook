# 1. How Linux works

[Previous: learning path](README.md) · [Index](README.md) · [Next: filesystem and paths](02-filesystem-and-paths.md)

A useful first model is a set of boundaries: hardware, the kernel, and programs running in userspace. When a command fails, identifying the boundary involved is more helpful than treating “Linux” as one large program.

## Kernel, userspace, and distribution

The **kernel** manages CPU scheduling, memory, devices, and access to shared resources. A running application does not normally program a storage controller itself. It requests operations through the kernel, which checks permissions and coordinates access with other processes.

**Userspace** contains applications and supporting software: shells, editors, libraries, package managers, and service managers. Userspace does not mean “unprivileged.” An administrator's shell is still a userspace program, even when it can request operations that an ordinary account cannot.

A **distribution** assembles a kernel with userspace tools, packages, installation choices, update policies, and defaults. Debian and Fedora can run related kernel versions while offering different package managers and software versions. Updating a shell package is not the same operation as booting a new kernel. A kernel release therefore does not identify a complete distribution.

This distinction matters in containers too. A normal Linux container shares its host's kernel but has its own userspace view. Its distribution identification can differ from the host's. A virtual machine, in contrast, normally boots its own kernel. Do not infer where a package came from just by reading the kernel version.

## Terminal and shell are different programs

A **terminal** supplies an input/output interface. A desktop terminal emulator draws text and sends keystrokes; an SSH session can provide a remote terminal. Neither is inherently Bash.

A **shell** interprets commands. Bash, for example, reads command text, performs expansions and redirections, and runs builtins or external programs. [Bash manual](https://man7.org/linux/man-pages/man1/bash.1.html) Changing the terminal's font does not change shell syntax. A script can run without a terminal, and many server programs run without a shell supervising each request.

Consider typing `cat /etc/os-release`. The shell separates the command and its argument, finds the executable, and arranges for it to run. The program opens the file, reads bytes, and writes output. Some operations cross into the kernel; parsing the command line and formatting the text happen in userspace.

The interface for requesting kernel operations is a **system call**, such as opening a file or creating a process. Applications commonly use library wrappers rather than issuing system calls directly. [syscalls(2)](https://man7.org/linux/man-pages/man2/syscalls.2.html) A library function is not automatically a system call: it may do its work entirely in userspace, or make several kernel requests.

## Lab: identify three separate things

Prerequisites: a Linux environment, a shell, and the usual `uname`, `grep`, and `id` utilities. This read-only block needs no administrator privileges. It prints selected system identifiers and numeric account IDs, not passwords, tokens, or a complete environment.

```bash
uname -s
uname -r
uname -m
if [ -r /etc/os-release ]; then
    grep -E '^(NAME|ID|VERSION_ID)=' /etc/os-release
elif [ -r /usr/lib/os-release ]; then
    grep -E '^(NAME|ID|VERSION_ID)=' /usr/lib/os-release
else
    printf 'No readable os-release file found\n'
fi
id -u
id -g
```

Observe three different kinds of evidence. `uname -s`, `-r`, and `-m` report the kernel name, release, and machine architecture respectively. [uname(1)](https://man7.org/linux/man-pages/man1/uname.1.html) The release string may include distribution-specific packaging text; it is not a userspace package inventory.

The selected `os-release` fields describe the operating system's userspace identity. The specification gives `/etc/os-release` precedence, with `/usr/lib/os-release` as the fallback. [os-release](https://www.freedesktop.org/software/systemd/man/latest/os-release.html) A minimal image might omit it. The two `id` commands show the effective user and group IDs of the command's execution context, not a history of who logged in.

If a command is missing, that establishes a userspace tooling gap, not a broken kernel. If you are connected remotely, the commands describe that remote environment. Record observations locally; even non-secret machine details need not be published.

**Validation:** this lab block has not been run. Output values vary; no container/VM comparison or kernel tracing was performed.

## Check your understanding

1. Two machines report the same kernel release but use different package managers. Is that contradictory? Explain which layer supplies each.
2. Can a process make system calls without an interactive shell? Where does a service fit in the model?
3. Why might `os-release` inside a container name a different distribution from the host while `uname -r` agrees?
