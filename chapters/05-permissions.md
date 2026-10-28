# 5. Users, groups and permissions

[Contents](../README.md) | [Previous: text](04-text.md) | [Next: processes](06-processes.md)

You have a file of maintenance notes. You want to edit it yourself, perhaps let a colleague read it, and keep unrelated users out. Later, you put it in a directory and discover that a readable file can still produce `Permission denied`. The file has not become corrupt. Linux is checking both who is asking and which parts of the path that person can use.

This chapter follows that small example. All changes are to new practice files, not system files or real accounts. Use an ordinary account, not a root shell: root privileges can bypass restrictions that these examples are meant to demonstrate.

## In this chapter

- [Who is asking to use the file?](#who-is-asking-to-use-the-file)
- [Make a private practice directory](#make-a-private-practice-directory)
- [Read a file's permission line](#read-a-files-permission-line)
- [Choose the permissions with chmod](#choose-the-permissions-with-chmod)
- [What execute permission does](#what-execute-permission-does)
- [Why directories have different rules](#why-directories-have-different-rules)
- [Follow the whole path](#follow-the-whole-path)
- [Writing a file is different from deleting it](#writing-a-file-is-different-from-deleting-it)
- [Ownership and shared groups](#ownership-and-shared-groups)
- [Choose defaults with umask](#choose-defaults-with-umask)
- [Understand sudo before reaching for it](#understand-sudo-before-reaching-for-it)
- [When the simple rules are not the whole answer](#when-the-simple-rules-are-not-the-whole-answer)
- [Remove the practice files](#remove-the-practice-files)
- [Further reading](#further-reading)

## Who is asking to use the file?

An account gives Linux a way to distinguish one user's work from another's. It has a name, such as `alex`, and a number called a **user ID**, often shortened to UID. The system uses the number internally. The name makes it easier for people to read.

Accounts are not always people. A web server or backup service may run under an account reserved for that work. This limits what the program can reach if it makes a mistake or is attacked.

Start with two read-only commands:

```bash
whoami
id
```

`whoami` prints the name under which the command is currently acting. `id` gives more detail, including the user number and group memberships. Here is **schematic output**, not a report of your machine:

```text
alex
uid=1001(alex) gid=1001(alex) groups=1001(alex),1100(editors)
```

In this example, the account is `alex`, its user number is `1001`, and its primary group is also named `alex`. It additionally belongs to `editors`. A **group** is a collection of accounts that can be given shared access. A group also has a numeric ID, called a GID. User names and group names can match, but users and groups are separate things.

A running command carries an identity and a set of group memberships. Normally it inherits them from the shell that started it. This is why opening a terminal as one person and running a service as another can produce different access results for the same file. The current identity used for many checks is called the **effective** identity. Tools such as `sudo` can deliberately start a command with a different identity.

An administrator can change group membership, but that does not generally rewrite the memberships of shells already running. A fresh login is normally needed to pick up a newly assigned group. We will not add accounts or change memberships here.

## Make a private practice directory

Start in a directory where you are allowed to create files, such as your home directory. Run:

```bash
mkdir -m 700 permissions-story
cd permissions-story
```

`mkdir` creates the directory. Its `-m 700` option sets the ordinary permissions so only its owner can use it; we will decode `700` shortly. `cd` makes it your current directory. If `mkdir` says the name already exists, stop and choose a new practice name, changing the later cleanup command to match. Do not reuse an unknown directory or continue after a failed `cd`.

Create the first note, then make its permissions explicit:

```bash
printf 'Check the water filter.\n' > notes.txt
chmod 600 -- notes.txt
cat notes.txt
```

`printf` writes the quoted text; `\n` ends the line. The shell's `>` puts that output in `notes.txt`, creating the file or replacing its existing contents. That replacement is safe here because this is a new practice directory. `chmod` changes permissions. `--` ends the command's options, so following names are treated as file names even if they begin with `-`.

The content printed by `cat` is:

```text
Check the water filter.
```

Permission-changing commands normally print nothing on success. Silence alone is not a useful description of the result, so inspect the file next.

## Read a file's permission line

```bash
ls -l -- notes.txt
```

`-l` asks for a long listing rather than just the name. A typical line has this shape; the owner, group, size and date below are **schematic**:

```text
-rw------- 1 alex alex 24 Oct 28 10:00 notes.txt
```

Read the fields from left to right:

- `-rw-------` describes the kind of entry and its permissions.
- `1` is a count of names directly linked to the file's underlying data. It is not a permission setting.
- The first `alex` is the owner; the second is the group assigned to the file.
- `24` is the size in bytes, followed by a modification date and the name.

Focus on the first field. The leading `-` means a regular file. A directory starts with `d`; a symbolic link, which points to another path, starts with `l`.

The remaining nine positions form three sets:

```text
          owner   group   others
            rw-     ---     ---
```

For a regular file:

- `r`, read, allows opening and reading its contents.
- `w`, write, allows changing its contents, including truncating them to an empty file.
- `x`, execute, allows attempting to run it as a program.
- `-` means that permission is absent in that position.

The owner is the account recorded on the file, not necessarily the person using the terminal now. The group set applies to members of the file's recorded group. “Others” means processes that match neither of those categories, not just remote users or people outside your organization.

For the ordinary permission check, Linux chooses one set. If the process is the owner, it uses the owner set. Otherwise, if one of its groups matches the file's group, it uses the group set. Otherwise it uses the others set. It does **not** combine all three or fall back to a more generous set when the selected one denies access. Additional access rules and administrative privileges can affect the outcome; we return to those later.

## Choose the permissions with chmod

There are two common ways to describe a change: state a complete ordinary permission pattern, or name just the part you want to change.

### Numeric modes describe a complete pattern

Suppose the file should be writable by its owner, readable by its group, and unavailable to others:

```bash
chmod 640 -- notes.txt
```

Each digit describes one of the three sets, in owner, group, others order. Within a set, read is worth `4`, write `2`, and execute `1`. Add the permissions you want:

| Digit | Letters | Meaning for a regular file |
|---|---|---|
| `0` | `---` | No permissions |
| `1` | `--x` | Execute only |
| `2` | `-w-` | Write only |
| `3` | `-wx` | Write and execute |
| `4` | `r--` | Read only |
| `5` | `r-x` | Read and execute |
| `6` | `rw-` | Read and write |
| `7` | `rwx` | Read, write and execute |

Thus `640` means `rw-`, `r--`, `---`. The `600` used earlier meant read and write for the owner, nothing for the other two sets. `700` on our directory gave the owner all three permissions.

For a compact view of the result, use GNU `stat`:

```bash
stat -c '%A %a %n' notes.txt
```

`stat` reports file information. `-c` supplies a format: `%A` is the permission string, `%a` is its numeric form, and `%n` is the name. Quotes keep this whole format together as one argument. The tested result is:

```text
-rw-r----- 640 notes.txt
```

Numeric modes such as `640` replace the ordinary permission pattern rather than adding a permission. Special directory bits have further preservation rules, so do not treat this as a universal way to clear every possible flag.

### Symbolic modes describe a targeted change

Now suppose group members should also be allowed to edit:

```bash
chmod g+w -- notes.txt
stat -c '%A %a %n' notes.txt
```

The result is:

```text
-rw-rw---- 660 notes.txt
```

`g` means the group set; `+w` adds write permission without changing the other ordinary permissions. The letters for selecting people are `u` for the owner, `g` for the group, `o` for others, and `a` for all three. Here `u` means the file's owner, not “whichever user is typing.”

To remove group write and explicitly leave others with no permissions:

```bash
chmod g-w,o= -- notes.txt
stat -c '%A %a %n' notes.txt
```

The result returns to:

```text
-rw-r----- 640 notes.txt
```

`-` removes the named permission. `=` sets exactly the listed permissions for that category; nothing after `o=` means none. The comma joins two changes in one argument. Naming the category explicitly also avoids the interaction between an omitted category and the shell's default permission mask.

These changes do not create a shared group or invite anyone into it. If the file's group contains only you, `g+r` has not given a colleague access. And our private outer directory still blocks other users from reaching the file, regardless of its group permissions.

## What execute permission does

A text note needs no execute permission. A script intended to run directly does. Make a tiny script in the practice directory:

```bash
printf '#!/bin/sh\nprintf "Notes are ready.\\n"\n' > show-note
chmod 600 -- show-note
```

This `printf` creates two lines:

```sh
#!/bin/sh
printf "Notes are ready.\n"
```

The first line tells Linux which interpreter to use when running the script directly. An interpreter is a program that reads instructions from text. Here `/bin/sh` reads the second line as a shell command. In the outer `printf`, `\\` writes a literal backslash, preserving `\n` for the script's own `printf`.

Try to run it:

```bash
./show-note
```

`./` means “in the current directory.” The tested Bash error was:

```text
bash: line 1: ./show-note: Permission denied
```

Interactive Bash may omit `line 1`. The important part is `Permission denied`: the file has read and write permission for its owner, but not execute permission. Correct that specific omission:

```bash
chmod u+x -- show-note
./show-note
```

Now it prints:

```text
Notes are ready.
```

The mode is now `700`, shown as `-rwx------`. Adding `x` did not turn arbitrary text into a valid program. This worked because the file already contained valid instructions and an interpreter line. The filesystem must also permit execution; a filesystem mounted with the `noexec` option can block direct execution even when `x` is present.

Execute permission is not a way to stop someone reading and interpreting a script. A person who can read a shell script may run `sh show-note`, asking an already executable interpreter to read it. Conversely, interpreters usually need read permission on the script as well as the permissions required for direct execution. Avoid treating `x` as a general secrecy control.

## Why directories have different rules

A directory stores names leading to files and other directories. It is not a program, so its `x` cannot mean “run this directory.” The same letters control different actions:

| Permission | On a regular file | On a directory |
|---|---|---|
| `r` | Read the contents | List the names it contains |
| `w` | Change the contents | Change its entries, normally requiring `x` too |
| `x` | Attempt to run it | Look up entries and pass through it using a path |

Directory `x` is often called **search** or **traversal** permission. It allows Linux to look up a specific name there. Directory `r` allows obtaining the list of names. To do the usual useful things, such as listing names together with their sizes and permissions, you generally need both `r` and `x`.

This is why a reasonable private directory mode is `700`, while a private text file usually needs only `600`. The extra `x` lets you reach the directory's contents.

Do not apply `chmod -R 644` to a directory tree. `-R` means recursively change everything below the named directory. That mode removes search permission from directories as well as execute permission from files, making normal path access fail. Files and directories need different treatment, and a blanket `777` is not a thoughtful correction either: it grants everyone write access.

## Follow the whole path

Put a copy of the note in a small cabinet:

```bash
mkdir cabinet
chmod 700 -- cabinet
cp notes.txt cabinet/notes.txt
chmod 644 -- cabinet/notes.txt
```

`cp` copies the source to the destination. The copied file has explicitly been made readable by all three categories so we can distinguish its own permissions from its directory's permissions. It is still inside our private practice directory.

Now deliberately remove only the owner's search permission on `cabinet`:

```bash
chmod u-x -- cabinet
ls -ld -- cabinet
```

For `ls`, `-d` means show the directory itself, not its contents; combined with `-l`, it shows that directory's permission line. Its leading field is now `drw-------`: the owner can list names and has the write bit, but cannot search it.

```bash
cat cabinet/notes.txt
```

The tested result is:

```text
cat: cabinet/notes.txt: Permission denied
```

Linux must first look up `notes.txt` inside `cabinet`. It cannot do that because search permission is missing. The note's own `644` mode never gets a chance to solve this problem.

Restore the missing bit:

```bash
chmod u+x -- cabinet
cat cabinet/notes.txt
```

The note is readable again:

```text
Check the water filter.
```

The same rule applies to every directory along a longer path. For `/home/alex/project/notes.txt`, a process must be able to search `/`, `/home`, `/home/alex`, and `/home/alex/project`, and then have the required access to the file itself. A private home directory can prevent another account from reading a file that has `644` permissions inside it. Changing only that file is not enough.

For the opposite contrast, keep search permission but remove the ability to list names:

```bash
chmod 100 -- cabinet
cat cabinet/notes.txt
ls cabinet
```

`cat` still prints the note because we already know its name. `ls` fails:

```text
ls: cannot open directory 'cabinet': Permission denied
```

Not being able to list a directory does not make known file names unreachable. Restore the ordinary private-directory mode before continuing:

```bash
chmod 700 -- cabinet
```

You can also ask a simple yes-or-no question about current access:

```bash
if test -r cabinet/notes.txt; then
  printf 'readable\n'
else
  printf 'not readable\n'
fi
```

`test -r` checks readability and returns a success or failure status instead of printing a report. `if` chooses the commands after `then` on success, or those after `else` on failure; `fi` closes the conditional. Here the result is `readable`. This is a check from the current process's perspective at that moment, not a guarantee about a different account or a file changed immediately afterward.

## Writing a file is different from deleting it

Editing changes the file's contents. Deleting removes its name from the containing directory. Those are different operations, checked in different places.

Create a disposable note and remove its write permission:

```bash
printf 'Old reminder.\n' > cabinet/old-note.txt
chmod 400 -- cabinet/old-note.txt
printf 'Replacement\n' > cabinet/old-note.txt
```

The last command fails with `Permission denied` because the shell cannot open the file for writing. The redirection fails before `printf` can replace its contents.

But this succeeds:

```bash
rm -f -- cabinet/old-note.txt
```

`rm` removes the file's directory entry. `-f` skips the usual confirmation for a write-protected file, which is appropriate only because this is our named disposable note. We still have write and search permission on `cabinet`, so the ordinary directory rules permit removal despite the file's `400` mode.

Now try the reverse:

```bash
printf 'Old reminder.\n' > cabinet/old-note.txt
chmod 600 -- cabinet/old-note.txt
chmod 500 -- cabinet
rm -f -- cabinet/old-note.txt
```

This time removal fails:

```text
rm: cannot remove 'cabinet/old-note.txt': Permission denied
```

We can write the file's contents, but `cabinet` has no write permission, so we cannot remove its entry. `-f` suppresses prompts; it does not bypass permissions. Restore the directory and remove the disposable file:

```bash
chmod 700 -- cabinet
rm -f -- cabinet/old-note.txt
```

This distinction matters for editors too. Some save by rewriting the existing file; others create a replacement and rename it. The second approach needs permission to change the directory, not just the old file.

Shared temporary directories often have an additional **sticky bit**. In a listing such as `drwxrwxrwt`, the final `t` means others have search permission and the sticky bit is set. It restricts removal and renaming of entries to the entry's owner, the directory's owner, or a suitably privileged process. This is how a directory can let many people create files without normally letting them delete one another's files. It does not make the files' contents private.

## Ownership and shared groups

`chmod` changes permissions; it does not change the recorded owner or group. The owner can normally change a file's permissions even after removing their own read or write permission. Owning a file is therefore different from merely having permission to edit it.

`chgrp` changes a file's assigned group. An ordinary owner can normally choose one of the groups they already belong to. Here is a safe example that uses your current primary group rather than requiring a new one:

```bash
chgrp "$(id -gn)" -- notes.txt
ls -l -- notes.txt
```

For `id`, `-g` selects the primary group number and `-n` asks for its name instead. `$(...)` runs that command and substitutes its output; the surrounding double quotes keep the result as one argument. This will often leave the group unchanged, which is fine: it demonstrates the operation without creating accounts or memberships. Group names in your listing will differ from the schematic examples above.

In a real collaboration, an administrator might arrange an `editors` group, assign a shared directory to that group, and give the appropriate accounts membership. Both the directory path and each file need suitable permissions. This chapter does not perform that setup.

`chown` changes ownership. For example, the command shape `chown new-owner -- file` requests a different owner; `chown new-owner:new-group -- file` requests both. These are descriptions of syntax, not commands to run against the practice files. Transferring ownership to another user normally requires administrative privilege. Do not fix an unexplained service error by taking ownership of its files: the service may require its own account to own them.

For more advanced shared-directory setups, a directory's **set-group-ID bit**, often called setgid, makes new entries inherit the directory's group rather than the creator's usual group. A group position such as `rws` shows that bit together with search permission. This controls the assigned group, not whether new files are group-writable; the creation defaults still matter. Setuid on executable files is a different privilege-changing mechanism. Neither is needed for our example, and neither should be added as a general permissions fix.

## Choose defaults with umask

So far we have used `chmod` after creation. How are permissions chosen at the moment a file is made?

A program requests some starting permissions. Linux then normally removes any permissions forbidden by the process's **umask**, its file-creation permission mask. Run this read-only command to see your current shell's mask:

```bash
umask
```

You might see `0022` or `0077`; those are examples, not guaranteed defaults. For ordinary files, programs commonly request `666`, meaning read and write for everyone but no execute bits. For directories, they commonly request `777` because directories need search permission.

Try a private default without changing the surrounding shell permanently:

```bash
(
  umask 077
  touch private.txt
  mkdir private-dir
  stat -c '%A %a %n' private.txt private-dir
)
```

The parentheses run the commands in a **subshell**, a separate shell environment. Changing its mask does not change the parent shell's mask. `touch` creates an empty file when the name does not already exist. Under ordinary permissions without inherited default access lists, the tested output is:

```text
-rw------- 600 private.txt
drwx------ 700 private-dir
```

Mask `077` removes all group and others permissions from the requested modes, leaving the owner alone. It does not add execute bits to the file.

Compare a less restrictive default:

```bash
(
  umask 022
  touch readable.txt
  mkdir readable-dir
  stat -c '%A %a %n' readable.txt readable-dir
)
```

The tested result is:

```text
-rw-r--r-- 644 readable.txt
drwxr-xr-x 755 readable-dir
```

Mask `022` removes write permission from group and others. It leaves their read permission, and directory search permission, intact. Our outer private directory still prevents other accounts from reaching these examples.

A mask is a set of permissions to turn off, not a subtraction problem. For example, mask `033` removes group and others write and execute bits. A new ordinary file requested as `666` still becomes `644`: there were no execute bits to remove in the first place. A program that requests fewer permissions, such as `600`, does not gain extra permissions from a more permissive mask.

Changing the mask does not change existing files:

```bash
(
  umask 077
  touch readable.txt
  stat -c '%a %n' readable.txt
)
```

The existing file still reports:

```text
644 readable.txt
```

Here `touch` updates timestamps rather than creating a new file. Use `chmod` when you intend to change an existing file. A directory with an inherited default access-control list can follow different creation rules; the examples above describe the ordinary case without such a list.

## Understand sudo before reaching for it

`sudo` asks the system to run one command as another account, usually root. Root is the administrative account with user ID `0`. Its privileges can bypass many ordinary file permission checks. That is why running this chapter as root would hide several of its intentional failures.

Local policy decides which commands you may run, as whom, and whether authentication is required. Being able to sign in does not automatically grant sudo permission. When authentication is requested, it is commonly your own password, but policy can differ. Do not share passwords or paste them into commands.

For a permitted, read-only inspection of sudo policy, an administrator may ask you to run `sudo -l`. The lowercase `-l` means list the commands policy allows. It may prompt for authentication, and policy listings or attempts can be logged. It was not run for this chapter; there is no need to use sudo in the practice directory.

Before using elevation for a real problem, identify the account that needs access, inspect the target and its parent directories, and decide what the authorized access should be. Our `cabinet` error needed `chmod u+x` on a directory we owned, not an administrator bypass. A missing file, wrong path, or invalid command also remains wrong under sudo.

There is a subtle shell boundary worth knowing. In a command shaped like `sudo printf 'text\n' > /protected/file`, your current shell handles `>` before sudo runs `printf`. The redirection can therefore fail under your ordinary account even if the command would have been elevated. Do not try that example on a real protected file. For authorized administrative editing, follow the system's approved method, such as `sudoedit` where policy allows it, rather than escalating an entire interactive shell just to experiment.

## When the simple rules are not the whole answer

The owner/group/others model explains a great deal, but Linux has other controls:

- An **access-control list**, or ACL, can grant permissions to additional named users or groups. An `ls -l` permission field ending in `+` commonly indicates an extended ACL. In that case, the displayed group bits can represent a limit on ACL entries rather than just the owning group's direct permissions. `getfacl`, if installed, shows the details.
- A filesystem can be mounted read-only, or with restrictions such as `noexec`. Changing a file's mode does not change those mount settings.
- SELinux or AppArmor can restrict a program even when ordinary permissions allow an operation. These are additional policies, not reasons to disable security whenever a command fails.
- Administrative capabilities can let a process bypass particular checks. Conversely, root inside a restricted environment does not necessarily control the whole host.

For a puzzling denial, start with the simplest evidence: which command and path failed, which account ran it, what permissions are on the file, and whether every parent directory is searchable. Inspect the additional layers when that evidence does not explain the result. Avoid changing several layers at once, because that makes it difficult to learn which one mattered.

## Remove the practice files

If you followed the example, you should still be inside `permissions-story`. Check your location with `pwd` and confirm that these are the files you created. Restore the directory permissions we changed, then remove only the named files:

```bash
chmod 700 -- cabinet
rm -- notes.txt show-note cabinet/notes.txt private.txt readable.txt
rmdir -- cabinet private-dir readable-dir
cd .. && rmdir -- permissions-story
```

`rm` removes only those five files. `rmdir` removes each named directory only if it is empty. The `&&` makes removal of the outer directory conditional on successfully moving to its parent. Extra files make `rmdir` refuse; inspect them rather than switching to recursive removal. If you chose a different practice name, use that name in the final command. There is no wildcard or administrator access.

The fixture examples were tested with Bash and GNU utilities under an ordinary Linux account, including the deliberate failures and cleanup. Output labels distinguish exact tested results from variable identity and listing examples. Account creation, transferring files to another owner, privileged sudo operations, shared-group collaboration between separate users, special-bit setups, ACL changes, and security-policy changes were not performed.

## Further reading

- [Linux man-pages: path_resolution(7)](https://man7.org/linux/man-pages/man7/path_resolution.7.html), including the permission checks at each part of a path.
- [GNU Coreutils: chmod invocation](https://www.gnu.org/software/coreutils/manual/html_node/chmod-invocation.html).
- [GNU Coreutils: Setting Permissions](https://www.gnu.org/software/coreutils/manual/html_node/Setting-Permissions.html), covering symbolic and numeric modes.
- [Linux man-pages: credentials(7)](https://man7.org/linux/man-pages/man7/credentials.7.html), for process user and group identities.
- [Linux man-pages: umask(2)](https://man7.org/linux/man-pages/man2/umask.2.html), including interaction with default ACLs.
- [Sudo manual](https://www.sudo.ws/docs/man/sudo.man/), for policy-dependent privilege changes and options.
