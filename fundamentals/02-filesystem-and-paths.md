# 2. Understand the filesystem and work with paths

Linux presents files through one directory tree rooted at `/`; storage devices are attached at mount points within that tree. A path names an entry, not necessarily unique data: hard links can name the same inode, while symbolic links store another path. This model matters when locating files, making backups, and interpreting links.

## Read paths from the current directory

```bash
pwd
printf 'home=%s\n' "$HOME"
ls -la /
ls -ld "$LINUX_LAB" "$LINUX_LAB/config"
```

`/` is the root directory; `/home/alex` is an absolute path. `.` means the current directory, `..` its parent, and `~/notes` expands to a path under your home. `pwd` prints the working directory; `$HOME` is an environment variable. `ls -a` includes dotfiles, `-l` gives details, and `-d` reports the named directory itself rather than its contents. Quote variable-based paths so spaces remain part of one operand.

## Create, copy, move, remove

```bash
mkdir -p "$LINUX_LAB/work/reports"
touch "$LINUX_LAB/work/empty.txt"
cp "$LINUX_LAB/notes/todo.txt" "$LINUX_LAB/work/tasks.txt"
mv "$LINUX_LAB/work/tasks.txt" "$LINUX_LAB/work/reports/tasks.txt"
ls -lh "$LINUX_LAB/work/reports"
```

`mkdir -p` creates missing parent directories and tolerates an existing directory. `touch` creates an empty file if absent, otherwise updates timestamps. `cp SOURCE DEST` copies while retaining the source; `mv SOURCE DEST` renames or relocates it. They may replace an existing destination; use `-i` for an interactive confirmation when appropriate. `ls -lh` lists the result with readable sizes.

For cleanup, `rmdir DIR` removes only an empty directory. `rm -i FILE` prompts before removing the named file; removal generally has no undo. Inspect exact paths first. Avoid recursive force deletion, especially with variables or elevated privileges.

## Read without editing

```bash
cat "$LINUX_LAB/config/app.conf"
head -n 2 "$LINUX_LAB/logs/app.log"
tail -n 2 "$LINUX_LAB/logs/app.log"
nl -ba "$LINUX_LAB/notes/todo.txt"
```

`cat` prints the whole file. `head -n 2` and `tail -n 2` show the first and last two lines; `nl -ba` numbers even blank lines. For large files, `less FILE` allows scrolling/search without dumping everything. `tail -f FILE` waits for appended data; Ctrl-C stops it. GNU `tail -F` also retries by filename across common log rotations.

## Search by name or size

```bash
find "$LINUX_LAB" -type f -name '*.log'
find "$LINUX_LAB" -type f -name '*spaces*'
find "$LINUX_LAB" -type f -size +1M
find "$LINUX_LAB" -type f -name '*.txt' -exec wc -l {} +
```

`find ROOT` walks from the specified root. `-type f` selects regular files; `-name` matches a filename pattern; quoted patterns prevent the shell expanding `*` first. `-size +1M` selects files larger than the unit threshold (GNU find uses 1 MiB here). `-exec wc -l {} +` passes batches of matched path operands safely, including names with spaces; `wc -l` counts newline characters. Preview results before adding actions that change files. Do not parse `ls` output as a filename list.

## Links name data in different ways

```bash
ln "$LINUX_LAB/notes/todo.txt" "$LINUX_LAB/work/todo-hardlink"
ln -s ../notes/todo.txt "$LINUX_LAB/work/todo-shortcut"
stat -c '%n inode=%i links=%h mode=%a' "$LINUX_LAB/notes/todo.txt" "$LINUX_LAB/work/todo-hardlink"
readlink "$LINUX_LAB/work/todo-shortcut"
```

`ln` creates a hard link: both names share an inode and file data, on the same filesystem. `ln -s TARGET LINK` creates a symbolic link whose contents are a path; this relative target is resolved from the link's directory. `stat -c` selects a GNU format: `%n` name, `%i` inode number, `%h` hard-link count, `%a` numeric mode. `readlink` prints the stored target. Existing link names make these creation commands fail rather than overwrite them.

## Archive a directory and compare a restore

```bash
tar -czf "$LINUX_LAB/archive/notes.tar.gz" -C "$LINUX_LAB" notes
tar -tzf "$LINUX_LAB/archive/notes.tar.gz"
mkdir -p "$LINUX_LAB/restored"
tar -xzf "$LINUX_LAB/archive/notes.tar.gz" -C "$LINUX_LAB/restored"
diff -r "$LINUX_LAB/notes" "$LINUX_LAB/restored/notes"
```

For `tar`, `-c` creates, `-t` lists, `-x` extracts, `-z` selects gzip compression, and `-f FILE` names the archive. `-C DIR` changes directory before processing the following path; this stores `notes/` rather than an absolute path. `diff -r` compares directory contents recursively: no output and status 0 means equal; status 1 means differences. Inspect an unfamiliar archive's listing and extract in an isolated unprivileged location.

**Try it:** Find `.conf` files, count all `.txt` lines without breaking on spaces, then archive `config/` without an absolute path.

```bash
find "$LINUX_LAB" -type f -name '*.conf'
find "$LINUX_LAB" -type f -name '*.txt' -exec wc -l {} +
tar -czf "$LINUX_LAB/archive/config.tar.gz" -C "$LINUX_LAB" config
```

[Manual: find](https://man7.org/linux/man-pages/man1/find.1.html) · [tar](https://man7.org/linux/man-pages/man1/tar.1.html) · [inode](https://man7.org/linux/man-pages/man7/inode.7.html) · [Previous](01-how-linux-works.md) · [Index](README.md) · [Next](03-shell-and-text.md)
