# Linux commands: choose the right tool

This is a quick reference, not a list to memorize. Start with the task, run the
smallest command that answers it, then read the output before changing anything.
For concepts and worked explanations, follow the [Linux learning path](../README.md).

Examples assume Bash on Linux and mostly GNU or util-linux commands. A command may
be missing from a minimal container, provided by a different package on another
distribution, or have different options on macOS/BSD. Check `command -v name` and
`name --help` or `man name` before relying on an unfamiliar flag. `cd` and `help`
are Bash builtins, so use `help cd`; `man cd` normally describes no command.

## First: understand the command line

A simple command has a program, options and operands:

```text
command [options] [operands...]
```

In `ls -lh /var/log`, `ls` is the program, `-l` and `-h` are options, and
`/var/log` is the operand. The shell processes quoting, variables, wildcards,
redirection and pipes before an external program receives its arguments. A quoted
path such as `"$HOME/my notes"` stays one argument; an unquoted wildcard such as
`*.log` is expanded by Bash to matching names before the program runs.

Standard input, output and error are numbered 0, 1 and 2. `>` redirects output
and truncates the destination; `>>` appends. `2>` redirects diagnostics. `|`
sends one program's output to another program's input. A command's exit status is
not its printed output: zero usually means success, but some tools use nonzero
for ordinary results such as a search with no match. See [shell and text](../fundamentals/03-shell-and-text.md)
for a worked explanation.

## Find your way around

| Task | Command | What to notice |
|---|---|---|
| Show current directory | `pwd` | The base for relative paths. |
| List files, including hidden names | `ls -la` | `-a` includes dotfiles; `-l` shows type, modes, owner, size and time. |
| Read sizes in a long listing | `ls -lh` | `-h` scales displayed sizes; it does not change stored file size. |
| Change directory | `cd /etc` | Bash builtin; use an absolute or current-directory-relative path. |
| Return to previous directory | `cd -` | Prints and changes to the previous working directory. |
| Create a nested directory | `mkdir -p a/b` | Creates missing parents; does not fail just because they exist. |
| Identify the OS and kernel | `cat /etc/os-release; uname -sr` | Distribution userspace and running kernel are different facts. |

`ls -l` shows a snapshot of names and metadata, not a reliable format to parse in a
script. For scripts, use `find` with `-exec ... {} +` or NUL-delimited output and
read it safely. See [paths and files](../fundamentals/02-filesystem-and-paths.md).

## Read and search text

| Task | Command | What to notice |
|---|---|---|
| Read a short file | `cat file` | Writes the whole file to standard output. |
| Inspect first or last lines | `head -n 20 file`; `tail -n 20 file` | `-n` sets the line count. |
| Page through a large file | `less file` | Search with `/text`, move with `n`, quit with `q`. |
| Follow new log lines | `tail -F file` | GNU `-F` retries and follows the filename through common rotations; Ctrl+C stops. |
| Search case-insensitively with line numbers | `grep -in 'timeout' app.log` | `-i` ignores case; `-n` adds source line numbers. Quote patterns. |
| Show nearby context | `grep -C 2 'ERROR' app.log` | `-C 2` prints two lines before and after each match. |
| Search a directory tree | `grep -RIn -- 'timeout' ./logs` | `-R` recurses and follows symlinks; `-I` skips binary files; `-n` numbers lines. |
| Select whitespace-separated fields | `awk '{print $1, $4}' file` | Awk's default fields split on whitespace; `$1` and `$4` are fields. |
| Select delimited fields | `cut -d, -f1,3 file.csv` | `-d,` sets a one-character delimiter; `-f1,3` selects fields. Not a full CSV parser. |
| Count matching lines | `grep -c 'ERROR' app.log` | Counts lines, not the number of matches within each line. |
| Sort then count duplicates | `sort file` followed by `uniq -c` | Feed sorted output to `uniq -c`; `uniq` groups adjacent duplicates, so sort first when grouping an entire file. |

