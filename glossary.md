# Linux glossary

Each term has one definition here. Lessons link to the relevant heading on first use rather than defining it again. Entries grow with the reviewed lessons, not with a list of future topics.

### Kernel

The core software that manages a computer's processors, memory and devices, and handles requests from running programs. Linux is a kernel. See the first lesson, `linux-01-01`, in [ROADMAP.md](ROADMAP.md).

### Terminal

The interface that displays text from programs and accepts typed input. It is not itself the shell that interprets commands.

### Shell

A program that reads commands and carries them out, either itself or by starting other programs. This course uses Bash for its verified examples.

### Command

An instruction given to a shell. It can name a program or a shell-provided operation and include arguments.

### Option

An argument that changes a command's behavior. Many Linux commands use a leading hyphen for options, but the available options depend on the command.

### Argument

A value passed to a command, such as an option or a file path. The command determines what each argument means.

### Architecture

The processor design a system's software targets. An architecture name reported by the running kernel does not describe every hardware feature or installed program.

### Distribution

A complete operating-system collection built around the Linux kernel, with selected programs, package tools and release policies. Debian and Ubuntu are distributions; their release numbers are separate from the kernel's.

### Virtual machine

A software-defined computer that runs a guest operating system using virtual hardware. KVM is a Linux-based virtualization technology used to run virtual machines.

### Container

An environment that isolates selected resources for programs while sharing a kernel with its host. A container's installed software can differ from its host's software.

### Exit status

A number a command returns when it finishes. Zero normally means success; a nonzero number normally indicates failure or another command-specific condition. It is separate from the text a command prints.

### Standard output

The usual channel through which a command writes its results, commonly displayed in the terminal.

### Standard error

A separate output channel used for diagnostics and error messages, also commonly displayed in the terminal.

### Working directory

The directory a running program uses as the starting point for relative file paths.

## Further reading

- [GNU Bash: What is a shell?](https://www.gnu.org/software/bash/manual/html_node/What-is-a-shell_003f.html)
- [Linux kernel overview](https://docs.kernel.org/admin-guide/README.html)
- [Linux kernel KVM documentation](https://docs.kernel.org/virt/kvm/index.html)
