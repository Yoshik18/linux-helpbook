# 2. The shell and commands

[Contents](../README.md) | [Previous: system](01-system.md) | [Next: files and paths](03-files-and-paths.md)

A shell is a program that reads commands, interprets their syntax and starts other programs. Bash is one common shell. A terminal window is the text interface where you interact with a shell; the terminal and shell are related but different things.

## Read a command line

A simple command has a program name followed by arguments:

```bash
ls -lah /var/log
```

Here `ls` lists directory entries. `-l` requests a detailed listing, `-a` includes names beginning with a dot, and `-h` makes sizes easier to read when used with `-l`. `/var/log` is the argument naming the directory to inspect. This command reads directory information; it does not change the files.

The meaning of an argument depends on the program. Options often begin with `-` or `--`, but their names and behavior belong to each program. Check its help instead of assuming another command uses the same options:

```bash
ls --help
```

External programs often support `--help`. Shell builtins have shell-specific help, for example `help cd` in Bash. Manual pages, when installed, provide longer documentation. Minimal containers may not include a manual-page viewer.

## Builtins and external programs

Some commands must run inside the shell. `cd` changes the shell's own working directory; a separate child process could not change its parent's directory. `type` tells Bash how a command name is resolved:

```bash
type cd
type ls
```

Bash reports `cd` as a builtin and usually resolves `ls` to an executable, unless an alias or function changes that resolution.

`command -v` is a portable way to ask the current shell how it would resolve a name:

```bash
command -v bash
```

It prints the path or shell name when found. If a command is missing, the result can be empty and the exit status nonzero. That only shows the command is not available through the current shell's lookup; it does not establish why.

## The current directory and PATH

The shell remembers a working directory for relative paths. `pwd` prints it. `cd` changes it:

```bash
pwd
cd /tmp
pwd
cd -
pwd
```

`cd /tmp` uses an absolute path from the filesystem root. `cd -` returns to the previous directory. These commands affect only the current shell session. Start with `pwd` when a relative file path behaves unexpectedly.

When you type a program name without a slash, the shell searches directories listed in `PATH`, in order. `printf '%s\n' "$PATH"` prints that list; the colon-separated entries are places the shell checks for executables. Avoid adding writable, untrusted directories to the front of `PATH`, because a file there could shadow a trusted command.

## Quotes and expansion

The shell processes quotes and expansions before it starts a program. Double quotes preserve spaces within a value while still allowing variable expansion:

```bash
name='Ada Lovelace'
printf 'Hello, %s\n' "$name"
```

The assignment sets a shell variable. `printf` then receives the format string and one argument containing the full name. Without the quotes around `$name`, the shell can split the value into separate words. Single quotes preserve their contents literally, so `'$name'` prints the characters `$name` rather than expanding the variable.

A common safety habit is to quote variable expansions that represent a single path or value. It prevents accidental word splitting and wildcard expansion. It does not make an untrusted value safe to embed in a command string evaluated by `eval`.

## Variables, wildcards and the environment

An assignment such as `name='Ada Lovelace'` sets a variable in the current shell. Do not put spaces around `=`: `name = value` tries to run a command named `name`. Export a variable when child programs need it:

```bash
export EDITOR=nano
printf '%s\n' "$EDITOR"
```

`export` makes `EDITOR` available to subsequently started programs. It does not install Nano, launch it, or change another terminal's environment. `unset EDITOR` removes that variable from this shell. Use your installed editor's actual name.

The shell also expands filename patterns before starting a command. In `ls -- *.txt`, `*` matches names in the current directory ending in `.txt`, normally excluding hidden names. Quoting `'*.txt'` passes the pattern literally instead. In default Bash, an unmatched pattern stays literal, so `ls` may complain that `*.txt` does not exist. Do not use a wildcard in a removal command until you have inspected what it expands to.

## Input, output and redirection

Commands normally read standard input (descriptor 0), write results to standard output (1), and send diagnostics to standard error (2). A pipe connects one command's standard output to the next command's input; it does not include standard error by default.

```bash
printf 'alpha\nbeta\n' | grep -F 'beta'
```

`printf` produces two lines and `grep` prints only `beta`. The shell connects the programs; neither creates a file. Redirections instead connect streams to files:

```bash
printf 'first note\n' > notes.txt
printf 'second note\n' >> notes.txt
wc -l < notes.txt
```

Run these only in a directory you own, after checking that `notes.txt` is a safe output name. `>` creates or truncates the file; `>>` appends, creating it if absent. `<` reads the file into the command's standard input. Here `wc -l` prints `2` without a filename because it reads a stream. The shell opens redirection targets before starting the command, so `command > input.txt` can destroy `input.txt` even if the command later fails.

`2> errors.txt` redirects diagnostics. `> result.txt 2>&1` sends output and diagnostics to the same file: `2>&1` duplicates descriptor 1's current destination. Order matters; reversing those redirections gives a different result. Do not suppress diagnostics while you are still investigating a failure.

## Exit status

After a command finishes, its exit status is available as `$?` until another command runs:

```bash
command -v bash
printf 'status=%s\n' "$?"
```

The second line prints the status of `command -v bash`, because it expands `$?` before `printf` runs. In a script, save a status immediately if later commands are needed. For pipelines, the default status is often the status of the last command; Bash's `set -o pipefail` changes that behavior. Learn the pipeline's components before relying on its status.

## Common confusion

- A terminal is not the shell. The terminal provides input and display; the shell interprets commands.
- Not every command is an executable. Some are shell builtins, aliases or functions.
- An option accepted by one program may mean something different, or nothing, in another.
- A printed success-looking line does not replace checking the command's status and intended effect.
- Shell quoting protects argument boundaries; it is not a substitute for safe program design when handling untrusted input.

## Further reading

- [Bash manual](https://www.gnu.org/software/bash/manual/)
- [GNU coreutils manual](https://www.gnu.org/software/coreutils/manual/)
- [Bash reference manual: shell expansions](https://www.gnu.org/software/bash/manual/html_node/Shell-Expansions.html)
