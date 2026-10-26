# 1. Get comfortable in the terminal

Start with the commands you use to identify a machine, find your way around and
get help. Examples use Bash on Linux. You do not need root.

## Find out which machine and shell you are using

```bash
uname -sr
uname -m
cat /etc/os-release
whoami
id
printf 'Bash version: %s\n' "$BASH_VERSION"
```

`uname -s` prints the kernel name, `-r` its release and `-m` the architecture.
`os-release` identifies the distribution's userspace. A container can report
Debian there while sharing its host's kernel. `id` also shows numeric IDs and
groups. Values differ by machine; compare fields, not a sample version number.

## Find your current directory

```bash
pwd
ls
ls -lah
cd /etc
pwd
cd -
```

`pwd` prints the current directory. `ls -l` adds modes, ownership, size and time;
`-a` includes dotfiles and `-h` makes sizes readable. `cd -` returns to the
previous directory. `cd` with no argument takes you home. An absolute path starts
with `/`; a relative path starts from your current directory.

## Find a command before installing anything

```bash
type cd
type ls
command -v bash
command -v ss
```

In Bash, `cd` is a builtin: changing directory must affect the shell itself.
External commands are generally found through `PATH`. `type` can identify
functions and aliases too. `command -v ss` printing nothing and returning nonzero
means it was not found, not that your network is broken.

## Ask the right help system

```bash
help cd
help printf
ls --help
```

For external commands, use `man ls` if manual pages are installed. In the usual
`less` pager, `/pattern` searches, `n` repeats the search and `q` exits. `man 5
passwd` describes the file format; `man 1 passwd` describes the command. Minimal
containers may not include `man` or its database.

## Create the practice files

From this repository's root, source the small, reviewable setup script:

```bash
source fundamentals/labs/setup.sh
printf '%s\n' "$LINUX_LAB"
ls -la "$LINUX_LAB"
```

It creates a private temporary directory containing fictional logs, configuration
and notes. It does not install anything or touch existing application files.
Later chapters use `$LINUX_LAB`; run setup again in a new terminal if necessary.
Each run creates a new directory. It honors `TMPDIR` when set.

## Practice

Find whether `printf` is a builtin, locate the external `bash` executable and
list hidden practice files without changing directories.

<details>
<summary>One answer</summary>

```bash
type printf
command -v bash
ls -la "$LINUX_LAB"
```

The hidden fixture is `.practice`. `ls` without `-a` omits it.

</details>

[Manual: Bash commands and builtins](https://man7.org/linux/man-pages/man1/bash.1.html)
· [uname](https://man7.org/linux/man-pages/man1/uname.1.html)
· [Guide index](README.md) · [Next: files and paths](02-filesystem-and-paths.md)
