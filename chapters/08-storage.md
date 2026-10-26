# 8. Disks and filesystems

[Contents](../README.md) | [Previous: resources](07-resources.md) | [Next: networking](09-networking.md)

A disk is a storage device. A filesystem organizes data on a device or another storage source. Linux makes filesystems available by attaching them into the directory tree at mount points. The root filesystem and the storage device are related but not the same thing.

## Inspect the device layout

On systems with util-linux, list block devices and selected fields:

```bash
lsblk -o NAME,TYPE,SIZE,FSTYPE,MOUNTPOINTS
```

`-o` selects columns: device name, kind, size, filesystem type and mount points. A disk can contain partitions, and a filesystem can sit above logical volumes or encrypted devices rather than directly on a partition. A network filesystem may appear in mount output without a corresponding local block device. Older versions may require `MOUNTPOINT` instead of `MOUNTPOINTS`.

For example, a disk named `sda` might contain `sda1` mounted at `/boot` and another partition used by a logical volume mounted at `/`. These names are illustrative: never select a device for formatting based on an example name. `mkfs` creates filesystem structures and can destroy existing data. This chapter inspects storage; it does not walk through repartitioning or formatting a real device.

## Check filesystem capacity

```bash
df -hT
```

`df` reports space for mounted filesystems. `-h` uses human-readable units; `-T` includes the filesystem type on implementations that support it. The `Use%` column is the percentage of accounted usable space already used, rounded up. GNU df calculates it from used blocks and blocks available to unprivileged users, so reserved space affects the denominator. It is not the percentage of an entire physical disk that contains files. Reserved blocks, filesystem metadata, snapshots, quotas and container limits can make observed capacity differ from a simple device size.

To check one path, pass it as an argument:

```bash
df -hT /var
```

This reports the filesystem containing `/var`. It does not say how much space a particular directory consumes.

## Find directory size

```bash
du -sh /var/log
```

`du` estimates space used by files reachable under the named directory. `-s` summarizes instead of listing each subdirectory; `-h` formats the size. The result can differ from `df` because of deleted-but-open files, hard links, sparse files, snapshots, permissions, mount boundaries and accounting units. If access is denied, the result may be incomplete. Do not add `sudo` until you know why the omitted paths matter.

To locate large files, first inspect a bounded part of the tree and narrow the target. A recursive full-filesystem scan can be expensive and produce permission errors. On a busy system, prefer targeted paths and coordinate any expensive scan with the system owner.

## Inodes and deleted-open files

Filesystems track file data and file metadata separately. An inode is a filesystem record for an object. A filesystem can have free data blocks but no free inodes, preventing creation of new files. `df -i` reports inode usage where supported:

```bash
df -i /var
```

If inode use is exhausted, investigate directories containing very many small files. Do not remove files by broad wildcard until you have identified what created them and whether an application owns them.

A file removed from its directory can continue consuming space while a process has it open. `df` may show less free space than `du` accounts for. Tools such as `lsof` can help locate deleted-open files, but may be missing or restricted. Restarting a process to release a file is a state change and can interrupt service; plan it with the service owner.

## Mounts

```bash
findmnt
```

`findmnt` lists mounted filesystems and their mount points on systems that provide util-linux. It helps explain which filesystem contains a path and whether a mount is read-only. Container views may omit host details. Reading mount output does not establish the health of the underlying storage device.

## Common confusion

- `df` answers capacity for a filesystem; `du` estimates usage under a directory.
- A filesystem can run out of inodes while some blocks remain free.
- Deleted files held open can occupy space not visible in a directory walk.
- A mount point is a directory in the tree, not necessarily a separate physical disk.
- `du` output can be incomplete when access or mount boundaries limit traversal.

## Further reading

- [GNU Coreutils: df invocation](https://www.gnu.org/software/coreutils/manual/html_node/df-invocation.html)
- [GNU Coreutils: du invocation](https://www.gnu.org/software/coreutils/manual/html_node/du-invocation.html)
- [util-linux: findmnt](https://man7.org/linux/man-pages/man8/findmnt.8.html)
- [Linux man-pages: inode(7)](https://man7.org/linux/man-pages/man7/inode.7.html)
- [util-linux: lsblk(8)](https://man7.org/linux/man-pages/man8/lsblk.8.html)
