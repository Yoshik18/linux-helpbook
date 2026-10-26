# 2. Filesystem and paths

[Previous: how Linux works](01-how-linux-works.md) · [Index](README.md) · [Next: shell and text](03-shell-and-text.md)

A pathname is a way to locate an object, not the object itself. Keeping names, file metadata, and open handles separate explains why renaming a file does not necessarily interrupt a program already reading it.

## Follow the tree

An **absolute path** starts at the process's root directory, `/`. A **relative path** starts at its current working directory in ordinary shell use. `.` means the current directory and `..` its parent. Resolving a path walks directory components and checks search permission along the way. [path_resolution(7)](https://man7.org/linux/man-pages/man7/path_resolution.7.html) A readable file can therefore be unreachable through a directory you cannot traverse.

The filesystem hierarchy has conventions, not a promise that every installation looks identical. `/etc` holds machine configuration, `/usr` installed software and shared data, `/var` changing application data such as logs, `/run` runtime state, and `/home` commonly users' home directories. `/proc` and `/sys` expose kernel interfaces rather than ordinary stored documents. [hier(7)](https://man7.org/linux/man-pages/man7/hier.7.html) `/usr` is not the directory for users' personal files. Some distributions make `/bin` a symlink into `/usr/bin`.

A **mount** attaches a filesystem or another mounted view at a directory in this tree. Paths below that mount point refer into the attached view, hiding any previous contents there while it remains mounted. [path_resolution(7)](https://man7.org/linux/man-pages/man7/path_resolution.7.html) One directory tree can span several filesystems. Neither an absolute path nor a familiar directory name tells you which disk stores its bytes. This chapter does not mount or unmount anything.

## Types, inodes, and links

Linux file types include regular files, directories, symbolic links, device nodes, sockets, and FIFOs. [inode(7)](https://man7.org/linux/man-pages/man7/inode.7.html) A socket is an IPC endpoint, not a text file that happens to have an unusual extension. Names beginning with a dot are hidden by default in `ls`; that convention is not access control.

An **inode** carries file metadata, including type, owner IDs, permissions, size, and link count. An inode number is unique within its filesystem, not across the machine. [inode(7)](https://man7.org/linux/man-pages/man7/inode.7.html) A directory entry associates a name with an inode. The filename is not simply another field inside that inode.

A **hard link** adds another name for the same file, not a synchronized copy. Ordinary hard links cannot cross filesystem boundaries because the names must refer to the same filesystem object. [inode(7)](https://man7.org/linux/man-pages/man7/inode.7.html) A **symbolic link** instead stores a pathname to resolve. A relative symlink target is interpreted from the directory containing the link, not the caller's working directory. [path_resolution(7)](https://man7.org/linux/man-pages/man7/path_resolution.7.html) It can point across filesystems or point nowhere.

When a process opens a file, it receives a **file descriptor**, an integer referring to an open file description. That reference is not redirected just because the pathname is later renamed or replaced. [open(2)](https://man7.org/linux/man-pages/man2/open.2.html) Removing the last filename also does not immediately reclaim storage while the file remains open. That is one reason deleting a growing log may not free the space you expected.

## Lab: separate names from open handles

Prerequisites: Bash, GNU `stat`, and standard file utilities on a writable Linux filesystem supporting links. Use an existing private scratch parent; here it is `${TMPDIR:-/tmp}`. Substitute your own scratch parent if learning elsewhere. Only newly created lab files are changed; no files are deleted.

```bash
(
    lab=$(mktemp -d "${TMPDIR:-/tmp}/linux-paths.XXXXXX") || exit 1
    cd "$lab" || exit 1
    printf 'first line\n' > original.txt
    ln original.txt second-name.txt
    ln -s original.txt shortcut.txt
    ls -li
    stat -c '%n inode=%i links=%h type=%F' original.txt second-name.txt shortcut.txt
    exec 3< original.txt
    mv original.txt renamed.txt
    cat second-name.txt
    cat <&3
    exec 3<&-
    readlink shortcut.txt
    if [ -e shortcut.txt ]; then
        printf 'Target exists\n'
    else
        printf 'Symlink remains, but its target is missing\n'
    fi
    printf 'Inspect the retained lab: %s\n' "$lab"
)
```

The two regular filenames initially share an inode number and link count of two. GNU `stat` without `-L` describes the symlink itself. After the rename, both reads still print `first line`: one uses the hard link, the other descriptor 3. `readlink` still prints `original.txt`, so the symlink is dangling. The parentheses keep the directory change and descriptor inside a subshell.

**Validation:** this lab block has not been run. No unlink-while-open or mount experiment was run; those mechanisms are explained above, not claimed as tested here.

## Check your understanding

1. Why does renaming the target break this symlink but not the hard link?
2. Why must you consider the filesystem identity as well as an inode number?
3. Does an open descriptor have to resolve the original pathname on every read?
