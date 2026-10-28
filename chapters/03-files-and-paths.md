# 3. Files, directories and paths

[Contents](../README.md) | [Previous: shell](02-shell.md) | [Next: text](04-text.md)

Suppose you have written a packing note and want to keep an earlier version before changing it. You need to know where the note lives, how to copy it, and whether changing one name will change the other. These are small tasks, but they introduce an important distinction: a file's name, its location, and its contents are not the same thing.

We will build a small `linux-notes` directory, put a note inside it, and follow that note through copying, moving, linking, and editing. Everything we create belongs inside that one directory. There is no need for administrator access or changes to system files.

## On this page

- [Where a file lives](#where-a-file-lives)
- [Make a place for the notes](#make-a-place-for-the-notes)
- [Write a note and follow its path](#write-a-note-and-follow-its-path)
- [Names with spaces and names beginning with a dot](#names-with-spaces-and-names-beginning-with-a-dot)
- [Look at a file without changing it](#look-at-a-file-without-changing-it)
- [Copy a version, then move it](#copy-a-version-then-move-it)
- [Find a note below a directory](#find-a-note-below-a-directory)
- [Two ways to give a file another name](#two-ways-to-give-a-file-another-name)
- [Edit the note in an editor](#edit-the-note-in-an-editor)
- [Remove the example without removing anything else](#remove-the-example-without-removing-anything-else)
- [Further reading](#further-reading)

## Where a file lives

A directory holds names of files and other directories. You may know directories as folders. A path is the written route through those names to the item you want.

Linux presents directories as one tree beginning at `/`, pronounced “slash.” This starting directory is called the **root directory**. A path such as `/home/sam/Documents/notes.txt` means: start at `/`, enter `home`, then `sam`, then `Documents`, and look for `notes.txt` there. Each slash separates one part of the route from the next.

That example is a location to understand, not a command or a promise that your machine has a user named Sam. Home directories can live elsewhere. Also, `/root` is a particular directory commonly used as the administrator account's home. It is not another spelling of `/`.

The shell always has a current directory, which is the starting place for paths that do not begin with `/`. Ask where you are:

```bash
pwd
```

`pwd` prints the current directory and changes nothing. An illustrative result is:

```text
/home/sam
```

Your result will depend on where the terminal started. Opening another terminal does not necessarily put it in the same directory as this one.

There are two ways to describe a location:

- An **absolute path** begins with `/` and gives a route from the root directory. `/home/sam/Documents/notes.txt` is absolute.
- A **relative path** does not begin with `/`. Its starting point is the current directory. From `/home/sam`, `Documents/notes.txt` reaches the same example file.

The difference is the starting point, not whether the file exists. An absolute path can name something that is missing; a relative path can name something that exists.

Your home directory is your usual personal working area. Bash normally has its path in a value named `HOME`. In a command, `$HOME` asks the shell to insert that value. We will use `"$HOME/linux-notes"` so the example does not depend on your account name. The double quotes keep the resulting path together as one piece, even if it contains spaces. `HOME` can be changed by the environment, so it is a convenience, not proof of who owns a directory.

You will also see `~` used for home in other documentation. At the beginning of an unquoted word, Bash normally expands `~/linux-notes` to a path in your home directory. Quoting the whole word as `"~/linux-notes"` prevents that expansion. The examples here use the less surprising `"$HOME/linux-notes"` form instead.

## Make a place for the notes

The next command creates a directory. Use it only if you do not already have a directory called `linux-notes` in your home:

```bash
mkdir -- "$HOME/linux-notes"
```

`mkdir` means “make directory.” The path after it is the directory to create. The `--` marks the end of command options, so a following name is treated as a name rather than an instruction such as `-l`. Many utilities in this chapter support `--`; not every Linux program does.

Success normally produces no text. If the directory already exists, the command refuses to replace it. The final words of the error will be `File exists`; the full path depends on your home directory. Do not delete an existing directory to make this example work. Choose an unused name and use it consistently throughout the chapter instead.

Move the shell into the new directory and check the location:

```bash
cd -- "$HOME/linux-notes"
pwd
```

`cd` changes the current directory of this shell. It does not move any files. `pwd` should now print your home-directory path followed by `/linux-notes`. If `cd` reports an error, stop there and correct the path before continuing. Commands that use relative paths would otherwise run from the wrong place.

Make two directories inside this one:

```bash
mkdir -- drafts archive
ls
```

The first command creates both names. `ls`, short for “list,” shows names in the current directory when you do not give it another path. In the local example run, its output contained:

```text
archive
drafts
```

A terminal may arrange these names on one line or add colors. Neither difference changes what exists. At this point both directories are empty.

## Write a note and follow its path

First create an empty text file inside `drafts`:

```bash
touch -- drafts/trip.txt
```

`touch` creates an empty file when the name does not exist. The path says to look inside `drafts`, which is itself inside our current directory. It does not create missing parent directories.

An important detail: `touch` does not empty a file that already exists. In that case it normally updates the file's access and modification times. The name can be misleading if you think it always means “create a new file.”

Put one line into the new file:

```bash
printf 'Pack a notebook.\n' > drafts/trip.txt
```

`printf` produces text. The single quotes keep the text together and prevent the shell from interpreting its contents. Within the format text given to `printf`, `\n` means a newline, so the line ends properly.

The `>` symbol is handled by the shell. It sends the command's output to the named file instead of the terminal. It creates that file if necessary, but **replaces its previous contents if it already exists**. Here that is intentional: we just created an empty practice file. A successful write produces no terminal output because the output went into the file.

Read it back:

```bash
cat -- drafts/trip.txt
```

For this small file, `cat` simply prints its contents:

```text
Pack a notebook.
```

The file has not moved into the terminal. You are seeing its text; the stored file remains in `drafts`.

Now consider this mistake:

```bash
cat -- trip.txt
```

The local run produced this error:

```text
cat: trip.txt: No such file or directory
```

The note exists, but not directly in `linux-notes`. The shell does not search every directory for a matching filename. From our current location, the route needs the `drafts/` part:

```bash
cat -- ./drafts/trip.txt
```

This prints `Pack a notebook.` again. The `.` means “the current directory,” so `./drafts/trip.txt` and `drafts/trip.txt` reach the same place here.

There is a corresponding name for the directory one level above: `..`, pronounced “dot dot.” Try moving into `drafts` and back out:

```bash
cd -- drafts
pwd
cd -- ..
pwd
```

The first printed path ends in `/linux-notes/drafts`. The second ends in `/linux-notes`. These endings describe the actual local results; their starting path varies by machine. We are now back in `linux-notes` for the remaining commands.

You can use `.` and `..` as parts of longer paths, not just with `cd`. From inside `drafts`, `../archive` would lead to the neighboring archive directory. There is no need to move there merely to copy a file there: commands can use paths to reach other directories while the shell stays put.

## Names with spaces and names beginning with a dot

Spaces are permitted in Linux filenames. Create a directory whose name contains one, then an empty file inside it:

```bash
mkdir -- "My Notes"
touch -- "My Notes/ideas.txt"
```

The double quotes are not part of either name. They tell the shell to pass the quoted text as one argument. Without quotes, `mkdir My Notes` would ask for two separate directories named `My` and `Notes`.

Use the same quoting when reading, copying, moving, or removing the file. Quoting a name is not only for creation.

A dot at the start of a name has a different purpose. Create a small reminder:

```bash
printf 'Check the train time.\n' > .reminder
```

A plain `ls` normally leaves out names beginning with a dot. Ask it to include those names:

```bash
ls -a
```

`-a` means “all,” including dot-prefixed names. The local run showed:

```text
.
..
.reminder
My Notes
archive
drafts
```

The first two entries are the current and parent directory names we just used. `.reminder` is the actual reminder file. A hidden name is hidden only from some default listings. It is not encrypted or protected from other people who already have permission to read it.

Linux filenames are usually case-sensitive. `My Notes` and `my notes` would normally be different names. Some filesystems can behave differently, so use the capitalization you actually created rather than depending on a guess.

## Look at a file without changing it

A simple list answers “which names are here?” A more detailed list answers questions such as “is that a directory?” and “how large is that file?”

```bash
ls -lah
```

These three short options are combined after one dash:

- `-l` asks for a long, detailed listing.
- `-a` includes hidden names, as before.
- `-h` displays sizes in more readable units when useful, such as `4.0K`.

A **schematic listing row**, with owner and date placeholders rather than copied machine output, looks like this:

```text
-rw-r--r-- 1 OWNER GROUP 22 DATE TIME .reminder
```

Read the row from its ends first. The final part is the name. The first character describes the kind of entry: `-` for a regular file, `d` for a directory, or `l` for a symbolic link, which we will make shortly. A regular file holds content, such as our note, rather than being a directory or a link. The following letters describe access permissions; the permissions chapter explains them in detail. The other fields include a link count, an owner, a group, a size, and a modification time.

For a regular file, the size is its content length in bytes. A directory's reported size is not the sum of everything stored under it. Do not use that number to judge how much space all its files occupy.

Usually `ls` given a directory lists what is inside it. To inspect the directory entry itself, add `-d`:

```bash
ls -ld -- "My Notes"
```

Here `-l` requests the detailed row and `-d` keeps the focus on `My Notes`, rather than its contents. The first character of its row should be `d`.

For one file, `stat` gives a fuller description:

```bash
stat -- drafts/trip.txt
```

This reads information *about* the file, often called its **metadata**. A storage area needs a way to organize file contents and names; that organization is called a **filesystem**. A machine can attach several filesystems to different places in its one directory tree. GNU `stat` reports fields including `Size`, `Links`, ownership, and several timestamps. `Modify` concerns content changes; `Change` concerns changes to the file's recorded information and is not a reliable creation time. If a `Birth` time appears, it depends on support from the underlying filesystem. Output and options differ between implementations.

A name ending in `.txt` is a helpful convention, not proof that the contents are text. If the `file` utility is installed, this optional command inspects recognizable content patterns:

```bash
file -- drafts/trip.txt
```

For our note, expect a description identifying text. This is an informed identification, not a guarantee that every application will interpret the file the same way. Renaming a photograph to `photo.txt` does not convert it into text.

The `file` utility was unavailable in the local example environment, so its examples here are an unexecuted walkthrough rather than reported results. If your terminal says `file: command not found`, skip them; they are not required for the rest of the chapter. Do not assume a missing optional utility means that the file you are inspecting is damaged.

## Copy a version, then move it

Before adding more items to the packing note, keep its first version:

```bash
cp -i -- drafts/trip.txt drafts/trip-copy.txt
```

`cp` copies from the first path, the **source**, to the second, the **destination**. In this example it reads the note and creates a separate file containing the same text. Later content changes to one of these files will not automatically change the other.

The `-i` option asks before replacing an existing destination file. On the first run, the destination is new, so there should be no question and no output. If you run the command again, GNU `cp` may ask:

```text
cp: overwrite 'drafts/trip-copy.txt'?
```

That prompt was observed in the local run. Answer `n` and press Enter to keep the existing copy. If you are unsure what a replacement prompt refers to, decline and inspect the two paths. Do not treat `-i` as a substitute for reading them.

The copy currently sits beside the working note. Move it into `archive`, giving it a clearer name at the same time:

```bash
mv -i -- drafts/trip-copy.txt archive/trip-v1.txt
```

`mv` means “move.” On the same filesystem it can change a file's name or directory location without making a second copy of the contents. The old name `drafts/trip-copy.txt` is gone; the new name is `archive/trip-v1.txt`. Across filesystems, `mv` may need to copy the data and then remove the source. That cross-filesystem behavior was not exercised in the local example.

As with `cp`, `-i` asks before replacing an existing destination. Confirm the moved file by reading its new path:

```bash
cat -- archive/trip-v1.txt
```

It still prints:

```text
Pack a notebook.
```

There is an important destination rule for both commands: if the final path already names a directory, the source is placed *inside* that directory, using its existing name. If the final path does not exist, it usually supplies the new file's name. Check whether your intended destination is a directory before moving something important.

This archived note is a separate copy, but it is not a complete backup strategy. Losing the disk or deleting the whole `linux-notes` directory could lose both versions together.

## Find a note below a directory

`ls` is useful when you know which directory to inspect. When you want to look through a directory and all the directories inside it, use `find`:

```bash
find . -type f -name '*.txt' -print
```

Read this command from left to right:

- `.` is where the search starts: our current `linux-notes` directory.
- `-type f` selects regular files, not directories.
- `-name '*.txt'` selects names ending in `.txt`.
- `-print` prints each matching path.

Here `*` means “any sequence of characters” in the name pattern. The single quotes matter: they keep the shell from expanding `*.txt` before `find` sees it. We want `find` to apply the pattern to names throughout its search, not the shell to substitute a few names from the current directory.

The local run printed these paths:

```text
./My Notes/ideas.txt
./archive/trip-v1.txt
./drafts/trip.txt
```

The order can differ. `find` is showing where matches live, not sorting them into a reading order. `.reminder` is absent because its name does not end in `.txt`. Hidden names are not automatically excluded from `find` searches.

This command only searches and prints. It does not follow symbolic links to other directories by default. Keep it that way while learning. Options that delete matches or run another command for each match introduce different risks from simply displaying paths.

## Two ways to give a file another name

Sometimes you want another route to the current note, not a snapshot of its old contents. Linux offers two different kinds of links for that purpose. They behave differently when you rename or remove a file.

### A symbolic link stores a route

Create a convenient name in `linux-notes` that points to the note inside `drafts`:

```bash
ln -s -- drafts/trip.txt current.txt
```

`ln` creates a link. With `-s`, it creates a **symbolic link**, also called a symlink: a special entry containing a path to follow. The first path is the target stored in the link; the second is the new link's name.

Inspect it:

```bash
ls -l -- current.txt
readlink -- current.txt
```

The detailed listing ends with `current.txt -> drafts/trip.txt`. The arrow shows the stored target. `readlink` prints just that target, which in the local run was:

```text
drafts/trip.txt
```

Now read through the link:

```bash
cat -- current.txt
```

It prints `Pack a notebook.` because opening `current.txt` leads to the file in `drafts`. We did not copy the note.

A relative target such as `drafts/trip.txt` is resolved from the directory *containing the link*, not from whichever directory your shell happens to be in later. Our link lives in `linux-notes`, so its target leads into `linux-notes/drafts`. Moving the link elsewhere could change what that relative route reaches. An absolute target instead starts at `/`, but can stop working if the target is moved or the tree is arranged differently on another machine.

If `file` is installed, these optional inspection commands distinguish the link from its target:

```bash
file -- current.txt
file -L -- current.txt
```

Without `-L`, `file` normally describes the symbolic link. `-L` asks it to follow the link and inspect the target's contents. As noted earlier, these `file` commands were not executable in the local environment.

### A hard link names the same underlying file

Make a different kind of link in `archive`:

```bash
ln -- drafts/trip.txt archive/shared.txt
```

Without `-s`, `ln` creates a **hard link**. This adds another name for the same underlying file. It does not store a route to `drafts/trip.txt`, and it does not create an independent copy.

To see evidence of that shared identity:

```bash
ls -li -- drafts/trip.txt archive/shared.txt
```

The new option `-i` prints the file's identifying number within its filesystem, called an **inode number**. Both rows have the same number in this example, and both show a link count of `2`. The exact number is machine-dependent. The number is meaningful together with the filesystem, not as a globally unique identifier across every disk.

Hard links normally must stay on the same filesystem. Ordinary users cannot make them to directories. Symbolic links can point across filesystems because they store a route instead of sharing this file identity.

### See what survives a rename

Rename the working note:

```bash
mv -i -- drafts/trip.txt drafts/packing.txt
```

Now try the symbolic link:

```bash
cat -- current.txt
```

The local result was:

```text
cat: current.txt: No such file or directory
```

`current.txt` still exists as a link, but its stored route still says `drafts/trip.txt`. Renaming the target did not update that route. This is a **broken link**: the link exists, but the destination cannot be reached.

The hard link still works:

```bash
cat -- archive/shared.txt
```

It prints `Pack a notebook.`. Nothing had to be redirected, because `archive/shared.txt` is another name for the underlying file, not a path pointing to its former name.

Repair the symbolic link by removing only that link and creating it again with the new target:

```bash
rm -- current.txt
ln -s -- drafts/packing.txt current.txt
```

`rm` removes a named entry without putting it in a desktop trash folder. Applied to this symbolic link, with no trailing slash, it removes the link itself, not the target file. We will use it for the final cleanup too.

Add another line to the working note:

```bash
printf 'Pack a water bottle.\n' >> drafts/packing.txt
```

The doubled symbol `>>` sends output to the end of the file instead of replacing its existing contents. This is the difference between adding a line and losing the previous one.

Read the current note through each link, then read the separate copy:

```bash
cat -- current.txt
cat -- archive/shared.txt
cat -- archive/trip-v1.txt
```

The first command and the second command each print:

```text
Pack a notebook.
Pack a water bottle.
```

The third prints only:

```text
Pack a notebook.
```

The symbolic link reaches the updated note by its path. The hard link names the same file we updated. The copy retains the earlier contents because it is independent.

Removing one hard-link name does not remove the file's contents while another hard-link name still exists. A running program that already has the file open can also keep it available after its last name is removed, until the program closes it. For everyday file work, the immediate lesson is simpler: removing a name and making the underlying data unavailable are not always the same event.

## Edit the note in an editor

Sending a short line with `printf` makes the example repeatable, but for changing a sentence you will usually want an editor. If Nano is installed, stay in `linux-notes` and open the working note:

```bash
nano drafts/packing.txt
```

This is an optional interactive walkthrough. Nano was not installed in the environment used for the local examples, so the editing interaction was not tested there.

Nano displays the file and lets you move the cursor and change text. Its shortcuts appear along the bottom. When a shortcut is shown as `^O`, the `^` means hold Ctrl while pressing the letter, not type a caret into the note.

To save, press **Ctrl+O**, check that the displayed destination is `drafts/packing.txt`, and press **Enter** to confirm it. Press **Ctrl+X** to exit. If you try to exit with unsaved changes, Nano asks whether to save them. Read that question before choosing.

Opening a nonexistent filename generally gives you a new buffer in the editor, not an immediately created file on disk. Saving creates the file. A typo in a filename can therefore lead to editing a new empty file instead of the note you intended. If the editor looks unexpectedly empty, check the path rather than immediately typing over the problem.

After leaving Nano, `cat -- drafts/packing.txt` reads the saved contents from disk. If you changed the note, its text will naturally differ from the earlier two-line output.

One link-related detail deserves care: different editors save differently. Some write into the existing file; others write a replacement file and rename it over the old one. That replacement can separate a hard-linked name from the newly saved version. Our `>>` example showed an update to the existing file, not a guarantee about every editor's saving behavior. Do not depend on hard links as a synchronization system for documents.

Start by editing your own notes, not a file under `/etc`. System configuration is not a good place to learn an unfamiliar editor's save and exit controls.

## Remove the example without removing anything else

Return to this part only when you are finished with the notes. The following removal commands are not a move to a desktop trash folder. They normally offer no built-in undo. They are deliberately limited to the names created in this chapter.

Make sure `pwd` shows the `linux-notes` directory you created. If you changed directories during editing, use `cd -- "$HOME/linux-notes"` to return and check again. Do not continue if that fails.

First, see why an empty-directory removal is useful:

```bash
rmdir -- archive
```

`rmdir` removes directories only when they are empty. At this stage the local run refused:

```text
rmdir: failed to remove 'archive': Directory not empty
```

That is expected: our saved copy and hard link are still inside it. The refusal gives us a chance to inspect rather than recursively deleting everything.

Remove the symbolic link first:

```bash
rm -- current.txt
```

The working note is still present. You can confirm that with:

```bash
cat -- drafts/packing.txt
```

Then remove the working file, its other hard-link name, and the archived independent copy:

```bash
rm -- drafts/packing.txt archive/shared.txt archive/trip-v1.txt
```

Remove the other two files we created, including the hidden reminder:

```bash
rm -- "My Notes/ideas.txt" .reminder
```

The directories should now be empty:

```bash
rmdir -- drafts archive "My Notes"
```

If this refuses, inspect the named directory with `ls -la` and its quoted path before deciding what to do. Perhaps you saved an extra note or an editor left a backup file. A refusal is not an instruction to switch to a more powerful deletion command.

Finally, leave the practice directory and remove its now-empty entry:

```bash
cd -- ..
rmdir -- linux-notes
```

If changing directory fails, stop before running the next line. In the verified sequence, all the named removals succeeded after the deliberate nonempty-directory refusal.

You have not needed `rm -r`, the option that removes a directory and its contents recursively. Avoid using it with an uncertain path, a wildcard, or a variable whose value you have not checked. For this example, explicit filenames and `rmdir` are enough to make every removal understandable.

The useful habit is to connect each operation to its exact location: check where relative paths begin, distinguish a link from a copy, and read the destination before changing anything. Those habits matter more than memorizing a long list of commands.

## Further reading

- [GNU Coreutils: File name manipulation](https://www.gnu.org/software/coreutils/manual/html_node/File-name-manipulation.html)
- [GNU Coreutils: Basic operations, including cp, mv, and rm](https://www.gnu.org/software/coreutils/manual/html_node/Basic-operations.html)
- [Linux man-pages: path_resolution(7)](https://man7.org/linux/man-pages/man7/path_resolution.7.html)
- [Linux man-pages: symlink(7)](https://man7.org/linux/man-pages/man7/symlink.7.html)
- [GNU findutils manual](https://www.gnu.org/software/findutils/manual/html_mono/find.html)
- [Nano: getting started](https://www.nano-editor.org/dist/latest/nano.html#Getting-Started)
