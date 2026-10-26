# 5. Users, groups and permissions

[Contents](../README.md) | [Previous: text](04-text.md) | [Next: processes](06-processes.md)

Linux associates each process with a user identity and groups. Files and directories record an owner, a group, and permission bits. Those bits determine what the owner, group members and other users may do. They are one layer of access control, not a complete security policy.

## Identify the current account

```bash
whoami
id
```

`whoami` prints the effective user name. `id` reports the effective user ID, primary group and supplementary groups. Groups often grant access to shared resources. The output describes the current process identity; it does not prove that every command you run has the same effective permissions if you use privilege-changing tools.

## Read permission bits

```bash
ls -l /etc/passwd
ls -ld /tmp
```

The first character of a long listing indicates the kind of entry, such as `-` for a regular file or `d` for a directory. The next nine characters appear in three groups: owner, group and other. `r` means read, `w` means write, and `x` means execute for files, or search/traverse for directories. A hyphen means the permission is absent.

For example, `-rw-r--r--` means the owner can read and write, while group and other users can read. `drwxrwxrwt` on a shared temporary directory includes the sticky bit, which restricts who can remove entries there. Exact ownership and permissions vary by system. These commands only inspect metadata.

Directory permissions behave differently from file permissions. Reading a directory allows listing its names; execute/search permission allows traversing it when the name is known. Creating or removing entries requires write and search permission on the containing directory. A readable file inside an inaccessible directory may still be unreachable by path.

## Check access to a path

The `test` builtin can check a property and returns a status rather than printing a report:

```bash
if test -r /etc/os-release; then
  printf 'readable\n'
else
  printf 'not readable\n'
fi
```

`-r` asks whether the current process can read the path. Access checks can depend on ACLs, mount options, namespaces and other security controls, so this test is useful evidence but not a universal access guarantee for every process.

## Change permissions only when needed

`chmod` changes permission bits. It modifies the target and should not be used casually:

```bash
chmod u+x "$HOME/bin/example"
```

This adds execute permission for the file owner only. Confirm the path first and ensure the file is meant to be executable. `chmod -R 644 directory` is a dangerous pattern: it removes execute/search permission from directories and can make their contents inaccessible. For directories, permissions need to preserve traversal.

`chown` changes file ownership and usually requires administrative privilege. Do not use it to troubleshoot a vague access error until you know which process account, owner and group should have access. On shared systems, changing ownership can disrupt services or other users.

## Numeric modes and default permissions

Permission values use `r=4`, `w=2` and `x=1`. Add the desired bits separately for owner, group and other: `640` means owner read/write (`6`), group read (`4`), and no access for others (`0`).

```bash
chmod 640 -- notes.txt
ls -l -- notes.txt
```

This changes an existing file named `notes.txt` in the current directory; use only a file you own and intend to restrict. Expect the ordinary permission bits to read `rw-r-----`. Unlike `chmod u+x`, a numeric mode replaces the ordinary permission bits rather than adding one bit. A directory with mode `640` lacks traversal permission and is usually unusable for ordinary path access. Do not apply file modes recursively to a mixed tree.

`umask` controls which requested permission bits are removed when new files and directories are created. Run `umask` without arguments to inspect the current shell's mask. A typical mask of `0022` leaves new regular files at `644` when the application requests `666`, and directories at `755` when it requests `777`. It is a bit mask, not general arithmetic subtraction; programs can request fewer permissions, and default ACLs can change the result. Changing the mask affects future creations by this shell and its children, not existing files.

## Privilege and sudo

`sudo` runs an authorized command with elevated privileges, subject to local policy. It does not make a command safe. Before using it, understand the command, target path and effect. Prefer a read-only check without elevation when it answers the question. Never paste a command with `sudo` just to make an error disappear.

## Common confusion

- `x` on a directory means search/traverse, not execute a program.
- A process may lack access because a parent directory is not searchable, even when the file itself is readable.
- Mode bits do not show every access-control layer, such as ACLs or mandatory security policy.
- `sudo` changes privilege, not the correctness of the command.
- Recursive permission changes can remove access from the directories required to reach files.

## Further reading

- [Linux man-pages: path_resolution(7)](https://man7.org/linux/man-pages/man7/path_resolution.7.html)
- [GNU Coreutils: chmod invocation](https://www.gnu.org/software/coreutils/manual/html_node/chmod-invocation.html)
- [Linux man-pages: credentials(7)](https://man7.org/linux/man-pages/man7/credentials.7.html)
