# 7. Storage and filesystems

[Previous: Memory and CPU](06-memory-and-cpu.md) · [Index](README.md) · [Next: Boot, services and logs](08-boot-services-and-logs.md)

A path tells you where a program looks, not which device stores its bytes.
Follow the layers before investigating storage. These commands assume Linux,
GNU coreutils and util-linux; filesystem behavior and container visibility vary.

## From blocks to paths

A block device exposes addressable blocks. It might represent a physical disk,
a virtual disk or a device assembled from other devices. A partition describes
a region within a device; it is not itself a filesystem. A filesystem organizes
file data and metadata on storage. Some filesystems instead use memory or a
network server, so not every mounted filesystem has a local disk underneath.

Mounting attaches a filesystem to a directory in a mount namespace. The same
path can therefore lead to different storage in different containers. Mounting
on a nonempty directory normally hides its existing contents without deleting
them. Looking at the parent directory's device is not enough when the child is
a separate mount.

These inspections do not mount, format or modify devices:

```bash
findmnt -T ${TMPDIR:-/tmp}
lsblk -o NAME,TYPE,SIZE,FSTYPE,MOUNTPOINTS
df -h ${TMPDIR:-/tmp}
df -i ${TMPDIR:-/tmp}
```

Replace the scratch path with an existing path you need to understand. `findmnt`
identifies its containing mount; `lsblk` shows visible block-device layers.
Network filesystems and container overlays need not map neatly onto that tree.
Older util-linux versions may require `MOUNTPOINT` instead of `MOUNTPOINTS`.
These commands were tested in a container, not against physical disks.

LVM adds another layer: physical volumes contribute storage to a volume group;
logical volumes expose virtual block devices backed by that pool. A filesystem
can then live on a logical volume. Growing a virtual disk, partition, LVM layer
and filesystem are separate operations.
Their presence and ordering depend on the system; this chapter deliberately gives
no provisioning commands. [lvm.8](https://man7.org/linux/man-pages/man8/lvm.8.html)

## A name is not the file's identity

A directory maps names to inode numbers. An inode records file metadata, such as
ownership, permissions and size; the filename is in the directory entry. Inode
numbers are unique within a filesystem, not across the entire machine. [inode.7](https://man7.org/linux/man-pages/man7/inode.7.html)

A hard link adds another name for the same inode. Both names access the same
file content; it is not a synchronized copy, and a hard link cannot cross
filesystem boundaries. A symbolic link is different: it stores a path to resolve
later, which may lead across mounts or point to nothing.

Removing one name does not necessarily release storage. Other hard links may
remain. Even after the final name disappears, an open descriptor can keep the
file alive until it closes. This explains why deleting an actively written log
might not reduce filesystem usage. [unlink.2](https://man7.org/linux/man-pages/man2/unlink.2.html)

## Length, allocation and durability differ

A sparse file has logical regions that read as zeros without allocating all the
corresponding data blocks. Its apparent length can be much larger than its
allocated storage. Compression, snapshots and copy-on-write sharing introduce
further differences; byte accounting is not identical on every filesystem. [du.1](https://man7.org/linux/man-pages/man1/du.1.html)

Buffered writes usually reach the page cache before persistent storage. A
successful write is therefore not automatically proof of survival after power
loss. Applications needing durability use appropriate synchronization, such as
`fsync()`, and must handle errors. Persisting a newly created directory entry
can also require synchronizing the containing directory. Filesystem journaling
helps recovery but does not replace application-level durability or backups. [fsync.2](https://man7.org/linux/man-pages/man2/fsync.2.html)

## Small, isolated inode and sparse-file experiment

This Bash lab requires GNU `truncate`, `stat` and `du`. It creates only a private
scratch directory and a logically 1 MiB sparse file; it does not provision a disk.
If the base directory is absent or unwritable, stop rather than changing it.

```bash
(
    base=${TMPDIR:-/tmp}
    [ -d "$base" ] && [ -w "$base" ] || exit 1
    lab=$(mktemp -d "$base/linux-storage.XXXXXX") || exit 1
    truncate -s 1M "$lab/original" || exit 1
    ln "$lab/original" "$lab/another-name" || exit 1
    stat -c '%n inode=%i links=%h size=%s blocks=%b' "$lab/"*
    du -B1 "$lab/original"
    du --apparent-size -B1 "$lab/original"
    printf 'Retained lab directory: %s\n' "$lab"
)
```

Both names should show the same inode and link count 2. Apparent size should be
1048576 bytes; allocated usage is usually much smaller. Exact allocation varies.
The lab was tested in a container and leaves its scratch files for inspection.

`df` reports filesystem-wide accounting; `du` walks reachable names and estimates
their allocation. Deleted-open files, permissions and mount boundaries can make
them disagree. For an investigation sequence rather than a second checklist,
continue with [disk-space troubleshooting](../troubleshooting/disk-space.md).

## Check your understanding

1. Why does adding a disk not automatically enlarge an existing filesystem?
2. Why do two hard-linked names not require two copies of the file data?
3. Why can a large apparent file size and low allocated usage both be correct?
