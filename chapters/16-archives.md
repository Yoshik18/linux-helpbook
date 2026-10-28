# 16. Archives and compression

[Contents](../README.md) | [Previous: ssh](15-ssh.md)

Suppose you want to send someone a folder of notes, or keep a copy before changing it. Sending each file separately is inconvenient. You also need the files to arrive with their names and folder arrangement intact. One file containing the whole folder is easier to move, inspect and restore.

This chapter builds that file, looks inside it without unpacking it, restores it somewhere safe, and checks that the restored contents match. All the files in the example are disposable. You do not need administrator privileges.

## In this chapter

- [Packing files is different from making them smaller](#packing-files-is-different-from-making-them-smaller)
- [Make a small folder to pack](#make-a-small-folder-to-pack)
- [Create and list an uncompressed archive](#create-and-list-an-uncompressed-archive)
- [Add compression without removing the notes](#add-compression-without-removing-the-notes)
- [Understand the paths inside the archive](#understand-the-paths-inside-the-archive)
- [Restore into a fresh directory](#restore-into-a-fresh-directory)
- [Compare the restored files](#compare-the-restored-files)
- [Compress one file and keep the original](#compress-one-file-and-keep-the-original)
- [Treat unfamiliar archives as unfamiliar files](#treat-unfamiliar-archives-as-unfamiliar-files)
- [Know what an archive does not protect](#know-what-an-archive-does-not-protect)
- [Remove the practice files](#remove-the-practice-files)
- [Further reading](#further-reading)

## Packing files is different from making them smaller

Putting several files and directories into one file is called **archiving**. An archive records their names, contents and some information about them, such as modification times and permissions. The `tar` program makes and reads a common kind of archive, usually named with a `.tar` ending.

Making data take up less space is called **compression**. A compression program finds ways to represent repeated patterns more compactly. Decompression reverses that representation so that other programs can read the original bytes again. `gzip` is one such program, and `.gz` is its usual filename ending.

These jobs are separate:

- `notes.tar` can hold a folder and its files without compressing them.
- `todo.txt.gz` contains a compressed file's data. It is not a folder containing independently named files.
- `notes.tar.gz` is a tar archive whose data has then been compressed with gzip. `.tgz` is another common ending for this combination.

Think of the tar archive as the packing arrangement and gzip as a way of storing that arrangement more compactly. To recover the files from `.tar.gz`, the compression must be reversed and the archive unpacked. `tar` can arrange both operations in one command.

Compression does not guarantee a smaller result. Tiny files have little data to save, and formats such as JPEG images are already compressed. Extra format information may even make the compressed result larger. Neither archiving nor compression encrypts the contents.

## Make a small folder to pack

Use one Bash terminal for the example so that its variable and current directory remain available between commands. First ask `mktemp` to create a new, uniquely named directory:

```bash
work=$(mktemp -d)
cd "$work"
```

`mktemp -d` creates a directory rather than a file and prints its path. The shell's `$(...)` runs the enclosed command and captures that printed path. `work=` stores it in a variable named `work`; there are no spaces around the equals sign. `cd` changes your current directory. Quoting `"$work"` makes the path one argument even if it contains spaces.

If creation or `cd` reports an error, stop and resolve it before continuing. Otherwise, subsequent relative paths will refer to this new directory. Its location depends on your system's temporary-directory settings. Keep this terminal open: the cleanup at the end uses the same variable.

Create a directory named `notes` and two small text files:

```bash
mkdir notes
printf 'Read chapter 16\nKeep a second copy\n' > notes/todo.txt
printf 'Meeting: Friday\n' > "notes/meeting notes.txt"
```

`mkdir` creates the directory. `printf` writes the supplied text; each `\n` in its quoted format becomes a newline. The shell's `>` directs that output into a file instead of the terminal. It creates a missing file and **replaces the contents of an existing file**, which is why we are using a new practice directory.

The second filename contains a space. The double quotes make `notes/meeting notes.txt` one path, not two arguments. These commands normally print nothing. You now have a `notes` directory containing a two-line to-do file and a one-line meeting file.

## Create and list an uncompressed archive

Start without compression so that the packing step is visible:

```bash
tar -cf notes.tar notes/
```

Read this as “create an archive called `notes.tar`, using `notes/` as the input.” The grouped letters after `-` are separate options:

- `-c` means **create** an archive.
- `-f` means the next argument is the archive **file**, here `notes.tar`.
- `notes/` is the directory to include, together with the files below it.

The output archive is alongside `notes`, not inside it. That avoids asking tar to include its own changing output. Creation reads the notes; it does not remove or move them. It normally prints nothing. Creating an archive at an existing output path can replace that archive, so choose a new name when keeping older copies matters.

Now list what was stored:

```bash
tar -tf notes.tar
```

`-t` lists the archive's entries, also called its **members**. `-f` still names the archive to read. In the worked example, this printed:

```text
notes/
notes/meeting notes.txt
notes/todo.txt
```

Your file order may differ. The important details are the names and the `notes/` prefix. The directory itself has an entry, and the two files have entries beneath it. Listing reads the archive without extracting any of those entries.

Create, list and extract are different operations. Choose one main operation for each tar command; do not combine `-c`, `-t` and `-x` in the hope of doing everything at once. Also keep the archive filename immediately after the group ending in `f`, as these examples do. The position of that filename matters.

## Add compression without removing the notes

Create a second archive from the same input:

```bash
tar -czf notes.tar.gz notes/
```

The new `-z` tells GNU tar to use gzip compression. Tar collects the named directory into an archive and passes that data through gzip. The result is `notes.tar.gz`; the original directory and the earlier `notes.tar` remain in place.

The ending is a useful description for people, not an instruction to the program. Merely renaming `notes.tar` to `notes.tar.gz` would not compress it. Here, `-z` is what requests compression.

List the compressed archive before doing anything that writes its contents back to disk:

```bash
tar -tzf notes.tar.gz
```

This combines **list**, **gzip** and **archive file**. It printed the same three names as the uncompressed listing above. That is expected: compression changed how the archive's data was stored, not which files were included.

A successful listing confirms that tar could read the archive well enough to enumerate its entries. It is useful inspection, not proof that the source selection was correct or that every restored file will be usable. The restoration and comparison below answer a stronger question.

## Understand the paths inside the archive

`notes/todo.txt` does not begin with `/`. It is a **relative path**: it describes a location starting from some chosen directory, rather than from the top of the whole filesystem.

We gave tar `notes/` rather than an absolute path to the practice directory. As a result, the archive can be restored under a different parent directory without needing the same machine layout. If you extract into `restored`, its stored name `notes/todo.txt` becomes `restored/notes/todo.txt`.

Tar's `-C` option chooses the directory from which it works. During extraction, it lets you select the parent of the restored paths without first changing the shell's current directory. It does not remove the `notes/` prefix from those paths, and it does not create the destination directory for you.

During creation, `-C` can also choose where subsequent input names are looked up. Its position matters because it affects the names that follow it. That is useful when packing files from another directory, but first keep the basic distinction clear: the archive's stored names and the directory you extract into are two different parts of the final location.

GNU tar has protections against some dangerous path forms, including default handling of leading `/` and `..` components. Do not disable those protections to make an unfamiliar archive extract. A path containing `..` can refer to a parent directory; an absolute path can identify a location outside the intended destination. These are reasons to stop and investigate, not reasons to add forceful options.

## Restore into a fresh directory

Extraction creates directories and writes files. Existing files with matching names can be overwritten. Start with a new destination that contains nothing valuable, rather than extracting into your home directory or a project you are editing.

Here is a common mistake, deliberately shown while the destination does not yet exist:

```bash
tar -xzf notes.tar.gz -C restored
```

`-x` means **extract**. `-z` handles gzip and `-f notes.tar.gz` identifies the input archive. `-C restored` asks tar to work inside `restored` before creating its entries.

The observed error was:

```text
tar: restored: Cannot open: No such file or directory
tar: Error is not recoverable: exiting now
```

This does not mean the archive is damaged. Tar could not enter the destination because we had not made it. The command returned failure status `2`; no files were restored by that attempt.

Correct the missing directory and try again:

```bash
mkdir restored
tar -xzf notes.tar.gz -C restored
```

If `mkdir` fails, do not continue with the extraction. In particular, an “already exists” message means this is no longer the fresh destination expected by the example. Inspect it or choose another new name first.

On success, both commands are quiet. The shell stays in the practice directory, while tar writes `restored/notes/meeting notes.txt` and `restored/notes/todo.txt`. The extra `notes` directory is not an accidental duplicate: it comes from the paths listed inside the archive.

## Compare the restored files

An archive that can be listed is not yet a demonstrated restore. We can go further because the originals still exist. `cmp` reads two files and compares their bytes, the individual units of their contents:

```bash
cmp notes/todo.txt restored/notes/todo.txt
cmp "notes/meeting notes.txt" "restored/notes/meeting notes.txt"
```

Both comparisons completed successfully with no output in the example. For `cmp`, silence together with success status `0` means the bytes match. A content difference produces a message and status `1`; an error such as a missing input produces a different failure status. If a comparison fails, read the message rather than treating all failures as corruption.

These checks show that both files survived the pack-and-restore round trip unchanged. They do not compare ownership, permissions or timestamps, and they do not prove that you remembered every file you intended to save. For a larger directory, checking only two selected files would not establish that the whole tree matched.

GNU tar can also compare an archive against files on disk:

```bash
tar -dzf notes.tar.gz
```

Here `-d` means compare, not decompress. From the current practice directory, tar uses the stored names to locate `notes/` and its files. This check also completed quietly and successfully. It checks recorded file information as well as contents, but it compares against the **original** `notes` here, not against `restored/notes`. That is why the explicit `cmp` commands are still useful evidence about the restored files.

If you edit a source file after packing it, the archive still contains the earlier version. A later difference may be exactly what a saved snapshot should show. Always be clear about which version and which directory you are comparing.

## Compress one file and keep the original

Sometimes there is no folder to pack: you only want a compressed copy of one large text file. Gzip can do that directly. Its default behavior needs care: successful in-place compression normally replaces the input pathname with a `.gz` file. Decompression with `gunzip` normally reverses that replacement.

Use `-k`, meaning **keep**, when you want the input to remain. First use `cp` to copy our to-do file into a separate disposable file:

```bash
cp notes/todo.txt note-copy.txt
gzip -k note-copy.txt
```

`cp` reads its first path and writes a copy at the second. The gzip command then creates `note-copy.txt.gz` while retaining `note-copy.txt`. Neither operation changes `notes/todo.txt`. These commands normally print nothing. This chapter uses GNU gzip; on a different implementation, check its documented options before relying on `-k`.

Gzip can test whether the compressed data passes its integrity checks without writing a decompressed file:

```bash
gzip -t note-copy.txt.gz
```

Here `-t` means **test**, not tar's list operation. The command completed without output and returned success. An integrity check can detect many kinds of accidental damage, but it is not encryption, proof of who created the file, or proof that it contains the right information.

Keeping the original introduces a predictable name collision. Consider:

```bash
gunzip -k note-copy.txt.gz
```

`gunzip` decompresses; `-k` would retain its compressed input. But its usual output name, `note-copy.txt`, already exists because we deliberately kept it. In a noninteractive run, the observed message was:

```text
gzip: note-copy.txt already exists;	not overwritten
```

The command returned status `2`. In a terminal, gzip may instead ask whether to overwrite the existing file. Decline that request. Do not add a force option just to silence a useful protection.

Choose a different output name instead:

```bash
gunzip -c note-copy.txt.gz > roundtrip.txt
cmp note-copy.txt roundtrip.txt
```

For gzip and gunzip, `-c` writes the resulting data to standard output, the output stream that normally goes to your terminal, while keeping the input file. It does **not** mean tar's “create.” The shell's `>` sends that stream into `roundtrip.txt`. That is a new name in this example; using an existing filename would truncate it before gunzip runs. Redirection is not an overwrite safeguard, and a failed decompression can leave an empty or partial output file.

The final `cmp` completed successfully without output: the decompressed bytes matched the retained original. This approach leaves the original, the compressed copy and the separately named decompressed copy available for inspection.

## Treat unfamiliar archives as unfamiliar files

The example is relatively straightforward because you created the archive from two known files. Downloading an archive from somebody else changes the decision. Listing it first helps you decide whether its names and layout are expected, but a fresh destination is not a security sandbox.

Look for entries outside the expected top-level folder, absolute paths, parent-directory components such as `..`, and unexpectedly large collections. A detailed listing, requested with tar's additional `-v` option, also shows information such as file types and links. A symbolic link is a name that refers to another path; an archive can contain these as well as ordinary files. Link behavior and unusual entry types can complicate where extraction writes data.

A listing is therefore a screening step, not a safety certificate. Deceptive names, links, huge expanded sizes and bugs in extraction software are further reasons not to unpack an archive merely because a brief listing looked harmless. Compressed data can expand enough to fill a disk. A private empty directory helps avoid accidental name collisions, but it does not impose disk limits or remove your account's access to other files.

For an archive you do not trust, obtain a trusted copy or ask for help using an appropriately isolated environment with storage limits. Do not extract it as root or into system directories. Do not run programs or scripts from it simply because extraction succeeded. The bytes inside an archive remain as trustworthy, or untrustworthy, as their source.

## Know what an archive does not protect

A successful round trip is useful, but one archive next to its source is not a complete backup. A disk failure can destroy both. Malware or a mistaken command with access to both can damage both. If you replace the same archive every time, an older good version may disappear just when you discover that the latest source was wrong.

Important backups need separate storage, retained versions and periodic restore checks. Sensitive data also needs appropriate access controls and, where required, encryption. A compressed archive is still readable by anyone who can obtain and unpack it.

Our notes stayed unchanged while tar read them. Live data is harder: if files change during packing, the archive may not represent one consistent moment. Databases often need their own export or backup procedure. Copying their active storage files into tar is not automatically a usable backup.

Tar can store more than file contents, but restoration depends on the options, archive format, privileges and destination filesystem. The two byte comparisons above do not establish that every permission, owner, special file attribute or application state was preserved. A working backup is one that can restore what you actually need, not merely one whose filename ends in `.tar.gz`.

## Remove the practice files

Only clean up when you are finished examining the copies. First display the directory saved in `work`:

```bash
printf '%s\n' "$work"
```

`%s` prints the variable's value as text and `\n` ends the line. Confirm that this is the unique temporary practice directory created at the start, not your home directory or a location containing other work. If you lost the variable or reused the name, do not guess the deletion target.

Then leave that directory and delete its contents and the directory itself:

```bash
cd "$HOME"
rm -r -- "$work"
```

`$HOME` is your home directory. If `cd` fails, stop. `rm` deletes files rather than moving them to a desktop trash folder; `-r` includes directories and everything below them. `--` ends option parsing so that the following value is treated as a path. The quotes keep that path together. This is deliberately limited to the disposable directory whose path you just checked. It removes the source notes, both archives and every restored or compressed copy from this example.

## Further reading

- [GNU tar manual](https://www.gnu.org/software/tar/manual/)
- [GNU gzip manual](https://www.gnu.org/software/gzip/manual/)
