# 4. Inspect and fix file access

Use the [practice setup](01-how-linux-works.md), as your ordinary user. Do not
use recursive permission resets or `sudo` to hide an unexplained access error.

## See who you are and which groups apply

```bash
whoami
id
id -u
id -G
getent passwd "$(id -u)"
```

`id` shows your current process credentials and groups. `getent` asks the
configured account database, which is not necessarily only `/etc/passwd`.
A running service may have different credentials from your login session. A
new group assignment does not retroactively change every running process.

## Read the mode and ownership

```bash
ls -ld "$LINUX_LAB" "$LINUX_LAB/config"
ls -l "$LINUX_LAB/config/private.txt"
stat -c '%A %a %U:%G %n' "$LINUX_LAB/config/private.txt"
```

The setup gives `private.txt` mode `600`: its owner can read/write it, while
group and other have no mode-bit access. `ls -ld` inspects a directory itself
instead of listing its children. An initial `d` identifies a directory.

## Make one lab script executable

```bash
bash "$LINUX_LAB/bin/hello.sh"
chmod u+x "$LINUX_LAB/bin/hello.sh"
"$LINUX_LAB/bin/hello.sh"
stat -c '%A %n' "$LINUX_LAB/bin/hello.sh"
```

Both invocations print `hello from the lab`. The first asks Bash to read the
file; direct execution also needs execute permission and a usable interpreter.
A `noexec` mount can still block direct execution. `u+x` changes only the owner's
execute bit, unlike assigning a whole numeric mode indiscriminately.

## Observe umask without changing your next terminal command

```bash
(
    umask 077
    printf 'private note\n' > "$LINUX_LAB/notes/new-private.txt"
    mkdir -p "$LINUX_LAB/private-dir"
    stat -c '%a %n' "$LINUX_LAB/notes/new-private.txt" "$LINUX_LAB/private-dir"
)
```

On ordinary creation without inherited default ACLs, expect `600` and `700`.
The parentheses isolate the umask change. Umask removes permissions from a
program's requested creation mode; it does not alter existing files or add bits.

## Find which parent directory blocks access

If installed, use `namei` to inspect the whole path, not just the final file:

```bash
namei -l "$LINUX_LAB/config/private.txt"
```

Every parent needs search (`x`) permission for path traversal. A directory's
`r` lets you list names; `x` lets you access a named entry. This is why
`chmod -R 644 directory/` can break access. Use the focused
[directory-permission lab](permissions.md) to reproduce that safely.

For systems using ACLs, `getfacl "$LINUX_LAB/config/private.txt"` shows extra
entries and the ACL mask. It needs the ACL tools package. SELinux/AppArmor and
read-only mounts can deny an operation even when mode bits look sufficient.
Do not disable those protections or use `chmod 777` as a diagnostic shortcut.

## Practice

Give only yourself read/write access to a new lab note. Inspect its numeric
mode, then identify every directory on the path.

<details>
<summary>One answer</summary>

```bash
printf 'practice\n' > "$LINUX_LAB/notes/private-note.txt"
chmod 600 "$LINUX_LAB/notes/private-note.txt"
stat -c '%a %n' "$LINUX_LAB/notes/private-note.txt"
namei -l "$LINUX_LAB/notes/private-note.txt"
```

</details>

[Manual: chmod](https://man7.org/linux/man-pages/man1/chmod.1.html)
· [umask](https://man7.org/linux/man-pages/man2/umask.2.html)
· [path resolution](https://man7.org/linux/man-pages/man7/path_resolution.7.html)
· [Previous](03-shell-and-text.md) · [Index](README.md) · [Next](05-processes-and-signals.md)
