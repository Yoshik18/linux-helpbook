# 4. Understand users, groups, and access

Every process runs with user and group credentials. For an ordinary file, Linux checks the owner's permissions first, then the matching group permissions, then the permissions for everyone else. Directories use the same mode bits with different effects: read lists names, execute (`x`) searches/traverses names. This distinction explains why a readable file can still be unreachable through a parent directory.

## Inspect the identity used by this shell

```bash
whoami
id
id -u
id -G
getent passwd "$(id -u)"
```

`whoami` prints the effective username. `id` reports user/group names and numeric IDs; `-u` prints only the effective UID and `-G` prints group IDs. `getent passwd KEY` queries the configured account database (which can include network sources), using the UID produced by `$(...)`. Account records are not proof that another service uses the same credentials. A process keeps its credentials; adding a user to a group does not update already-running processes.

## Read owner, mode, and file type

```bash
ls -ld "$LINUX_LAB" "$LINUX_LAB/config"
ls -l "$LINUX_LAB/config/private.txt"
stat -c '%A %a %U:%G %n' "$LINUX_LAB/config/private.txt"
```

`ls -ld` shows each named directory itself; without `-d`, `ls` lists contents. Long listings show type/mode, owner, group, size, and time. `stat -c` uses GNU format escapes: `%A` symbolic mode, `%a` octal mode, `%U:%G` owner/group names, `%n` path. The fixture's `private.txt` is mode `600`: its owner has read/write, group and others have no mode-bit access. The initial `-` in a mode display indicates a regular file; `d` indicates a directory.

## Change only the permission you intend

```bash
bash "$LINUX_LAB/bin/hello.sh"
chmod u+x "$LINUX_LAB/bin/hello.sh"
"$LINUX_LAB/bin/hello.sh"
stat -c '%A %n' "$LINUX_LAB/bin/hello.sh"
```

`bash FILE` asks Bash to read the script, so the file need not have execute permission. `chmod u+x FILE` adds execute permission for the owner (`u`) without replacing other mode bits. Direct execution also requires a valid interpreter line and a filesystem that permits execution; a `noexec` mount can block it. Both fixture invocations print `hello from the lab` when Bash and execution are available.

Numeric modes encode owner/group/other read (`4`), write (`2`), and execute (`1`) bits. Thus `chmod 600 FILE` means owner read+write, no group/other access. Avoid broad recursive changes: directories need execute/search permission for traversal, unlike ordinary files.

## Umask limits new permissions

```bash
(
    umask 077
    printf 'private note\n' > "$LINUX_LAB/notes/new-private.txt"
    mkdir -p "$LINUX_LAB/private-dir"
    stat -c '%a %n' "$LINUX_LAB/notes/new-private.txt" "$LINUX_LAB/private-dir"
)
```

In the subshell, `umask 077` removes group/other permissions from subsequently created objects. With the usual requested creation modes and no inherited default ACL, expect file `600` and directory `700`. The parentheses keep the umask change local to this compound command. Umask affects creation, not existing files, and cannot add permission bits that the program did not request.

## Diagnose path traversal and ACLs

```bash
namei -l "$LINUX_LAB/config/private.txt"
getfacl "$LINUX_LAB/config/private.txt"
```

If installed, `namei -l` displays each path component and its mode/owner. To reach a named file, a user needs search (`x`) permission on every parent directory. Directory `r` permits listing names; directory `x` permits lookup/traversal. `getfacl` displays access-control-list entries and the ACL mask, which can limit effective named-user/group permissions; the `acl` utilities may not be installed. SELinux/AppArmor policy, read-only mounts, or other constraints can deny access even when mode bits look permissive. Do not use `chmod 777` or disable protections as a diagnostic shortcut.

**Try it:** Create a private note, set owner-only read/write access, inspect the numeric mode and each directory in its path.

```bash
printf 'practice\n' > "$LINUX_LAB/notes/private-note.txt"
chmod 600 "$LINUX_LAB/notes/private-note.txt"
stat -c '%a %n' "$LINUX_LAB/notes/private-note.txt"
namei -l "$LINUX_LAB/notes/private-note.txt"
```

[Manual: chmod](https://man7.org/linux/man-pages/man1/chmod.1.html) · [umask](https://man7.org/linux/man-pages/man2/umask.2.html) · [Path resolution](https://man7.org/linux/man-pages/man7/path_resolution.7.html) · [Directory-permission lab](permissions.md) · [Previous](03-shell-and-text.md) · [Index](README.md) · [Next](05-processes-and-signals.md)
