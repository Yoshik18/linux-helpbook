# 7. Understand filesystems and disk usage

When a system reports “no space,” distinguish the filesystem containing the path, its free data blocks, its available inodes, and the directories consuming space. Inspect first; do not delete files at random.

## Map paths to mounted storage

```bash
findmnt -T "$HOME"
df -h "$HOME"
df -i "$HOME"
lsblk -o NAME,TYPE,SIZE,FSTYPE,MOUNTPOINTS
```

A disk contains partitions; a partition may hold an LVM physical volume, logical volume, RAID device, or filesystem; a filesystem is then mounted at a directory. A mount makes a filesystem's contents visible at a path. `findmnt -T` identifies the mount covering a path. `df -h` reports filesystem capacity and used/available blocks; `df -i` reports inode capacity. Many small files can exhaust inodes even with bytes available. `lsblk` shows visible block-device relationships, not every network, bind, or overlay mount. Older util-linux releases may use `MOUNTPOINT` rather than `MOUNTPOINTS`.

## Find large directories without crossing mounts

```bash
du -x -h --max-depth=1 "$HOME"
du -x -B1 --max-depth=2 "$HOME" | sort -nr | head -n 10
find "$HOME" -type f -size +100M -print
```

`du` totals disk blocks used by files beneath a directory; `-x` stays on one filesystem, `--max-depth` limits depth, and `-B1` reports byte units suitable for numeric sorting. `sort -nr` orders numeric values descending; `head -n 10` limits the displayed list. Unlike `df`, which reports a whole filesystem, `du` walks visible directory entries. It can be slow, permission-denied results are incomplete, and hard links, compression, reflinks, and snapshots complicate totals. Passing a directory includes hidden entries; shell glob `*` generally does not. `find` here lists names, not allocated size.

## Logical size differs from allocated space

On the [shared practice files](01-how-linux-works.md), create the sparse file:

```bash
truncate -s 1M "$LINUX_LAB/data/sparse.bin"
stat -c 'length=%s bytes; blocks=%b; block-unit=%B' "$LINUX_LAB/data/sparse.bin"
du -B1 "$LINUX_LAB/data/sparse.bin"
du --apparent-size -B1 "$LINUX_LAB/data/sparse.bin"
```

`truncate -s` sets the logical length; holes read back as zeroes without requiring every block to be allocated. `stat` reports logical size and allocated block count/unit. `du` normally reports allocated blocks; `--apparent-size` reports logical length. Filesystem behavior varies, so exact savings differ. This lab only creates or resizes a known file under `$LINUX_LAB`; do not copy the command to a real data path.

## A deleted name can still consume space

Unlinking a file removes its directory entry, but storage remains allocated while a process holds it open. This isolated example creates and removes only a small file under the private fixture:

```bash
(
    printf 'still readable\n' > "$LINUX_LAB/data/open-demo.txt"
    exec 3< "$LINUX_LAB/data/open-demo.txt"
    rm -- "$LINUX_LAB/data/open-demo.txt"
    readlink "/proc/$BASHPID/fd/3"
    cat <&3
    exec 3<&-
)
```

The link target normally ends in `(deleted)` and `cat` still prints `still readable`. Closing the final descriptor releases storage when no other links remain. `$BASHPID` identifies this Bash subshell; `$$` can still identify its parent. On a host, `lsof +L1` can list deleted-open files when installed and permitted. Identify the owning process and follow its supported log-reopen or restart procedure; do not truncate an unknown descriptor or restart a database casually. Permissions can hide results.

## Keep storage changes out of blind command recipes

`mkfs`, partition-table edits, mounting, filesystem growth, and LVM changes affect persistent data. The correct order and command depend on device identity, filesystem, backups, and recovery plan. Never copy a device name from an example into a real system. `findmnt`, `lsblk`, and read-only volume queries help establish the layout; they do not authorize a destructive change.

## Practice

Compare `df -h` and `df -i` for your home directory. Create the sparse lab file above and explain why its apparent length can exceed its allocated blocks. Remove only the lab file and directory you created.

[df manual](https://man7.org/linux/man-pages/man1/df.1.html) · [du manual](https://man7.org/linux/man-pages/man1/du.1.html) · [unlink system call](https://man7.org/linux/man-pages/man2/unlink.2.html) · [Disk-space checklist](../troubleshooting/disk-space.md) · [Previous](06-memory-and-cpu.md) · [Index](README.md) · [Next](08-boot-services-and-logs.md)
