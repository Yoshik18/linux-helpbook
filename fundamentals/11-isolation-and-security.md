# 11. Isolation and security

[Previous: Networking](10-networking.md) · [Index](README.md) · [Next: Performance and debugging](12-performance-and-debugging.md)

## Isolation has several jobs

A container is not a small virtual machine. Ordinary Linux containers run
processes against a shared host kernel; a VM normally runs a separate guest
kernel behind a virtualization boundary. A separate filesystem view does not
remove the kernel attack surface. Container security depends on several
mechanisms working together, plus runtime configuration and kernel maintenance.

Namespaces change what a process sees. PID namespaces provide process-ID views;
mount namespaces separate mount tables; network namespaces separate network
stacks; user namespaces separate identities and privilege scopes. Processes can
share some namespace types while differing in others. “In a container” is
therefore not a precise description of every boundary. [namespaces.7](https://man7.org/linux/man-pages/man7/namespaces.7.html)

Cgroups answer a different question: how much resource can a group consume?
Controllers account for and constrain resources such as CPU time, memory, I/O
and task counts. A namespace alone does not prevent a workload from exhausting
memory. A cgroup namespace changes the visible cgroup hierarchy; it does not
itself impose a memory limit. [cgroup-v2](https://docs.kernel.org/admin-guide/cgroup-v2.html)

## Permission is more than the username

File ownership, mode bits and ACLs establish ordinary access rules. Capabilities
split traditional root privileges into smaller units, such as network
administration or bypassing file-access checks. Some capabilities remain very
broad: `CAP_SYS_ADMIN` should not be treated as a harmless convenience. [capabilities.7](https://man7.org/linux/man-pages/man7/capabilities.7.html)

“Root in the container” is incomplete information. Without user-namespace
remapping, UID 0 may still be host UID 0, although other controls restrict its
powers. With a user namespace, UID 0 inside can map to an unprivileged UID
outside. Capabilities are interpreted in relevant user-namespace scopes, not
as universal host authority. [user_namespaces.7](https://man7.org/linux/man-pages/man7/user_namespaces.7.html) Neither mapping makes a writable sensitive
host mount safe.

Seccomp filters restrict system calls and can reject selected operations.
They do not replace file permissions or provide a complete sandbox on their
own. [seccomp.2](https://man7.org/linux/man-pages/man2/seccomp.2.html) Linux Security Modules such as SELinux and AppArmor add policy checks;
an operation can satisfy ordinary permissions and still be denied by policy. [Linux Security Modules](https://docs.kernel.org/admin-guide/LSM/index.html)
“No new privileges” prevents gaining privileges through execution mechanisms
such as set-user-ID programs; it is not a label meaning “no privileges exist.”

## Three read-only investigations

These Python 3 examples inspect only the process running the example. They do
not create namespaces, change cgroups, modify security policy or start a
container. `/proc/self` refers to the reading process, not a permanently fixed
PID. Restricted environments may hide interfaces; do not escalate privileges
to bypass that restriction.

### 1. Inspect namespace membership

```bash
python3 - <<'PY'
import os
for kind in ('user', 'pid', 'mnt', 'net', 'cgroup'):
    path = '/proc/self/ns/' + kind
    try:
        print(kind, os.readlink(path))
    except OSError as error:
        print(kind, type(error).__name__)
PY
```

Values such as `net:[...]` identify namespace objects. Matching identifiers for
two permitted processes indicate a shared namespace of that type. A number
alone does not say “secure” or even “container”: compare the relevant
boundaries, not whether the number looks unusual. [namespaces.7](https://man7.org/linux/man-pages/man7/namespaces.7.html)

### 2. Inspect identity translation

```bash
python3 - <<'PY'
from pathlib import Path
for name in ('uid_map', 'gid_map'):
    print(name)
    print(Path('/proc/self', name).read_text(), end='')
PY
```

Each mapping line describes an inside starting ID, an outside starting ID and
a range length. For example, a mapping of inside UID 0 to outside UID 100000
would explain why a file's owner looks different across viewpoints. That is
an illustrative mapping, not expected output. Mapping interpretation depends
on the reader's user namespace; do not infer complete host authority from one
line. [user_namespaces.7](https://man7.org/linux/man-pages/man7/user_namespaces.7.html)

### 3. Inspect resource membership and security state

```bash
python3 - <<'PY'
from pathlib import Path
print(Path('/proc/self/cgroup').read_text(), end='')
for line in Path('/proc/self/status').read_text().splitlines():
    if line.startswith(('CapEff:', 'NoNewPrivs:', 'Seccomp:')):
        print(line)
PY
```

A cgroup v2 membership line has the form `0::/path`; legacy v1 can have separate
controller lines. Actual controller files depend on the mounted hierarchy,
namespace view, kernel and enabled controllers. Do not mechanically append a
host-visible path to a container's `/sys/fs/cgroup`. [cgroup-v2](https://docs.kernel.org/admin-guide/cgroup-v2.html)

`CapEff` is a hexadecimal capability mask, not a risk score. `Seccomp: 2` means
filter mode, not proof of a particular allowlist. Membership also does not prove
limits are configured: inspect the applicable controller settings and ancestors
when authorized.

## Keep the defaults restrictive

Prefer non-root execution, narrow capabilities, enforced runtime security
profiles and explicit resource budgets. Avoid privileged containers, host
namespace sharing and sensitive host mounts unless the design genuinely needs
them and the risks have been reviewed. A denied operation is evidence to
investigate, not an instruction to disable the control.

## Check your understanding

- Why can an isolated process list coexist with unrestricted memory consumption?
- What changes when container UID 0 maps to a nonzero outside UID?
- Why can a readable file still be blocked by a security policy?