GNU `grep` returns 0 if it finds a match, 1 if it finds none and 2 for an error.
That difference matters in scripts and pipelines. A zero count from a downstream
`wc` does not prove the input was readable. See [logs and pipelines](../fundamentals/03-shell-and-text.md).

## Create, copy and find files

| Task | Command | What to notice |
|---|---|---|
| Create an empty file | `touch notes.txt` | Creates it if absent; otherwise changes timestamps. |
| Copy a file | `cp -i source destination` | `-i` prompts before overwriting an existing destination. |
| Rename or move | `mv -i old-name new-name` | Can replace a destination; `-i` asks first in an interactive terminal. |
| Make a temporary directory | `mktemp -d` | Prints a newly created unique path; save that path before using it. |
| Find regular `.log` files | `find /var/log -type f -name '*.log'` | `-type f` means regular file; quote the pattern so the shell does not expand it. |
| Find files larger than 10 MiB | `find /path -type f -size +10M -print` | GNU find's `M` unit is 1024×1024 bytes; inspect matches before acting. |
| Count lines in safely matched files | `find ./logs -type f -name '*.log' -exec wc -l {} +` | Passes filenames as arguments, including spaces; `+` batches them. |
| Compare two trees | `diff -ruN old/ new/` | `-r` recurses, `-u` shows context, `-N` treats a missing file as empty. Status 1 means differences. |

Do not append `-delete`, `rm` or a recursive permission change until you have
checked the exact paths and understand the effects. Start in a disposable directory.

## Understand access before changing it

| Task | Command | What to notice |
|---|---|---|
| Show current user and groups | `id` | Numeric UID/GID and groups used by this process. |
| Inspect a file's mode and owner | `stat -c '%A %a %U:%G %n' file` | GNU `stat` format: symbolic mode, octal mode, owner/group and path. |
| Inspect each path component | `namei -l /path/to/file` | `-l` shows modes/owners while resolving each component; util-linux required. |
| Add execute for the owner | `chmod u+x script.sh` | Changes only the owner's execute bit. It does not make a script's interpreter available. |
| Set a specific file mode | `chmod 600 private.conf` | Owner read/write, no group/other mode bits. Choose based on actual access needs. |
| Change the owning user/group | `chown user:group file` | Usually requires privilege when changing ownership. Verify target first. |

For a directory, `x` means search/traverse; without it, a user cannot access a
known name inside. `chmod -R 644 directory/` is not a general permission repair:
it removes directory execute bits. Learn [users and permissions](../fundamentals/04-users-and-access.md)
before changing a tree.

## Inspect processes and resources

| Task | Command | What to notice |
|---|---|---|
| List processes with useful columns | `ps -eo pid,ppid,user,stat,pcpu,rss,comm --sort=-pcpu` | procps syntax; CPU is an average, RSS is resident memory in KiB. |
| Find an exact process name | `pgrep -a -x nginx` | `-x` requires exact name; `-a` prints arguments, which may contain secrets. |
| Watch changing activity | `top` | Interactive; press `q` to quit. Values depend on CPU count/tool settings. |
| Show memory | `free -h` | `-h` scales values; check `available`, not only `free`. |
| Sample CPU, memory and I/O counters | `vmstat 1 5` | One-second interval, five reports; first report often covers time since boot. |
| Check filesystem capacity | `df -h /var` | Reports the filesystem containing `/var`; `-h` is display scaling. |
| Check inode capacity | `df -i /var` | A filesystem can run out of inodes before byte capacity. |
| Measure directories | `du -x -h --max-depth=1 /var` | GNU flags: stay on one filesystem and limit depth; permission gaps make totals incomplete. |

A high load average is not a CPU percentage. `free` memory includes cache and is
not automatically wasted. Compare the same scope over time. See [processes](../fundamentals/05-processes-and-signals.md),
[CPU and memory](../fundamentals/06-memory-and-cpu.md) and [disk troubleshooting](../troubleshooting/disk-space.md).

