# File permissions: understand the path before changing access

Linux checks access using the process's user and group credentials, the file type,
permission bits and other security controls. Read-only commands can narrow down
a problem. Do not use `chmod 777` or recursive permission changes as a shortcut.

## Read a mode as owner, group and others

```bash
id
stat -c '%A %a %U:%G %n' "$LINUX_LAB/config/private.txt"
```

`id` prints the current process's user ID, group ID and supplementary groups.
The GNU `stat -c` format prints symbolic mode (`%A`), octal mode (`%a`),
ownership and the path. In a mode such as `-rw-r-----`, the first `-` means a
regular file; the next three characters apply to the owner, group and others.
`r` reads file contents, `w` writes them, `x` executes a file when the interpreter
and mount policy allow it.

In octal, read is 4, write is 2 and execute is 1. Add them for each class:

| Mode | Owner | Group | Others | Common use, not a universal rule |
|---|---|---|---|---|
| `600` | read/write | none | none | Private regular file |
| `640` | read/write | read | none | File shared with a trusted group |
| `644` | read/write | read | read | Non-secret data file |
| `700` | read/write/execute | none | none | Private directory or owner-only script |
| `755` | read/write/execute | read/execute | read/execute | Publicly traversable directory or executable |

The correct mode depends on purpose, parent directories, ACLs and policy. A file
may still be unreadable when its mode appears open if a parent directory denies
traversal, an ACL narrows access, a security module denies it, or a mount is
read-only/noexec.

## Directory permissions are different

For a directory:

- `r` lets a process list names.
- `x` lets it search the directory and reach an entry whose name it already knows.
- `w` permits adding/removing names when paired with `x`, subject to ownership and sticky-bit rules.

A file's write bit is not the main control for deleting its name. Deletion usually
depends on the parent directory. To open `/a/b/file`, the process needs search
permission on each directory in the path and the required permission on the file.

```bash
ls -ld / /var /var/log
namei -l /var/log/syslog
```

`ls -ld` displays each named directory itself. `namei -l` (util-linux) follows
the path one component at a time and prints ownership/modes, helping find where
traversal fails. Filesystem paths and protected names vary by host; don't assume
`/var/log/syslog` exists.

## Change one practice file

The setup creates a private temporary directory and a dummy file. Source it from
the repository root as your ordinary user, then inspect and change only that file:

```bash
source fundamentals/labs/setup.sh
stat -c '%A %a %n' "$LINUX_LAB/config/private.txt"
chmod u+x "$LINUX_LAB/bin/hello.sh"
stat -c '%A %a %n' "$LINUX_LAB/bin/hello.sh"
```

`chmod u+x` adds execute for the file owner (`u`) without replacing other bits.
`chmod 750 file` instead assigns owner `rwx`, group `r-x`, others none. Prefer
the symbolic form when you want to add or remove one permission while preserving
the rest. `chmod` changes mode bits; it does not change ownership or parent access.

To demonstrate how a directory's search bit matters, this block creates a fresh
subdirectory within the lab. Run the whole block as your ordinary user; the final
`chmod` restores access. If you stop after the expected failure, run that final
`chmod` line manually before continuing:

```bash
mkdir -p "$LINUX_LAB/access-demo/notes"
printf 'practice only\n' > "$LINUX_LAB/access-demo/notes/readme.txt"
chmod 700 "$LINUX_LAB/access-demo/notes"
chmod 600 "$LINUX_LAB/access-demo/notes/readme.txt"
cat "$LINUX_LAB/access-demo/notes/readme.txt"
chmod 600 "$LINUX_LAB/access-demo/notes"
cat "$LINUX_LAB/access-demo/notes/readme.txt"  # Expected to fail as an ordinary user.
chmod 700 "$LINUX_LAB/access-demo/notes"
cat "$LINUX_LAB/access-demo/notes/readme.txt"
```

The second `cat` cannot traverse the directory; the file remains mode `600`.
The final `chmod` restores the directory so the lab is usable. A privileged
process may get a different result. Do not reproduce this on a real service path.

## Understand umask and access databases

New files receive requested creation permissions with bits removed by the
process's umask. For example, programs commonly request `666` for regular files
and `777` for directories, then the umask removes bits. A umask of `022` often
leads to file mode `644` and directory mode `755`; a umask of `077` commonly
leads to `600` and `700`. Existing files do not change when umask changes.
Default ACLs and applications can alter the simple result.

```bash
umask
(
    umask 077
    : > "$LINUX_LAB/notes/umask-example.txt"
    mkdir -p "$LINUX_LAB/umask-dir"
    stat -c '%a %n' "$LINUX_LAB/notes/umask-example.txt" "$LINUX_LAB/umask-dir"
)
```

Parentheses run a subshell so the temporary umask does not change the calling
shell. `getent passwd "$USER"` and `getent group` query the configured account
sources, which may include network directories as well as local files. A newly
added group is not necessarily active in processes that were already running.

If ACL utilities are installed, `getfacl file` displays additional access entries
and their mask. SELinux/AppArmor denials and read-only mounts require their own
evidence. Do not disable security policy to make a permissions example pass.

## Safe troubleshooting order

1. Identify the user and groups of the process that failed, not only your login.
2. Check the target and each parent directory with `stat`/`namei`.
3. Inspect ACLs and relevant policy only if mode bits do not explain the result.
4. Make the narrowest approved change to a lab or intended path.
5. Recheck the exact file and parent modes, then test as the intended user.

See [users and access](04-users-and-access.md) and the [manual for `chmod`](https://man7.org/linux/man-pages/man1/chmod.1.html).

[Back to the Linux learning path](../README.md)
