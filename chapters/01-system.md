# 1. How a Linux system fits together

[Contents](../README.md) | [Next: shell](02-shell.md)

You have opened a terminal and found instructions for installing a program. One page says to follow the Ubuntu steps; another mentions Fedora. Both call themselves Linux guides. Before trying either set of instructions, you need to answer a smaller question: what system are you actually using?

That question has several parts. The name of the installed operating system is one part. The software that manages the hardware is another. The program reading your typed commands is a third. These parts work together, but they do not have the same name or version number.

This chapter builds a small description of your environment, one piece at a time. The commands only read information and print it. They do not install software, change settings, or require administrator access. By the end, you should know what each answer tells you, where it came from, and what it leaves unanswered.

## In this chapter

- [Start with the terminal](#start-with-the-terminal)
- [Meet the part that manages the hardware](#meet-the-part-that-manages-the-hardware)
- [Find the distribution name](#find-the-distribution-name)
- [Read a mistake without making it worse](#read-a-mistake-without-making-it-worse)
- [See how a command reaches the system](#see-how-a-command-reaches-the-system)
- [Get your bearings in the directory tree](#get-your-bearings-in-the-directory-tree)
- [Understand why containers give mixed-looking answers](#understand-why-containers-give-mixed-looking-answers)
- [Distinguish the shell from the rest of Linux](#distinguish-the-shell-from-the-rest-of-linux)
- [Put the answers together](#put-the-answers-together)
- [Further reading](#further-reading)

## Start with the terminal

A terminal is the window, or text-only screen, where you type commands and read replies. Inside it, a program waits for your instructions. That program is called a **shell**. You will learn how to work with it in the next chapter. For now, enter one command at a time and press Enter after each one.

The terminal usually displays some text before the place where you type. This is the **prompt**. It might contain an account name, a directory name, or a `$` character. The prompt is not part of the command. The command blocks in this handbook omit it so that you can copy just what you need.

Text under a command is its output, not another instruction to type. Where an answer depends on the machine, this chapter labels the example accordingly. Do not expect your version numbers to match a book or a web page.

## Meet the part that manages the hardware

Several programs may need the processor, memory, or a disk at the same time. Something has to decide when each program runs and whether it may read or change a particular resource. The central software doing this work is the **kernel**.

The kernel also provides a controlled way for programs to use devices. A text editor does not normally decide for itself how to move data to a particular disk. It asks the operating system to save a file. The kernel and the device-support code it uses handle the lower-level work.

Ask for the running kernel's name:

```bash
uname -s
```

On Linux, the answer is:

```text
Linux
```

`uname` prints information about the running system. The space separates the command name from its option. An **option** adjusts what a command does; here, `-s` asks specifically for the kernel name. The `-` is part of the option and must be typed.

Now ask for the kernel release:

```bash
uname -r
```

For example, this was the observed output in the local environment used to check this chapter:

```text
5.15.0-198-generic
```

Your answer may be different. The `-r` option selects the release identifier of the kernel that is running now. It does not list all kernel versions installed on the disk. Installing an updated kernel does not necessarily change this answer immediately, because the old kernel can remain running until the machine starts again.

One more question helps when choosing software downloads:

```bash
uname -m
```

The observed answer in the same environment was:

```text
aarch64
```

`aarch64` names a 64-bit ARM architecture. Another common answer is `x86_64`, used on many Intel and AMD computers. An **architecture** is a family of machine instructions a processor can understand. Software compiled for one architecture will not necessarily run on another without additional support.

This is a machine hardware name reported by the running environment, not the computer's brand or model. For an actual installation, use your distribution's download and package instructions too: the architecture label alone does not settle every compatibility question.

Once the separate answers make sense, you can request all three together:

```bash
uname -srm
```

For `uname`, these short options can be grouped after one hyphen. This has the same effect as asking for `-s`, `-r`, and `-m` separately. The observed combined result was:

```text
Linux 5.15.0-198-generic aarch64
```

Read it as three answers: kernel name, kernel release, and machine architecture. There is still no Ubuntu, Debian, or Fedora version in it. That information belongs to a different part of the system.

## Find the distribution name

A usable computer needs more than a kernel. It needs programs for reading files, starting other programs, installing software, and many other jobs. It also needs shared supporting code, called **libraries**, that programs can reuse instead of each implementing the same work themselves.

A **distribution** brings these pieces together. It supplies a kernel, programs, libraries, installation tools, and choices about how the system is arranged. Debian, Ubuntu, and Fedora are distributions. They use Linux kernels, but they do not all supply the same software versions or the same commands for installing software.

That is why an instruction can be correct for one Linux distribution and unsuitable for another.

Most modern distributions provide an identification file at `/etc/os-release`. Read it with:

```bash
cat /etc/os-release
```

`cat` displays the contents of the file named after it. Despite its short name, it does not open an editor or change the file.

The name `/etc/os-release` is a **path**, an address for a file. The first `/` means to start at the top of the directory tree. `etc` is a directory, a place that contains files or other directories. The next `/` separates that directory name from the file name `os-release`. Because the path starts at the top, this command does not depend on which directory you are currently working in.

Here are selected lines from the observed output in the checking environment. The complete file contained additional lines:

```text
PRETTY_NAME="Debian GNU/Linux 13 (trixie)"
NAME="Debian GNU/Linux"
VERSION_ID="13"
ID=debian
```

Each line gives a field name on the left of `=` and its value on the right.

- `PRETTY_NAME` is a readable label intended for people. It is usually the most useful line to include when asking for help.
- `NAME` names the operating system without a release number.
- `VERSION_ID` identifies the distribution release, when the distribution provides one. Some distributions do not have a fixed release number.
- `ID` is a short identifier intended for software to read, such as `debian` or `fedora`.

The quotation marks around some values belong to the file's format. They allow a value to contain spaces. You do not need to remove the quotes or type these lines back into the terminal. You are reading a description, not a set of instructions.

Compare the two release answers collected so far. `5.15.0-198-generic` identifies a running kernel; `13` identifies this Debian environment's distribution release. They measure different things. There is no reason for their numbers to match.

If `/etc/os-release` does not exist, the standard fallback location is:

```bash
cat /usr/lib/os-release
```

Use this fallback when the first file is missing, not to combine two competing descriptions. The specification gives `/etc/os-release` priority. Older or unusual systems may provide neither location. A missing file is a reason to look at that system's documentation, not evidence that the kernel has stopped working.

## Read a mistake without making it worse

A one-character mistake is enough to change a file name. Suppose you leave off the final `e`:

```bash
cat /etc/os-releas
```

In the checked environment, this produced:

```text
cat: /etc/os-releas: No such file or directory
```

The message tells you which command complained, which path it tried, and why it could not read it. In this case the problem is the spelling, not a lack of administrator access. Adding an administrative command in front would not repair the missing letter.

A command also reports a small number to the shell when it finishes. This is its **exit status**. Zero conventionally means success; a nonzero value means that something failed or that a condition was not met. The precise meaning depends on the command.

To see the status of the failed command, run this immediately afterward:

```bash
printf 'status=%s\n' "$?"
```

The observed result after the misspelled path was:

```text
status=1
```

There are several small pieces in this command:

- `printf` prints text using a specified format.
- The single-quoted text `'status=%s\n'` is that format. Single quotes keep the shell from interpreting its contents.
- `status=` is ordinary text to print. `%s` is where `printf` inserts a supplied string.
- `\n` tells `printf` to end the output line.
- `$?` means the exit status of the previous command. The surrounding double quotes keep its value together as one argument to `printf`.

You do not need to memorize this syntax yet. Its purpose here is to make the otherwise invisible success-or-failure number visible.

Correct the spelling and then check again:

```bash
cat /etc/os-release
printf 'status=%s\n' "$?"
```

Run the two lines in order. The first displays the identification file; the second displays `status=0` if `cat` read it successfully. In the checked environment it did.

The timing matters. `$?` refers to the command that just finished, not the last command you remember caring about. If you run something else between the failed `cat` and the status check, you will be checking that other command instead.

Also separate “the command succeeded” from “the whole computer is fine.” A zero status here means that `cat` read the file successfully. It says nothing about pending security updates, disk health, or whether a website hosted on the machine is working.

## See how a command reaches the system

When you typed `cat /etc/os-release`, the shell recognized the command name and started the `cat` program with the file path as an argument. An **argument** is a piece of information passed to a command, such as a file name or an option.

The running program then needed access to a file. It requested that access through the kernel, read the available contents, and sent text back toward the terminal. The kernel checks access rules; the program does not gain permission simply because you asked it to read something.

A simplified picture is:

```text
You type a command
        |
        v
The shell starts a program
        |
        v
The program asks the kernel to read a file
        |
        v
The program receives data and prints a result
```

The requests a program makes to the kernel are called **system calls**. Programs often use libraries to make these requests. Some work also involves other running programs. The picture is a starting model, not a promise that every command follows exactly four steps.

Software outside the kernel is often called **user space**. The shell, `cat`, a web browser, and most of the other programs you use belong there. The name does not mean “only programs installed by your personal account.” System services, which do work in the background, also usually run in user space.

A running instance of a program is a **process**. The kernel shares processor time among processes, manages their memory, and enforces access boundaries. Later chapters examine those processes directly. For now, the useful distinction is that the shell reads your instruction, a program does the requested job, and the kernel provides controlled access to the system beneath it.

## Get your bearings in the directory tree

The identification file introduced `/etc`. It sits inside a larger arrangement of directories. Seeing that arrangement helps explain why a settings file and an installed program usually live in different places.

List the names at the top of the tree:

```bash
ls /
```

`ls` lists directory contents. The `/` argument asks it to list the top directory rather than the directory where you happen to be working. This top directory is called the **root directory**.

The exact output and its arrangement vary. The following is a schematic selection of common names, not a transcript from a particular installation:

```text
bin  dev  etc  home  proc  root  run  sys  tmp  usr  var
```

Do not try to memorize the whole tree. Start with the jobs these locations do.

### Settings, personal files, and installed software

`/etc` commonly holds system-wide settings. Reading `/etc/os-release` was a safe way to inspect one file there. It does not follow that changing arbitrary files in `/etc` is harmless: other files control how programs or the whole system behave.

`/home` usually contains ordinary users' personal directories, such as `/home/alex`. Your own home directory is where you generally keep your work. Some systems place home directories elsewhere, so do not assume that example is your actual path.

`/root` is commonly the home directory of the administrator account named `root`. It is not another name for `/`, the root directory of the entire tree. These similar names refer to different things.

`/usr` contains much of the installed software and shared program data. Despite its name, it is not the usual place for personal documents. Programs often live in `/usr/bin`; libraries often live under `/usr/lib` or architecture-specific locations.

On many modern distributions, `/bin` and `/sbin` are links to locations within `/usr`. A **link** can make one path lead to something stored at another path. Finding these names does not necessarily mean you have separate copies of the programs. Directory details vary across distributions.

### Data that changes while the machine runs

`/var` holds changing data such as logs, software installation records, and application state. A log is a record of events; application state is information a program keeps about its ongoing work. “Changing” does not mean disposable. A database stored under `/var` can be essential data.

`/tmp` is for temporary files. Files there can be removed by reboot policies or scheduled cleanup. It is not a suitable place for the only copy of an important document.

`/run` holds information associated with the current running system, such as files that help programs find or coordinate with background services. It is normally recreated for a new boot. Do not treat its files as permanent configuration.

### Devices and views into the running kernel

`/dev` contains interfaces to devices. A program may use one of these paths to communicate with a device rather than read an ordinary document.

`/proc` and `/sys` expose information from the running kernel. Many entries look like text files, but their contents are supplied by the system as you read them, rather than being ordinary documents saved on a disk. Some entries also accept writes that change kernel or device behavior.

This is an important limit to the directory metaphor: a file-shaped interface can be a control, not just stored text. Do not edit something under `/proc`, `/sys`, or `/dev` because it resembles a file you recognize. Later chapters introduce specific read-only inspections and explain any changes separately.

## Understand why containers give mixed-looking answers

Suppose an environment reports Debian in `/etc/os-release`, while `uname -r` reports a kernel release associated with another distribution. Those answers are not necessarily contradictory.

A **container** gives programs a separated view of parts of a system, including files and processes, while using the host's kernel. The **host** is the system providing that kernel. A Debian container can therefore have Debian programs and Debian identification files without running a separate Debian kernel.

Inside that container:

- `cat /etc/os-release` reads the identification file visible inside the container.
- `uname -r` reports the running kernel release made available to it, normally the host's kernel.

The commands are answering different questions about different layers. Do not use the container's distribution name as proof of the host distribution. Equally, do not use a surprising kernel release as proof that the container's identification file is wrong. These two commands alone do not establish whether you are in a container at all.

A **virtual machine** works differently: it presents virtual hardware on which a guest operating system can run its own kernel. Windows Subsystem for Linux has its own arrangements too; WSL 2 uses a Linux kernel in a managed virtual machine. Service management and networking can differ from an ordinary Linux installation. When asking for help, mention a container, virtual machine, or WSL if you know that is what you are using.

## Distinguish the shell from the rest of Linux

You now have a kernel name and a distribution name. The program interpreting your commands has its own identity as well. Bash is a common shell, but it is not the only one, and it is not the Linux kernel.

A shell can handle some commands itself. For example, in Bash, `printf` is normally built into the shell. Other commands, including the `cat` used earlier, normally start a separate program. Both kinds can appear at the same prompt.

You may encounter this command in instructions that try to identify a shell:

```bash
printf 'shell=%s\n' "$SHELL"
```

This uses the same printing format as the exit-status example. The new part is `$SHELL`, which asks the shell to substitute the value stored under the name `SHELL`. A named stored value is a **variable**. Some variables are passed to programs that the shell starts; these are called environment variables.

An illustrative result is:

```text
shell=/bin/bash
```

This often describes your configured login shell, the shell selected for your account when you sign in. It does **not** reliably identify the shell reading your commands right now. Starting a different shell does not necessarily update this value. It can also be unset or manually changed.

Bash provides a more specific clue about itself:

```bash
printf 'bash=%s\n' "${BASH_VERSION:-not Bash}"
```

An illustrative answer is:

```text
bash=5.2.37(1)-release
```

`${BASH_VERSION:-not Bash}` asks for the value of `BASH_VERSION`, but substitutes the text `not Bash` if that value is unset or empty. The braces mark the boundary of this longer substitution; `:-` introduces its fallback text. Bash sets `BASH_VERSION` to its own version.

Treat that as a useful Bash-specific clue, not a universal shell detector. The fallback syntax shown here is supported by Bash and many related shells, but not every shell uses the same language. These variable examples only print information; they do not change which shell your account starts.

## Put the answers together

The running example began with a practical decision: which installation instructions fit this environment? You now have a more useful description than “it runs Linux.”

Using the locally observed values above, the description would be:

> The visible distribution is Debian GNU/Linux 13 (trixie). The running kernel is Linux 5.15.0-198-generic, and the reported machine architecture is aarch64.

That is an interpretation of three observations, not a claim that every layer is supplied by Debian. It also does not establish whether the machine is fully updated or whether a particular download will work.

On your own system, keep the distribution's readable name, the `uname -srm` answer, and any known context such as “inside a container” together when looking for help. You generally do not need to post a complete terminal session or disclose your account name, computer name, or network addresses to answer these initial questions.

The next chapter focuses on the shell itself: how it separates command names from arguments, how quoting works, and how to find help when a command behaves differently from an example.

## Further reading

- [Linux kernel documentation](https://docs.kernel.org/): the kernel project's documentation, with deeper explanations and reference material.
- [os-release specification](https://www.freedesktop.org/software/systemd/man/latest/os-release.html): the identification fields, their meanings, and the fallback rules.
- [GNU coreutils: uname](https://www.gnu.org/software/coreutils/manual/html_node/uname-invocation.html): the options and ordering of kernel and machine information.
- [Linux man-pages: file-hierarchy(7)](https://man7.org/linux/man-pages/man7/file-hierarchy.7.html): a directory-layout reference for systemd-based systems, with links to broader hierarchy specifications. It is not a guarantee that every Linux system uses an identical layout.
