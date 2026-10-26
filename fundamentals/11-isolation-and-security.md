# 11. Inspect limits and security boundaries

Start by inspecting your own process and practice files. These commands do not
create namespaces, alter cgroups, grant capabilities or disable policy.

## Find your shell's namespace memberships

```bash
ls -l "/proc/$$/ns"
readlink "/proc/$$/ns/net"
readlink "/proc/$$/ns/mnt"
readlink "/proc/$$/ns/user"
```

The links identify namespace objects. Compare two permitted processes to see
whether they share a network or mount view. An identifier alone does not prove
“this is secure” or “this is a container.” Ordinary Linux containers share the
host kernel; their separate views are not the same boundary as a VM's kernel.

## Check UID mapping and capability state

```bash
cat "/proc/$$/uid_map"
cat "/proc/$$/gid_map"
grep -E '^(Uid|Gid|CapEff|NoNewPrivs|Seccomp):' "/proc/$$/status"
```

Mapping rows describe inside ID, outside ID and range length, relative to the
reader's namespace. `CapEff` is a hexadecimal effective-capability mask.
`NoNewPrivs` concerns gaining privileges through exec; it does not mean the
process has no privileges. `Seccomp: 2` means filter mode, not proof of a
particular syscall allowlist. Do not infer host authority from a username alone.

## Inspect resource membership separately from isolation

```bash
cat "/proc/$$/cgroup"
findmnt -t cgroup,cgroup2
ulimit -n
ulimit -u
```

Namespaces determine views; cgroups account for and constrain resources. A
private PID list alone does not impose a memory budget. Cgroup v2 uses entries
such as `0::/path`; v1 can show separate controller lines. Resolve the mounted
hierarchy and ancestors before reading specific controller limits. The shell's
`ulimit` values are inherited resource limits, not a complete container policy.
Do not write new limits just to test their effect on a shared host.

## Find overly broad permissions in the lab

```bash
find "$LINUX_LAB/config" -type f -perm /077 -print
stat -c '%a %n' "$LINUX_LAB/config/private.txt"
```

GNU find's `/077` means any group/other permission bit is set. It is a review
filter, not proof every matching file is a security flaw. The dummy private file
should be `600` and absent from that list. The normal app config may appear,
but the parent temporary directory is private. Reachability and policy still
matter; do not blanket-change permissions based only on this query.

If installed, `getfacl` inspects extended file access rules and `getcap` inspects
file capabilities. A successful mode-bit check does not exclude SELinux or
AppArmor denial. Diagnose the applicable policy rather than turning it off.

## Keep inspection output safe to share

Avoid posting full environments, process arguments or application logs without
review: these may contain credentials. Read one required field instead. Do not
run `sudo`, `chmod 777`, privileged containers or host-mount workarounds to make
a denied command succeed. The denial is evidence about a boundary.

## Practice

Show only your shell's effective capability mask and open-file limit. Then find
lab config files with group/other bits set without changing their permissions.

<details>
<summary>One answer</summary>

```bash
grep '^CapEff:' "/proc/$$/status"
ulimit -n
find "$LINUX_LAB/config" -type f -perm /077 -print
```

</details>

[Manual: namespaces](https://man7.org/linux/man-pages/man7/namespaces.7.html)
· [capabilities](https://man7.org/linux/man-pages/man7/capabilities.7.html)
· [cgroup v2](https://docs.kernel.org/admin-guide/cgroup-v2.html)
· [Previous](10-networking.md) · [Index](README.md) · [Next](12-performance-and-debugging.md)
