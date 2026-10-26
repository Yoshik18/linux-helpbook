# 4. Users and access

[Previous: shell and text](03-shell-and-text.md) · [Index](README.md) · [Next: processes and signals](05-processes-and-signals.md)

A process requests access using its credentials. The kernel does not decide based on the person at the keyboard or on whether the command sounds administrative. Start a permissions investigation by identifying the process, the object, and the operation that failed.

## Identity is numeric

A **UID** identifies a user; a **GID** identifies a group. Names are labels resolved through the system's account lookup configuration. Files record owner IDs, and processes carry user and group credentials, including supplementary groups. [credentials(7)](https://man7.org/linux/man-pages/man7/credentials.7.html) A service account gives a program an identity without requiring an interactive human login.

Real IDs describe process ownership, while effective IDs normally determine its active privileges. Linux file checks technically use filesystem IDs, which ordinarily match the effective IDs. [credentials(7)](https://man7.org/linux/man-pages/man7/credentials.7.html) Most everyday commands do not change these identities, but the distinction matters when inspecting privileged programs.

**Authentication** establishes an identity, for example by verifying an SSH key. **Authorization** decides what that identity may do. Successfully logging in does not grant permission to read every file. A service can be denied access even when the same operation succeeds in your interactive shell, because the service has different credentials or restrictions.

Supplementary groups provide additional group-based access. Processes inherit credentials, so editing account membership does not automatically rewrite every already-running process's group list. [credentials(7)](https://man7.org/linux/man-pages/man7/credentials.7.html) A new login or service restart may be needed after an authorized membership change. Compare the credentials of the process that actually failed, not only an account database entry.

## Permissions describe operations

Basic mode bits select owner, group, or other permissions. Without an extended ACL, the owner class is used if the UID matches; otherwise a matching group class is used, then other. These are not three opportunities to add permissions together. [path_resolution(7)](https://man7.org/linux/man-pages/man7/path_resolution.7.html)

For regular files, read and write concern contents; execute allows attempting execution, subject to other checks. For directories, read lists names, execute means search/traversal, and write together with search normally permits creating or removing entries. Every directory along a path matters. Removing a file is generally controlled by its parent directory, with extra restrictions in sticky-bit directories. [path_resolution(7)](https://man7.org/linux/man-pages/man7/path_resolution.7.html) [inode(7)](https://man7.org/linux/man-pages/man7/inode.7.html) Use the existing [permissions reference and directory-access exercise](permissions.md) for mode notation and a focused traversal experiment; there is no reason to replace it with a recursive permission reset.

**Root** is UID 0, but Linux divides privileged operations into capabilities. A privileged process can bypass many basic access checks; capabilities, namespaces, security policies, and read-only mounts still matter. Treat “root can do anything” as an unsafe debugging shortcut, not a complete model.

`sudo` runs an authorized command as another identity, commonly root, according to local policy. It is not a repair for an unexplained denial. A broad group membership or permission change may grant much more access than the one operation you intended. This chapter neither changes accounts nor invokes `sudo`.

## Lab: observe creation policy without changing your session

A **umask** removes permission bits from the mode a program requests for a new object. It does not add permissions or change existing files. Without a default ACL, creation uses `requested_mode & ~umask`: ordinary shell-created files requesting `666` become `600` under mask `077`, while directories requesting `777` become `700`. [umask(2)](https://man7.org/linux/man-pages/man2/umask.2.html) This is bit masking, not general arithmetic subtraction.

Prerequisites: Bash, GNU `stat`, and an existing writable scratch parent. This lab changes only its own newly created files. The subshell prevents its umask from affecting later commands in your session. It does not need root.

```bash
(
    lab=$(mktemp -d "${TMPDIR:-/tmp}/linux-access.XXXXXX") || exit 1
    id -u
    id -g
    id -G
    umask 077
    printf 'practice data\n' > "$lab/private.txt"
    mkdir "$lab/private-dir"
    stat -c '%a %n' "$lab/private.txt" "$lab/private-dir"
    umask 022
    printf 'another file\n' > "$lab/ordinary.txt"
    stat -c '%a %n' "$lab/private.txt" "$lab/ordinary.txt"
    printf 'Retained lab: %s\n' "$lab"
)
```

Expect `600` and `700`, then `600` and `644`. Changing the umask did not loosen the first file. Numeric IDs depend on your session. The private parent directory also limits traversal: a `644` file inside it is not automatically accessible to everyone.

**Validation:** this lab block has not been run. No account changes, privilege escalation, or cross-user access checks were run. Results may differ under inherited default ACLs: Linux applies default-ACL inheritance rather than the ordinary umask calculation. [umask(2)](https://man7.org/linux/man-pages/man2/umask.2.html)

If modes look permissive but access still fails, inspect parent directories, ACLs, mount restrictions, and the service's isolation settings. ACLs add named-user/group rules and a mask; SELinux and AppArmor can impose additional policy through Linux Security Modules. [acl(5)](https://man7.org/linux/man-pages/man5/acl.5.html) [Linux Security Modules](https://docs.kernel.org/admin-guide/LSM/index.html) Do not disable those policies merely to make a test pass.

## Check your understanding

1. Why can a fresh login see new group access while an existing service still cannot?
2. Why does setting a more permissive umask leave an old file unchanged?
3. Can a file with mode `644` remain unreachable to another user? Explain the directory checks.
