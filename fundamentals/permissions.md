# File permissions without breaking directory access

A file's permissions control access to its contents. A directory's permissions
control access to its entries. The same numeric mode can mean very different
things depending on which one you change.

## Read the mode

```bash
ls -ld .
stat -c '%A %a %U:%G %n' .
```

`stat -c` is GNU syntax. The first character in `ls -l` identifies the type:
`d` is a directory, `-` a regular file. The next three groups describe the owner,
group and everyone else. Each group can have read (`r`), write (`w`) and execute
or search (`x`) permission.

For a regular file, `x` allows execution, subject to the interpreter, mount
options and other controls. For a directory:

- `r` allows listing the names of entries.
- `x` allows searching/traversing the directory to access a named entry.
- `w`, normally together with `x`, allows creating and removing entries.

Deleting a file generally depends on permissions on its parent directory, not
whether the file itself is writable. Sticky-bit directories add restrictions.
ACLs, SELinux/AppArmor policies, capabilities and read-only mounts can also affect
access. Basic mode bits do not explain every `Permission denied` error.

## Try it in a private lab

Run this as your ordinary user, not root. The lab creates one temporary directory
and changes only a child inside it. It does not change your home permissions.

```bash
lab=$(mktemp -d) || exit 1
mkdir "$lab/notes"
printf 'hello\n' > "$lab/notes/example.txt"
chmod 700 "$lab/notes"
chmod 600 "$lab/notes/example.txt"
cat "$lab/notes/example.txt"

# Remove search permission from the directory, not the file.
chmod 600 "$lab/notes"
cat "$lab/notes/example.txt" # Expected: Permission denied for an ordinary user.

# Restore access before trying anything else.
chmod 700 "$lab/notes"
cat "$lab/notes/example.txt"
printf 'Lab directory: %s\n' "$lab"
```

A privileged process may bypass the expected failure. Stop and check `id` if your
results differ. Keep the small lab directory for inspection, then remove only
that directory when you are finished.

## What can go wrong?

`chmod -R 644 directory/` applies a regular-file-style mode to directories too.
Their missing `x` bit can make files unreachable even when those files are
readable. Do not repair this by giving everything `777`.

Check the user, groups, parent directory modes and the failing operation first.
If installed, `namei -l /path/to/file` helps inspect the whole path. Choose access
based on who actually needs it. Private configuration is not the same as a
public website's static assets, and executable scripts are not plain text data.

## Interview takeaway

- Why can you list filenames in a directory but fail to open those files?
- Why might a user delete a read-only file from a writable directory?

## Further reading

- [`chmod(1)`](https://man7.org/linux/man-pages/man1/chmod.1.html)
- [`path_resolution(7)`](https://man7.org/linux/man-pages/man7/path_resolution.7.html)

[Back to the learning path](../README.md)
