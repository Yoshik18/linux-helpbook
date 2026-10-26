# 9. Packages and software

[Previous: Boot, services and logs](08-boot-services-and-logs.md) · [Index](README.md) · [Next: Networking](10-networking.md)

## A package is more than an executable

A distribution package contains files plus metadata: its name, architecture,
version, dependencies and sometimes installation scripts. The package database
records which package owns which paths. This lets the distribution coordinate
changes across programs instead of treating every download as an independent
installer.

A repository publishes packages and an index describing available versions.
The high-level manager selects a compatible set from configured repositories;
the lower-level package system records and applies the transaction. Debian and
Ubuntu commonly pair APT with dpkg; Fedora and related systems pair DNF with RPM.
Package names and supported releases differ, even for the same software.

Dependencies are constraints, not just a list of downloads. One program may
require a particular library interface while another conflicts with a proposed
replacement. The newest upstream version is therefore not automatically the
version the distribution will select. Repository priorities, held packages,
architecture and release policy matter too.

## Refreshing information is not upgrading software

In APT, `update` refreshes repository metadata; `upgrade` changes installed
packages. `apt upgrade` may add dependencies but does not remove existing
packages. `full-upgrade` can remove packages to resolve the whole transaction.
These are explanations, not commands to run as part of this chapter. [apt.8.en](https://manpages.debian.org/bookworm/apt/apt.8.en.html)

Do not transfer that vocabulary blindly: DNF's `update` is an alias for
`upgrade` in the referenced DNF documentation. DNF major versions and
distribution policies vary; read the local help before planning changes. [command_ref](https://dnf.readthedocs.io/en/latest/command_ref.html)

A version string may include a distribution revision as well as the upstream
version. Distributions can backport security fixes without adopting every new
upstream feature. Check the distribution advisory and package changelog rather
than declaring software vulnerable from its upstream-looking number alone.

Repository authentication establishes provenance, not harmlessness. APT verifies
signed repository metadata and follows checksums down to package contents; this
is not a separate end-user signature check on every package. A compromised
trusted signing key or a malicious trusted publisher remains a risk. Do not
bypass signature failures to make an installation proceed. [apt-secure.8.en](https://manpages.debian.org/bookworm/apt/apt-secure.8.en.html)

## Three investigations before changing anything

### 1. Installed and available are different facts

On Debian-family systems, these inspect the local database and cached metadata:

```bash
dpkg-query -W bash
apt-cache policy bash
```

The first reports the recorded installed version. The second distinguishes
installed and candidate versions and their known origins. A candidate is what
the current policy would select, not proof that metadata is fresh or an upgrade
has happened. No repository refresh or installation is performed here. [dpkg-query.1](https://man7.org/linux/man-pages/man1/dpkg-query.1.html)

### 2. Find the program the shell actually selects

```bash
command -v bash
printf '%s\n' "$PATH"
dpkg-query -L bash
```

`PATH` is an ordered search list for external commands without a slash.
`command -v` can also identify a builtin, alias or function: its output is not
always a filesystem pathname. Compare an external command's selected path with
the package file list before assuming it is the distribution copy. Local tools
in `/usr/local/bin` or a language environment may take precedence.

Package executables commonly live in `/usr/bin`, configuration in `/etc`, and
shared data in `/usr/share`. Merged-`/usr` layouts can make `/bin` a symlink;
library locations vary by architecture. Query ownership rather than guessing
from a path. RPM systems provide analogous local queries such as `rpm -q bash`
and `rpm -ql bash`; these examples are not tested here.

### 3. Finding a command does not mean it can start

For a trusted, known executable, inspect metadata without executing it:

```bash
readelf -d /usr/bin/bash
```

When present, `NEEDED` entries name shared-library dependencies. The dynamic
loader resolves these using its configured search rules, not shell `PATH`.
A missing library or incompatible ABI (the binary interface between components)
can stop a program before its main logic runs. Loader details differ between
C libraries; the cited reference describes glibc. [ld.so.8](https://man7.org/linux/man-pages/man8/ld.so.8.html)

## Packages, bundles and source builds

A bundled application may carry private libraries; a source build may install
outside the distribution database. Both can be legitimate, but they shift
responsibility for tracking files, vulnerabilities and upgrades. A language
package manager also has its own environment and dependency rules. Avoid
silently overwriting distribution-managed files, and establish an update and
removal plan before choosing an alternative delivery method.

## Check your understanding

- Why might refreshing APT metadata leave a vulnerable running program unchanged?
- How could two shells run different executables for the same command name?
- Why does a valid repository signature not prove a package is safe?
