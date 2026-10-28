# 8. Disks and filesystems

[Contents](../README.md) | [Previous: resources](07-resources.md) | [Next: networking](09-networking.md)

You try to save a report and the program says “No space left on device.” You remove an old download, but the error remains. Perhaps the download and the report live on different storage. Perhaps the program has filled the filesystem with millions of tiny files. Perhaps a running process still holds a file you thought was gone.

The useful first question is not “What can I delete?” It is “Which storage is this program trying to use, and what has run out?” This chapter builds that answer from paths you already know. The inspection commands do not format, partition or mount anything. A small worked example creates ordinary files in a new directory so that you can see why a file's size and its storage use are different measurements.

## In this chapter

- [From a storage device to a path](#from-a-storage-device-to-a-path)
- [See the layout without changing it](#see-the-layout-without-changing-it)
- [Ask how much room a filesystem has](#ask-how-much-room-a-filesystem-has)
- [Build a small example you can measure](#build-a-small-example-you-can-measure)
- [A large file that uses little space](#a-large-file-that-uses-little-space)
- [Find where directory space is going](#find-where-directory-space-is-going)
- [When df and du disagree](#when-df-and-du-disagree)
- [Free bytes, but no room for another file](#free-bytes-but-no-room-for-another-file)
- [Why a deleted file can still occupy space](#why-a-deleted-file-can-still-occupy-space)
- [Work through a failed save](#work-through-a-failed-save)
- [Remove only the example files](#remove-only-the-example-files)
- [Further reading](#further-reading)

## From a storage device to a path

Suppose you keep a report at `/home/lee/reports/october.txt`. That path tells Linux how to find the file, but it does not identify a physical drive. Several layers connect the two.

A **disk**, in the broad sense used here, is a storage device: an SSD, a hard drive, or a virtual drive supplied to a virtual machine. It provides space where data can be stored. Unlike working memory, ordinary disk storage retains data across a shutdown.

A device can be divided into regions called **partitions**. Each partition has a defined range on the device. Dividing one SSD into two partitions does not create two independent SSDs. A failure of the SSD can affect both.

Inside a region, Linux needs a way to keep track of file contents, names, directories, ownership and free space. That organization is a **filesystem**. Ext4 and XFS are examples of filesystem types. A partition is a region of storage; a filesystem is the organization built on storage. They are not interchangeable names for the same thing.

Linux makes a filesystem accessible by attaching it to a directory in its existing directory tree. That attachment is a **mount**, and the directory where it appears is its **mount point**. Mounting connects existing storage to a path; it does not create the filesystem or erase it.

Here is one possible arrangement, not a description of your machine:

```text
one SSD
  partition 1: an ext4 filesystem attached at /
  partition 2: an ext4 filesystem attached at /home
```

`/` is the starting directory for absolute paths. In this example, `/etc/hosts` lives on the first filesystem, while `/home/lee/reports/october.txt` lives on the second. Following the report's path crosses the attachment at `/home`. If the `/home` filesystem fills up, free space on the `/` filesystem does not automatically become available to the report.

On another machine there might be no separate `/home` filesystem. Both paths would then use the filesystem mounted at `/`. A directory name alone cannot tell you which arrangement is in use.

A mount point also does not have to represent a local disk. A filesystem can come from another machine over a network, or use memory rather than persistent disk storage. Linux can place encryption or a flexible storage-allocation layer between a partition and a filesystem. The simple chain “disk, partition, filesystem, mount point” is useful, but it is not a requirement that every system follow it exactly.

One subtle consequence of mounting: files already in the mount-point directory are normally hidden while another filesystem is attached there. They have not been erased. Do not try to investigate this by mounting or unmounting storage on a running machine; changing an attachment can disrupt programs using that path.

## See the layout without changing it

On a machine with the util-linux tools installed, start with:

```bash
lsblk -o NAME,TYPE,SIZE,FSTYPE,MOUNTPOINTS
```

`lsblk` lists storage devices that Linux accesses in blocks, meaning chunks of data rather than individual characters. `-o` selects the output columns. The comma-separated list is one argument; there are no spaces between its column names.

This is **schematic output**, simplified to match the arrangement above:

```text
NAME   TYPE SIZE FSTYPE MOUNTPOINTS
sda    disk  80G
├─sda1 part  30G ext4   /
└─sda2 part  50G ext4   /home
```

Read the columns from left to right:

- `NAME` is the device's name. Indentation shows that `sda1` and `sda2` belong to `sda`.
- `TYPE` says whether the row is a whole disk, a partition (`part`), or another kind of storage object.
- `SIZE` is the capacity of that device or region, not the space currently free for your files.
- `FSTYPE` identifies a recognized filesystem or other storage format. A blank cell does not prove the storage is empty.
- `MOUNTPOINTS` shows where it is attached. A filesystem can have more than one attachment.

Other machines use names such as `nvme0n1` and `nvme0n1p1`. Older `lsblk` versions may require `MOUNTPOINT` instead of `MOUNTPOINTS`. Containers can show an incomplete or confusing view of the host's storage. Never choose a device to erase based on an example name.

Creating a filesystem, sometimes called formatting, writes new filesystem structures. A command such as `mkfs` can destroy access to existing data. Changing partitions can do the same. Neither operation is a remedy to try while investigating a full filesystem, and neither is part of this chapter.

To look at attachments rather than device layout, use:

```bash
findmnt
```

With no options, `findmnt` lists mounts, usually as a tree. Its `TARGET` column contains mount points; `SOURCE` identifies what supplies each filesystem. There can be many rows for special system filesystems. You do not need to interpret all of them to answer a question about one report.

A more focused query is:

```bash
findmnt --target /home --output TARGET,FSTYPE,OPTIONS
```

`--target /home` asks which mounted filesystem contains that path, even if `/home` is not itself a mount point. `--output` chooses three columns. `FSTYPE` is the filesystem type; `OPTIONS` lists settings separated by commas. `rw` means mounted read-write, while `ro` means mounted read-only. A read-write mount does not grant every user permission to write every file. Permissions still apply.

These commands describe the storage visible to your current environment. They do not test drive health or prove that the underlying hardware is reliable.

## Ask how much room a filesystem has

Use `df` when you want to know whether the filesystem containing a path has available space:

```bash
df -hT /home
```

`df` reports filesystem capacity. `-h` makes sizes easier to read with units such as `M` and `G`. GNU tools use powers of 1024 for this option: `M` represents a mebibyte, or 1,048,576 bytes. `-T` adds the filesystem type. The options can be combined as `-hT`; the final argument is the existing path to inspect.

**Schematic output:**

```text
Filesystem     Type  Size  Used Avail Use% Mounted on
/dev/sda2      ext4   50G   43G  4.0G  92% /home
```

Here is what this tells you:

- `Filesystem` is the reported source, not the name of your report.
- `Type` is `ext4` in this example.
- `Size` is the filesystem's reported total size.
- `Used` is space accounted as used by the filesystem.
- `Avail` is space available to ordinary users, not necessarily every free block.
- `Use%` is a rounded usage percentage.
- `Mounted on` is the attachment point that answers which filesystem you inspected.

Do not expect the displayed numbers to add up exactly. Human-readable figures are rounded, and some filesystems reserve space that ordinary users cannot allocate. GNU `df` bases its usage percentage on used space and space available to ordinary users, rounding upward. It is not measuring how much of the entire physical disk contains your files.

`df -hT /home/lee/reports` would report the same filesystem as `/home` in our example. It would **not** report the size of the `reports` directory. Without a path, `df -hT` gives a wider view of mounted filesystems, which can be useful but noisier.

A filesystem's usable capacity can also differ from the drive's advertised capacity because of filesystem bookkeeping, storage layers and allocation rules. Quotas, which limit a particular user or group, can prevent your write even while the filesystem has free space. Container storage limits can impose another boundary. Treat `df` as one part of the explanation, not a promise that a particular write will succeed.

## Build a small example you can measure

The next example writes about four mebibytes of actual file data plus a small note. It needs Bash and common GNU utilities. It does not use a device as a write destination, require administrator access, or make a filesystem.

Create a fresh directory in your home directory. This keeps the example away from system files and avoids depending on a machine-specific temporary directory:

```bash
work=$(mktemp -d "$HOME/storage-example.XXXXXX")
```

`mktemp` chooses a new name that is not already in use. `-d` creates a directory rather than a file. The final six `X` characters are a template: the program replaces them with a unique suffix. `$(...)` captures the command's printed result, and `work=` stores it in the shell variable `work`. Successful assignment normally prints nothing.

If the command reports an error, stop here and correct the scratch path. Do not continue with an unset or empty `work` variable.

```bash
printf '%s\n' "$work"
cd "$work"
```

`printf` prints the value so you can check it. Its format `%s\n` means “print a string, then a newline.” `"$work"` expands the variable as one argument, including any spaces in its value. `cd` moves into that directory. Check that it succeeds before continuing. The remaining relative paths are meant to stay inside this new directory.

Create a small report folder and a note:

```bash
mkdir reports
printf 'Storage notes\n' > reports/notes.txt
```

`mkdir` creates the subdirectory. This `printf` writes the words and a newline. The shell's `>` sends that output into the named file instead of the terminal. It would replace existing contents, which is why we are using a newly created directory rather than an important path.

A short text file can occupy more storage than its text length. Many filesystems allocate data in fixed-size pieces. Storing a few bytes may require one whole piece, with additional filesystem bookkeeping elsewhere. Now we will create the opposite situation: a long file with very little allocated data storage.

## A large file that uses little space

Run this only inside the new example directory:

```bash
truncate -s 64M reports/archive.img
```

`truncate` sets a file's length. `-s` introduces the desired size, and `64M` means 64 mebibytes here. The filename ends in `.img` simply as a name; this command has not created a working disk image or filesystem.

The file did not exist before this command. Extending a new file this way allows the filesystem to represent the unwritten region without allocating a data block for every byte. Reading that region produces zero bytes. Such an unwritten region is called a **hole**, and a file containing holes is called a **sparse file**.

Do not try this command on a real archive. Setting an existing file to a shorter length discards the contents beyond the new end.

Create another file with actual writes for comparison:

```bash
dd if=/dev/zero of=reports/written.img bs=1M count=4 status=none
```

`dd` copies data using the `name=value` arguments shown here:

- `if=/dev/zero` selects the input. `/dev/zero` is a special source that produces zero bytes when read. We are reading from it, not writing to a disk device.
- `of=reports/written.img` selects the output file inside our new directory. This is the destination that must be checked carefully.
- `bs=1M` requests chunks of one mebibyte.
- `count=4` copies four such chunks and then stops.
- `status=none` suppresses the usual progress and summary messages; errors are still reported.

Both files read as zeros, but we created them differently. Compare their lengths:

```bash
ls -lh reports/archive.img reports/written.img
```

`ls` lists the two files. `-l` requests the detailed format, which includes permissions, owner, size and modification time. `-h` makes its size column human-readable. The size column should show `64M` for `archive.img` and `4.0M` for `written.img`. The other fields depend on your account and machine.

This size is the file's **apparent size**: its length as a program reading from beginning to end would see it. Now ask about allocated storage instead:

```bash
du -h reports/archive.img reports/written.img
```

`du` reports the storage accounted to the named files. `-h` again formats sizes in readable units. This output was **observed in the local scratch example on ext4**:

```text
0       reports/archive.img
4.0M    reports/written.img
```

The 64-mebibyte file has no allocated data blocks in this result. The zero does not mean that creating it had absolutely no filesystem cost: its name and file record still need bookkeeping. The four-mebibyte file has allocated space because `dd` wrote its contents.

Ask `du` to measure apparent size instead:

```bash
du --apparent-size -h reports/archive.img reports/written.img
```

`--apparent-size` changes what is measured; it is not merely another display format. **Observed output:**

```text
64M     reports/archive.img
4.0M    reports/written.img
```

This is the difference to remember: file length describes how much content a reader sees; allocated storage describes space charged to storing it. A sparse file can have a large length without occupying the same amount of storage yet. Writing into its holes can increase its storage use later without changing its length.

Your allocated figures can differ. Filesystem block sizes, transparent compression and shared storage between files affect accounting. Copying a sparse file may preserve its holes, or may write them out as ordinary zeros, depending on the copy method and destination. A sparse file is not a guarantee that an eventual copy will fit elsewhere.

## Find where directory space is going

We have measured individual files. To measure the directory as a whole, use:

```bash
du -sh reports
```

`-s` means summarize: print one total for this argument instead of a line for every visited subdirectory. `-h` formats that total. **Observed output for the example:**

```text
4.1M    reports
```

The total includes the written file, the note and directory storage. Human-readable rounding explains why a total just above four mebibytes can print as `4.1M`.

Compare it with:

```bash
du --apparent-size -sh reports
```

**Observed output:**

```text
69M     reports
```

The directory now includes the sparse file's full apparent length. The total also includes other entries and is rounded. Do not infer exact byte counts from either human-readable total.

For a larger directory, one summary may leave you asking which subdirectory is responsible. GNU `du` can show one level at a time:

```bash
du -h --max-depth=1 .
```

`.` means the current directory. `--max-depth=1` asks for the starting directory and its immediate subdirectories, not a printed line for every deeper directory. **Observed output in our example:**

```text
4.1M    ./reports
4.1M    .
```

The first row is the subdirectory. The second is the total including it. These are nested totals, not separate piles of storage to add together.

Limiting the displayed depth does **not** limit how deeply `du` must walk to compute those totals. On a real system, start with a relevant, bounded directory, such as your own reports folder, rather than scanning `/`. Walking millions of files can take time and compete with normal work.

If a scan says `Permission denied`, its total may be incomplete. That message means the program could not inspect part of the tree, not that the inaccessible directory is empty. Do not immediately repeat an expensive whole-machine scan with `sudo`. First decide whether the omitted paths matter and whether you are authorized to inspect them.

## When df and du disagree

These tools answer different questions:

| Question | Tool |
| --- | --- |
| How much room is available on the filesystem holding this path? | `df -hT path` |
| How much allocated storage can I account for under this directory? | `du -sh path` |
| What is the apparent length of the files under this directory? | `du --apparent-size -sh path` |

Replace `path` with an actual existing path. Do not type it literally unless that is your directory's name.

Even without unusual files, a directory total should not equal an entire filesystem's used space. Other directories on that filesystem use space too. To compare measurements meaningfully, identify the filesystem first and make sure the directory scan covers the area you intend.

Several additional differences matter:

- **Filesystem bookkeeping:** allocation maps and other internal structures need space but are not ordinary files for `du` to add up.
- **Hard links:** more than one filename can refer to the same underlying file. GNU `du` normally counts that file once within a run. Totals from separate runs on different directories can therefore overlap.
- **Mounts inside a directory tree:** a recursive walk can enter another mounted filesystem. GNU `du -xsh path` adds `-x`, meaning stay on the filesystem of the starting argument. It helps avoid mixing totals from separate filesystems, but does not solve every case, such as multiple attachments of the same filesystem.
- **Snapshots and shared data:** storage retained by snapshots or shared between files may not correspond to a simple sum of visible file sizes. Use filesystem-specific reporting when the system uses those features.
- **A changing system:** a program can write or remove files between measurements. The two commands are not an atomic snapshot taken at the same instant.

Deleted files that remain open deserve their own explanation below. They are a particularly useful reason not to treat a mismatch as proof that either tool is broken.

## Free bytes, but no room for another file

A filesystem needs both space for contents and records describing its objects. On common Linux filesystems, one such record is called an **inode**. It stores information such as file type, ownership, permissions and where the file's data is located. Directory entries associate names with those records; the inode itself does not store the filename.

Consider a program creating a new tiny temporary file for every request and never clearing old ones. Each file needs a record even if its contents are empty. On a filesystem with a limited supply of inodes, that program can consume the available records before it consumes the available data space. A new file cannot be created just because there are bytes left for its contents.

Use an existing affected path:

```bash
df -i /home
```

`-i` changes the report from data-space usage to inode usage. **Schematic output for inode exhaustion:**

```text
Filesystem     Inodes  IUsed IFree IUse% Mounted on
/dev/sda2      200000 200000     0  100% /home
```

`Inodes` is the reported total number of records, `IUsed` the used count, and `IFree` the available count. `IUse%` is the usage percentage. Here the zero in `IFree` is important even if `df -hT /home` reports free bytes.

Not all filesystems manage or report inodes in the same way. Some allocate records dynamically, and some special filesystems do not provide useful counts through this interface. Interpret the numbers alongside the filesystem type rather than assuming every filesystem has a fixed inode table.

If you need to narrow down which directory contains many objects, a GNU `du` option changes the measurement:

```bash
du --inodes --max-depth=1 /home/lee/reports
```

This is a conditional example: use a real directory that you own or are authorized to inspect. `--inodes` asks for inode usage rather than byte usage. `--max-depth=1` gives the same one-level presentation as before. Large counts point toward directories worth investigating; the command still has to traverse their contents and may be slow.

Do not create enough files to reproduce exhaustion on a shared filesystem. Do not remove a broad wildcard of files as a repair. Identify what is creating them and what retention or cleanup procedure the application supports. Otherwise the files may immediately return, or you may erase information the application needs.

## Why a deleted file can still occupy space

Imagine a program writing a log. It opens the log once and keeps using that open connection to the file. Removing the log's name from its directory does not necessarily close the program's connection.

Linux separates these two events:

1. The last directory name for the file is removed. A normal directory walk can no longer find it.
2. The last process holding the file open closes it. Its remaining storage can then be reclaimed, assuming nothing else retains it.

Between those events, `du` cannot count the file through its old directory entry, while `df` still accounts for its allocated storage. The process may even keep writing, causing the apparently missing file to grow.

This is why deleting a busy log is not a reliable way to free its space. The application needs to close or reopen the file through an appropriate procedure. Proper log rotation coordinates naming and reopening rather than merely removing a name.

Where installed, the following read-only command can help investigate:

```bash
lsof +L1
```

`lsof` lists files held open by processes. Its `+L1` selector requests files whose link count is below one, meaning there are no remaining directory hard links. Unlike a typical short option, this selector begins with `+`.

Common columns include `COMMAND` for the program name, `PID` for its process number, `FD` for the open file reference within that process, and `NAME` for a displayed path or description. A removed path may have `(deleted)` appended. Exact columns and visibility vary. Ordinary users may see only some processes; container boundaries and access restrictions can hide others. No output is not proof that the whole host has no deleted-open files.

If the shell reports `lsof: command not found`, the diagnostic tool is not installed. That is separate from the storage problem. Use the system's approved software-installation process if you need it; do not assume an unavailable diagnostic means there are no open files.

Do not terminate a process just because it appears in this listing. A restart can interrupt service or lose work. Identify the application and follow its documented reopen, rotation or restart procedure with the service owner. Directly truncating a live file can also lose data and produce surprising results while a writer remains active. Neither action belongs in a blind disk-cleanup recipe.

## Work through a failed save

Return to the report that would not save. First identify the existing directory into which the program writes. The new filename might not exist yet.

Our scratch example can show why that matters:

```bash
df -hT reports/missing.txt
```

**Observed error:**

```text
df: reports/missing.txt: No such file or directory
```

The command failed because it was asked about a nonexistent path. This does not tell you whether the filesystem is full. Ask about the existing parent directory instead:

```bash
df -hT reports
```

The result describes the filesystem containing `reports`, including a `Mounted on` path that may be far above the scratch directory. Its numbers depend on your machine, so no fixed capacity output is expected here.

For an actual failed save, continue in this order:

1. **Check the path and attachment.** Use `findmnt --target` with the existing destination directory. Is it the filesystem you expected? If a removable or network filesystem is absent, writing into its usual directory could instead be using the filesystem underneath.
2. **Check available data space.** Run `df -hT` with that directory. Little available space supports a capacity problem. A different filesystem with lots of space does not resolve it.
3. **Check file records.** Run `df -i` with the same directory. High inode usage suggests investigating many small files rather than only hunting for a large download.
4. **Measure a relevant directory.** Use `du -sh`, then a one-level view if needed. Read any errors. Do not assume the largest visible file caused the failure, or that it is safe to remove.
5. **Explain any remaining mismatch.** Consider deleted-open files, inaccessible paths, quotas, snapshots and storage limits. If the filesystem is mounted read-only, deleting something is not the remedy.

An error such as `Permission denied` is a different starting point from `No space left on device`. A save can also fail because an application writes temporary data elsewhere before moving it into place. If the obvious destination has room, find out where the application actually failed to write rather than repeatedly deleting files from the destination.

The goal is an explanation tied to a path, a filesystem and a specific constraint. Only then is it sensible to plan cleanup, adjust retention or request more capacity.

## Remove only the example files

If you followed the scratch example, first make sure you are still in its unique directory:

```bash
pwd
printf '%s\n' "$work"
```

`pwd` prints the current directory. Compare it with the saved value. If either path is unexpected, stop rather than running a deletion command somewhere else.

After confirming the directory, remove only the three files this example created:

```bash
rm -- reports/notes.txt reports/archive.img reports/written.img
rmdir reports
```

`rm` removes the named files. `--` marks the end of options, so subsequent arguments are treated as filenames. There is no wildcard and no recursive removal. `rmdir` removes a directory only when it is empty; unexpected extra files make it refuse rather than delete them.

Finally leave the directory before removing it:

```bash
cd ..
rmdir "$work"
```

`..` is the parent directory. The final command uses the saved absolute path and again removes only an empty directory. This cleanup was checked on the disposable scratch files. No live logs, application files or device contents were removed.

## Further reading

- [GNU Coreutils: df invocation](https://www.gnu.org/software/coreutils/manual/html_node/df-invocation.html)
- [GNU Coreutils: du invocation](https://www.gnu.org/software/coreutils/manual/html_node/du-invocation.html)
- [GNU Coreutils: truncate invocation](https://www.gnu.org/software/coreutils/manual/html_node/truncate-invocation.html)
- [util-linux: findmnt](https://man7.org/linux/man-pages/man8/findmnt.8.html)
- [Linux man-pages: inode(7)](https://man7.org/linux/man-pages/man7/inode.7.html)
- [Linux man-pages: unlink(2), removal of a name and the lifetime of an open file](https://man7.org/linux/man-pages/man2/unlink.2.html)
- [util-linux: lsblk(8)](https://man7.org/linux/man-pages/man8/lsblk.8.html)
