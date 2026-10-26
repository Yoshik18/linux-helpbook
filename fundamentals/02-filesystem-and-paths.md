# 2. Work with files, directories and archives

Run the [practice setup](01-how-linux-works.md) first. Every write below targets
its private `$LINUX_LAB` directory, not a real service's files.

## Create, copy and rename

```bash
mkdir -p "$LINUX_LAB/work/reports"
touch "$LINUX_LAB/work/empty.txt"
cp "$LINUX_LAB/notes/todo.txt" "$LINUX_LAB/work/tasks.txt"
mv "$LINUX_LAB/work/tasks.txt" "$LINUX_LAB/work/reports/tasks.txt"
ls -lh "$LINUX_LAB/work/reports"
```

`mkdir -p` creates missing parents and accepts an existing directory. `touch`
creates an empty file or updates an existing file's timestamps. `cp` leaves the
source in place; `mv` changes its location/name. Both can overwrite destinations:
use `cp -i` or `mv -i` for a confirmation prompt when working interactively.

To remove a practice file deliberately, use `rm -i` with its exact path. There
is no general undo. `rmdir` removes only an empty directory. Do not start with a
recursive force-delete command.

## Read a file without opening an editor

```bash
cat "$LINUX_LAB/config/app.conf"
head -n 2 "$LINUX_LAB/logs/app.log"
tail -n 2 "$LINUX_LAB/logs/app.log"
nl -ba "$LINUX_LAB/notes/todo.txt"
```

Expect three configuration lines. `head` shows the beginning, `tail` the end and
`nl -ba` numbers all lines. For a large file, use `less filename` instead of
flooding the terminal. `tail -f filename` follows growth; Ctrl+C stops following.
GNU `tail -F` also retries and follows the name across common log rotation cases.

## Find files by name or size

```bash
find "$LINUX_LAB" -type f -name '*.log'
find "$LINUX_LAB" -type f -name '*spaces*'
find "$LINUX_LAB" -type f -size +1M
find "$LINUX_LAB" -type f -name '*.txt' -exec wc -l {} +
```

Quote the pattern so `find`, not your current shell, interprets it. `-type f`
selects regular files. The size query initially returns nothing. `-exec ... {} +`
passes matching paths as separate arguments, including filenames with spaces.
Preview matches before adding any mutating operation. Do not parse `ls` output
as a general filename list.

## Inspect links and file identity

```bash
ln "$LINUX_LAB/notes/todo.txt" "$LINUX_LAB/work/todo-hardlink"
ln -s ../notes/todo.txt "$LINUX_LAB/work/todo-shortcut"
stat -c '%n inode=%i links=%h mode=%a' "$LINUX_LAB/notes/todo.txt" "$LINUX_LAB/work/todo-hardlink"
readlink "$LINUX_LAB/work/todo-shortcut"
```

The hard-linked names share an inode and data on the same filesystem. A symlink
stores a path; its relative target is resolved from the symlink's directory.
`ln` refuses an existing destination here, so rerunning this section may report
that the link already exists. It does not create another copy of the file.

## Create and inspect a backup archive

```bash
tar -czf "$LINUX_LAB/archive/notes.tar.gz" -C "$LINUX_LAB" notes
tar -tzf "$LINUX_LAB/archive/notes.tar.gz"
mkdir -p "$LINUX_LAB/restored"
tar -xzf "$LINUX_LAB/archive/notes.tar.gz" -C "$LINUX_LAB/restored"
diff -r "$LINUX_LAB/notes" "$LINUX_LAB/restored/notes"
```

`-c` creates, `-t` lists, `-x` extracts, `-z` uses gzip and `-f` names the archive.
`-C` changes the base directory for the operation. A successful `diff` prints
nothing and returns zero. Extract unfamiliar archives only in an isolated,
unprivileged environment after inspecting their paths and contents.

## Practice

Find all `.conf` files and count the lines in every `.txt` file without breaking
on spaces. Create a compressed archive of `config/` without absolute paths.

<details>
<summary>One answer</summary>

```bash
find "$LINUX_LAB" -type f -name '*.conf'
find "$LINUX_LAB" -type f -name '*.txt' -exec wc -l {} +
tar -czf "$LINUX_LAB/archive/config.tar.gz" -C "$LINUX_LAB" config
```

</details>

[Manual: find](https://man7.org/linux/man-pages/man1/find.1.html)
· [tar](https://man7.org/linux/man-pages/man1/tar.1.html)
· [inode](https://man7.org/linux/man-pages/man7/inode.7.html)
· [Previous](01-how-linux-works.md) · [Index](README.md) · [Next](03-shell-and-text.md)
