# 3. Files, directories and paths

[Contents](../README.md) | [Previous: shell](02-shell.md) | [Next: text](04-text.md)

Linux stores files in a single directory tree. The top is `/`, called the root directory. Directories organize names, and a path tells the system how to reach a name. A path beginning with `/` is absolute; any other path is interpreted from the shell's current directory.

## Navigate and inspect

```bash
pwd
ls -lah /
```

`pwd` prints the current directory. `ls -lah /` lists the root directory: `-l` requests detailed fields, `-a` includes hidden names, and `-h` makes file sizes human-readable. A name beginning with `.` is hidden by convention, not protected from access.

A directory listing shows names and metadata, not necessarily what a program is doing with those files. To inspect one path, use `stat` where available:

```bash
stat /etc/os-release
```

`stat` reports metadata such as type, size, owner and modification time. Exact fields and formatting vary. It reads metadata and does not follow every tool's conventions identically, so check `stat --help` on non-GNU systems.

## Absolute and relative paths

`/etc/hostname` is an absolute path. `.` means the current directory and `..` means its parent. If the current directory is `/home/sam`, then `Documents/notes.txt` refers to `/home/sam/Documents/notes.txt`.

```bash
printf 'current: '; pwd
printf 'home: %s\n' "$HOME"
```

`$HOME` is usually the current user's home-directory path. Environment setup can change it, so treat it as a convenient value, not proof of account identity. `printf` prints the labels and values without changing files.

Spaces are allowed in names. Quote paths so the shell passes one argument:

```bash
ls -ld -- "$HOME/My Notes"
```

`-d` asks `ls` to describe the directory entry itself rather than listing its contents. `--` ends option parsing for many GNU utilities, which helps when a name begins with a dash. Quoting preserves spaces. Not every program supports `--`, so consult its help when needed.

## File type and links

Linux does not require filename extensions to determine file type. A name such as `report.txt` is still just a name. `file` inspects content patterns and reports a likely type:

```bash
file -L /etc/os-release
```

`-L` follows symbolic links, which matters because `/etc/os-release` may link to another file. The result is an identification guess based on file content, not a guarantee about how every application will interpret the file.

A symbolic link is a path that points to another path. `ls -l` shows the link target after `->`. Use `readlink` to print that target:

```bash
readlink /bin/sh
```

The link may be relative or absolute. A relative link target is resolved from the directory containing the link. The target might be missing, so a displayed link does not guarantee that its destination exists.

## Create and remove practice files carefully

The following commands create a directory and one empty file in your home directory. Use a name that does not already exist. They modify your filesystem:

```bash
mkdir -- "$HOME/linux-notes"
touch -- "$HOME/linux-notes/first.txt"
ls -l -- "$HOME/linux-notes"
```

`mkdir` creates the directory. `touch` creates an empty file if it does not exist; if it does exist, it normally updates both its access and modification times. `ls` confirms the names and metadata. If the path already contains anything you need, choose another directory name instead.

## Copy, move and locate files

Continue in the `linux-notes` directory created above. These commands write files:

```bash
cp -i -- "$HOME/linux-notes/first.txt" "$HOME/linux-notes/copy.txt"
mv -i -- "$HOME/linux-notes/copy.txt" "$HOME/linux-notes/renamed.txt"
find "$HOME/linux-notes" -type f -name '*.txt' -print
```

`cp` reads the source and creates a separate destination file. `mv` renames or moves an entry; across filesystems it may copy and then remove the source. `-i` asks before replacing an existing destination. Check both operands, because the final operand is a destination directory if that directory already exists. A copy is not a complete backup policy, and moving a path can break programs that expect its old location.

`find` starts at the named directory, selects regular files with `-type f`, matches basenames using `-name`, and prints matching paths with `-print`. Quotes keep `*.txt` for `find` to interpret, rather than letting the shell expand it in the current directory. This invocation does not follow symbolic links to other directories. Avoid adding `-delete` or command execution until you understand precisely which paths match. Keep these files until you have finished the example, then use the explicit cleanup below.

A hard link is another directory entry for the same inode on the same filesystem. Unlike a symbolic link, it does not contain a target path. Removing one hard link leaves the data accessible through other links, and through processes that still have the file open. Ordinary hard links to directories are restricted to preserve the tree structure.

## Edit a text file

If Nano is installed, `nano notes.txt` opens a text editor for that path in the current directory. Confirm that you are in a directory you own and that the file is safe to change. Type text, use Ctrl+O followed by Enter to save, and Ctrl+X to exit. Opening a missing filename does not create it on disk until you save. Other editors have different controls; do not experiment on system configuration as your first editing task.

## Remove only the files you created

After confirming the exact paths, remove the two files from the sequence above and then its directory:

```bash
rm -- "$HOME/linux-notes/first.txt" "$HOME/linux-notes/renamed.txt"
rmdir -- "$HOME/linux-notes"
```

`rm` removes the named files; `rmdir` removes a directory only when it is empty. If you saved any additional notes there, `rmdir` will refuse rather than delete them. These actions are not generally recoverable from the command line. Avoid `rm -r` on paths you have not inspected, and never copy a removal command with an uncertain variable or wildcard.

## Common confusion

- `/` is the filesystem tree's root; `/root` is the home directory commonly used by the root account.
- A hidden name is not a security boundary.
- A symbolic link can point to a missing destination.
- `touch` can change an existing file's timestamp.
- Relative paths depend on the shell's current directory.

## Further reading

- [GNU Coreutils: File name manipulation](https://www.gnu.org/software/coreutils/manual/html_node/File-name-manipulation.html)
- [Linux man-pages: path_resolution(7)](https://man7.org/linux/man-pages/man7/path_resolution.7.html)
- [Linux man-pages: symlink(7)](https://man7.org/linux/man-pages/man7/symlink.7.html)
- [GNU findutils manual](https://www.gnu.org/software/findutils/manual/html_mono/find.html)
- [Nano: getting started](https://www.nano-editor.org/dist/latest/nano.html#Getting-Started)
