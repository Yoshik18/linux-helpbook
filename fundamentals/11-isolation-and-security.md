# 11. Understand Linux isolation and access controls

Linux security is layered. Namespaces give processes different views of resources; cgroups account for and constrain resource use; capabilities divide some privileged operations; file modes and ACLs govern discretionary access. Seccomp and Linux security modules add further restrictions. None is a magic label that proves a process is safe.

Use read-only checks on your own process and the disposable practice files. `/proc` visibility varies with kernel, permissions and container settings. These examples do not create namespaces, change limits or grant privileges.

## Namespaces: which view does a process see?

```bash
ls -l "/proc/$$/ns"
readlink "/proc/$$/ns/net"
readlink "/proc/$$/ns/mnt"
readlink "/proc/$$/ns/pid"
```

`$$` is this Bash process ID. Namespace links identify the namespace objects for networking, mounts and process IDs. Compare permitted PIDs to see whether they share a view; a matching identifier indicates shared membership, not whether the overall system is secure. A container typically shares the host kernel even when it has separate views. A VM has a separate guest kernel. PID namespace behavior also makes the same process appear under different IDs in different views.

## Cgroups: what resource budget applies?

```bash
cat "/proc/$$/cgroup"
findmnt -t cgroup,cgroup2
```

The first reports cgroup membership; the second shows mounted cgroup filesystems when `findmnt` is available. On cgroup v2, a line such as `0::/some/path` identifies membership relative to a hierarchy. Controller files such as `memory.current`, `memory.max`, `cpu.max`, and `memory.events` may be present at the resolved directory. cgroup namespaces can virtualize the visible paths, but membership/view separation alone does not impose a resource limit. v1 uses different controller paths. Parent cgroups can impose tighter limits than a leaf. Do not guess a filesystem path by concatenating membership text: mount roots and namespaces affect mapping. A membership path alone does not tell you the effective limit.

## Capabilities: which privileged operations are available?

```bash
grep -E '^(Uid|Gid|CapInh|CapPrm|CapEff|CapBnd|NoNewPrivs|Seccomp):' "/proc/$$/status"
cat "/proc/$$/uid_map"
cat "/proc/$$/gid_map"
```

The status fields report numeric credentials, capability sets as hexadecimal masks, no-new-privileges state and seccomp mode. `CapEff` is the effective set now; it is not a human-readable list. `uid_map`/`gid_map` relate IDs inside this user namespace to IDs outside it. `NoNewPrivs: 1` prevents privilege gains through exec, but does not remove existing authority. `Seccomp: 2` indicates filter mode, not which system calls the filter allows. Do not infer host authority from a displayed username or mask alone. `capsh --print` can decode capabilities when the libcap tools are installed; inspect local help and avoid pasting sensitive process status publicly.

## Permissions: follow the whole path

After the shared setup in chapter 1:

```bash
id
stat -c '%A %a %U:%G %n' "$LINUX_LAB/config/private.txt"
namei -l "$LINUX_LAB/config/private.txt"
```

When the ACL utilities are installed, inspect the extra access entries too:

```bash
getfacl "$LINUX_LAB/config/private.txt"
```

The output includes ACL entries and the ACL mask, which can limit named-user or group permissions. If these tools are absent, skip this query; do not install software on a real host just to finish the lesson. Mode bits still do not describe SELinux/AppArmor rules, read-only mounts, or every access condition. A permission failure is evidence to inspect the applicable boundary, not a reason to run `chmod 777` or disable policy.

For review, GNU `find` can locate group/other permission bits in the lab:

```bash
find "$LINUX_LAB/config" -type f -perm /077 -print
```

`-perm /077` matches any group or other bit. It flags candidates for review, not necessarily vulnerabilities; intended sharing and parent-directory reachability matter. No permissions are changed.

## Practice: distinguish view from limit

Record your shell's network namespace link and cgroup membership. Ask: which output indicates a different view, and which identifies resource accounting membership? If permitted, compare with a second process you own. Do not launch privileged containers or write cgroup controls for this exercise. Explain why neither output alone demonstrates a secure isolation boundary.

[Manual: namespaces](https://man7.org/linux/man-pages/man7/namespaces.7.html) · [capabilities](https://man7.org/linux/man-pages/man7/capabilities.7.html) · [cgroup v2](https://docs.kernel.org/admin-guide/cgroup-v2.html) · [Previous](10-networking.md) · [Index](README.md) · [Next](12-performance-and-debugging.md)
