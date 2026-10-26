# 7. Find disk usage and inspect filesystems

Start with the directory that cannot be written, not with random deletion.
Use the [practice directory](01-how-linux-works.md) for write examples.

## Check bytes and inodes on the affected filesystem

```bash
df -h "$LINUX_LAB"
df -i "$LINUX_LAB"
findmnt -T "$LINUX_LAB"
lsblk -o NAME,TYPE,SIZE,FSTYPE,MOUNTPOINTS
```

`df -h` shows filesystem capacity; `df -i` checks inodes. Many tiny files can
exhaust inodes before bytes. `findmnt -T` identifies the mount containing a path;
`lsblk` shows visible block-device layers, not every network or overlay mount.
Older util-linux versions may need `MOUNTPOINT` instead of `MOUNTPOINTS`.

## Find which directory owns the usage

```bash
du -x -h --max-depth=1 "$LINUX_LAB"
du -x -B1 --max-depth=2 "$LINUX_LAB" | sort -nr | head -n 10
find "$LINUX_LAB" -type f -size +1M -printf '%s %p\n'
```

`du -x` stays on the same filesystem. Passing the directory includes hidden
entries; an ordinary `*` glob does not. `-B1` gives allocated byte accounting
for numeric sorting. `find -printf` is GNU syntax and prints logical file size
here, which may differ from allocated blocks. Permission errors mean incomplete
results. On a real host, narrow the target before doing a large tree walk.

## See why apparent size can mislead

```bash
truncate -s 1M "$LINUX_LAB/data/sparse.bin"
stat -c 'length=%s blocks=%b block-unit=%B' "$LINUX_LAB/data/sparse.bin"
du -B1 "$LINUX_LAB/data/sparse.bin"
du --apparent-size -B1 "$LINUX_LAB/data/sparse.bin"
```

The logical size is `1048576` bytes. Allocated usage is usually smaller because
the hole reads as zeros without allocating every data block. Exact allocation
depends on the filesystem. Hard links, compression and copy-on-write sharing
also complicate adding directory totals from separate scans.

## Inspect a deleted file that remains open

This block creates and removes only its own small lab file. An open descriptor
keeps it readable until closed; do not apply this removal to a service log.

```bash
(
    printf 'still open\n' > "$LINUX_LAB/data/open-demo.txt"
    exec 3< "$LINUX_LAB/data/open-demo.txt"
    rm -- "$LINUX_LAB/data/open-demo.txt"
    readlink "/proc/$BASHPID/fd/3"
    cat <&3
    exec 3<&-
)
```

`cat` still prints `still open`, and the descriptor target normally ends in
`(deleted)`. `$BASHPID` identifies this Bash subshell; `$$` can still identify
its parent. On a real investigation, `lsof +L1` can
identify deleted-open files if installed and permitted. Do not truncate unknown
descriptors or restart a database just to recover space.

## Know where inspection ends

A disk, a partition, an LVM logical volume and a filesystem are different layers.
`lsblk`, `findmnt`, and approved LVM queries help map them. Growing one layer does
not automatically grow the others. This guide does not give a generic `mkfs`,
partition deletion or live resize command: the correct operation depends on the
actual device, filesystem, backups and recovery plan.

## Practice

Find the filesystem containing the practice logs, then compare the sparse file's
allocated and apparent sizes. Explain which number answers “disk space used.”

<details>
<summary>One answer</summary>

```bash
findmnt -T "$LINUX_LAB/logs"
du -B1 "$LINUX_LAB/data/sparse.bin"
du --apparent-size -B1 "$LINUX_LAB/data/sparse.bin"
```

</details>

[Manual: du](https://man7.org/linux/man-pages/man1/du.1.html)
· [df](https://man7.org/linux/man-pages/man1/df.1.html)
· [unlink and open files](https://man7.org/linux/man-pages/man2/unlink.2.html)
· [Disk-space checklist](../troubleshooting/disk-space.md)
· [Previous](06-memory-and-cpu.md) · [Index](README.md) · [Next](08-boot-services-and-logs.md)
