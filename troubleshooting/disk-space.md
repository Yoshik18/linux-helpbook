# Disk full: find the filesystem before deleting files

A service can report `No space left on device` even when another mounted
filesystem has plenty of room. Start with the path the service writes to.
The checks below inspect state. Do not delete logs, databases or caches just to
make a number smaller.

## 1. Check capacity and inodes

```bash
# Replace /var with the actual failing directory.
df -h /var
df -i /var
```

`df -h` reports filesystem capacity; `df -i` reports inode usage. A workload that
creates many tiny files can exhaust inodes before filling available bytes.
These commands do not identify which directory owns the space.

## 2. Measure the same filesystem

```bash
du -x -h --max-depth=1 /var
```

On GNU `du`, `-x` stays on one filesystem. Inspect the largest relevant directory
next, rather than repeatedly scanning the whole host. Permission errors mean the
result is incomplete. Get narrowly approved access if you need more visibility.

Pass a directory itself rather than `*`: ordinary shell globbing misses hidden
entries. Human-readable sizes are convenient but not precise accounting. If you
need additive totals or machine sorting, use one byte-based traversal:

```bash
du -x -B1 --max-depth=1 /var | sort -nr
```

Hard links share data. `du` normally counts a shared inode once per invocation,
so adding separate overlapping scans can overcount. Sparse files can have a large
apparent length but use fewer allocated blocks. See `du --apparent-size` when
investigating that distinction, not as a replacement for physical usage.

## 3. If df and du disagree

Possible causes include a deleted file still held open, permission gaps, reserved
filesystem space, snapshots, files hidden beneath a mount, or measurement while
files are changing. A disagreement alone does not prove a leak.

If `lsof` is installed and your access permits it:

```bash
lsof +L1
```

Look for deleted regular files on the affected filesystem. The output includes
process and file details that may be sensitive. A deleted open file may retain
storage until the last reference closes. Coordinate with the service owner before
restarting anything; do not truncate an arbitrary descriptor under `/proc`.

## Try it yourself

This creates a 1 MiB file inside a new temporary directory. It needs Bash and
standard Linux utilities, but no root access. It does not fill a filesystem.

```bash
lab=$(mktemp -d) || exit 1
mkdir "$lab/.cache"
dd if=/dev/zero of="$lab/.cache/sample.bin" bs=1024 count=1024 status=none
du -h --max-depth=1 "$lab"
df -h "$lab"
printf 'Lab directory: %s\n' "$lab"
```

You should see the hidden `.cache` directory in `du` and the containing
filesystem in `df`. Allocation and displayed rounding vary by filesystem. Clean
up only this temporary directory after checking the printed path.

## Interview takeaway

- How can a host have free bytes and still fail to create files?
- Why does deleting a large log not always free its storage immediately?

## Further reading

- [`df(1)`](https://man7.org/linux/man-pages/man1/df.1.html)
- [`du(1)`](https://man7.org/linux/man-pages/man1/du.1.html)
- [`unlink(2)` and open files](https://man7.org/linux/man-pages/man2/unlink.2.html)

[Back to the learning path](../README.md)
