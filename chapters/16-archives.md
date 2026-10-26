# 16. Archives and compression

[Contents](../README.md) | [Previous: ssh](15-ssh.md)

An archive groups files into one container. Compression reduces the size of data using an algorithm. These are separate operations, though the common `.tar.gz` format combines a tar archive with gzip compression.

## Inspect an archive before extracting

```bash
tar -tzf backup.tar.gz
```

`tar` reads the archive. `-t` lists its members, `-z` handles gzip compression, and `-f` tells tar that the next argument is the archive filename. Listing does not extract files. Review member paths before extraction, especially when the archive comes from someone else; unexpected absolute paths or `..` path components can be dangerous.

## Create an archive

```bash
tar -czf notes.tar.gz notes/
```

`-c` creates an archive, `-z` compresses it with gzip, and `-f notes.tar.gz` names the output archive. `notes/` is the input directory. The command reads its contents and creates or replaces `notes.tar.gz` in the current directory. Check whether that output path already contains a file you need.

To extract, choose a new destination directory that you control, inspect the archive first, then use `tar -xzf archive.tar.gz -C destination/`. `-x` extracts and `-C` sets the destination directory. Extraction writes files and can overwrite names, so do not unpack an untrusted archive into a system directory or your working tree without reviewing its contents.

## Compression alone

`gzip file.txt` commonly compresses the file into `file.txt.gz` and removes the original pathname after successful compression. This changes the directory contents. To preserve the original, use `gzip -k file.txt` where the installed gzip supports `-k`, and verify with its help. `gunzip` reverses gzip compression. Neither tool is a substitute for a backup strategy.

## Common confusion

- `tar` groups files; gzip compresses a byte stream.
- Listing archive members is safer than extracting immediately.
- Extraction can overwrite existing files or create unexpected paths.
- Compression does not encrypt data or protect its contents from inspection.
- Verify important archives and keep backups separate from the source data.

## Further reading

- [GNU tar manual](https://www.gnu.org/software/tar/manual/)
- [GNU gzip manual](https://www.gnu.org/software/gzip/manual/)