## Check network layers

| Question | Command | What it tells you |
|---|---|---|
| Which addresses are configured? | `ip -br address` | `-br` formats interface/address output briefly; it sends no probe. |
| Which route would be used? | `ip route get 203.0.113.10` | Kernel route lookup for this destination; documentation address, not necessarily reachable. |
| What does the configured resolver return? | `getent ahosts example.com` | Uses system name-service configuration, which may include hosts files and DNS. |
| Is a TCP port listening? | `ss -lnt` | `-l` listeners, `-n` numeric endpoints, `-t` TCP. Does not test a remote client path. |
| Does an HTTP endpoint answer? | `curl --fail --connect-timeout 3 --max-time 10 https://example.com/ -o /dev/null` | Bounded request; `--fail` returns nonzero for HTTP error responses. Contact only allowed endpoints. |
| Show connection stages | `curl -v --connect-timeout 3 --max-time 10 https://example.com/ -o /dev/null` | Verbose output may contain sensitive headers; redact before sharing. |

DNS, routing, TCP, TLS and HTTP are different steps. Ping tests ICMP, not HTTP.
A timeout is not by itself proof of a firewall problem. See [networking](../fundamentals/10-networking.md)
and [the troubleshooting checklist](../troubleshooting/network-connectivity.md).

## Services, logs and software

| Task | Command | What to notice |
|---|---|---|
| Inspect failed systemd units | `systemctl --no-pager --failed` | Requires a reachable systemd manager; read-only query. |
| Inspect recent unit logs | `journalctl -u example.service -n 50 --no-pager` | Substitute the real unit; access and journal retention vary. |
| Check installed Debian package | `dpkg-query -W bash` | Queries the local package database; does not refresh repository metadata. |
| Check candidate package version | `apt-cache policy bash` | Candidate depends on cached repository metadata, which may be stale. |
| Check installed RPM package | `rpm -q bash` | Queries the local RPM database. |
| Print package file list | `dpkg-query -L bash` or `rpm -ql bash` | Files the package database records; filesystem aliases may differ. |

`systemctl restart`, package installation and service configuration alter state.
Do not run them on a real host as a way to learn a syntax. See [services](../fundamentals/08-boot-services-and-logs.md)
and [packages](../fundamentals/09-packages-and-software.md).

## Archives and Bash job control

| Task | Command | What to notice |
|---|---|---|
| Create a gzip-compressed archive | `tar -czf backup.tar.gz -C /path/to/parent directory` | `-c` create, `-z` gzip, `-f` archive file, `-C` change base directory. |
| List an archive before extraction | `tar -tzf backup.tar.gz` | Inspect names before extracting unfamiliar content. |
| Extract to a chosen directory | `tar -xzf backup.tar.gz -C /safe/lab` | `-x` extracts; use a private, unprivileged destination. |
| Run a short job in background | `sleep 5 &` | `&` backgrounds it in the current shell; it is not a service manager. |
| Return job to foreground | `fg` | Interactive shell job control; not available in ordinary noninteractive scripts. |
| Wait for a child and get status | `wait "$pid"` | Use a PID captured from a child you started; the status is the command's result. |

For scripting, arrays, variables, conditions, loops, functions and robust argument
handling, use the [Bash scripting guide](../shell-scripting/scripting.md). For Vim
keys, see the [Vim reference](../vim/vim.md).

## Safer troubleshooting order

1. Identify the exact symptom, path, process, port and time window.
2. Inspect state with read-only commands and record output that is safe to share.
3. Check one layer at a time; distinguish an observation from a diagnosis.
4. Change one thing only when you know its scope, have authorization and can verify or roll it back.
5. Preserve logs and evidence before a restart, deletion or cleanup.

Examples here are for learning. Redact credentials, arguments, addresses and
private paths. Never use broad recursive changes, guessed PIDs or disk/partition
commands on a machine you do not control.
