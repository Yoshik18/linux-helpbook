# 9. Find, install and inspect software packages

First identify the distribution. Package names and commands differ. Inspection
is safe to start with; installation and upgrades change the machine and belong
in a disposable VM or an explicitly approved maintenance window.

## Check what is already available

```bash
cat /etc/os-release
command -v bash
command -v curl
command -v ss
```

A tool missing from `PATH` may be absent, installed elsewhere or hidden by an
environment. Do not install another copy before checking the selected executable.

## Debian/Ubuntu: query before installing

```bash
dpkg-query -W bash
apt-cache policy bash
apt-cache search '^iproute2$'
apt-cache show iproute2
```

`dpkg-query -W` reads installed package information. `apt-cache policy` separates
the installed version, candidate and origins from cached metadata. A candidate
is not proof the cache is current. On Debian-family systems, `ss` and `ip` are
normally supplied by `iproute2`.

On Fedora/RHEL-family systems, analogous queries include:

```bash
rpm -q bash
rpm -ql bash
dnf info iproute
dnf provides '*/ss'
```

`rpm` queries the local database; DNF queries may contact configured repositories.
DNF4/DNF5 and distribution versions differ. Use local help for exact behavior.

## Install only in your own disposable lab

These commands change packages and may require elevation. They are examples,
not executed checks or approval to update a real server:

```bash
# Debian/Ubuntu lab
sudo apt update
sudo apt install iproute2 lsof

# Fedora-family lab: use this alternative, not both sets
sudo dnf install iproute lsof
```

APT `update` refreshes metadata; it does not upgrade installed packages. `apt
upgrade` changes installed software and differs from `full-upgrade`, which may
remove packages to resolve dependencies. In the referenced DNF documentation,
`update` is an alias for `upgrade`: do not transfer APT vocabulary blindly.
Never disable repository signature checks to get past an error.

## Find which package owns an executable

```bash
type -a bash
dpkg-query -L bash
# Query the path recorded in the package's file list above.
# Depending on the distribution, that can be /bin/bash or /usr/bin/bash.
dpkg-query -S /bin/bash /usr/bin/bash
```

One of those paths may report no match. Package databases do not necessarily
resolve filesystem aliases: on merged-`/usr` systems both paths can reach the
same executable while only one is recorded. Use the path shown by `dpkg-query -L`.
A local copy in `/usr/local/bin` can win over a distribution copy in `/usr/bin`.
For RPM systems use `rpm -qf` with the path recorded by `rpm -ql bash`.
A language virtual environment or bundled application may not be owned by the
OS package database at all.

For a trusted executable with ELF tools installed:

```bash
readelf -d /usr/bin/bash
```

`NEEDED` entries list dynamic-library dependencies. Library lookup is separate
from shell `PATH`. Do not use `ldd` indiscriminately on untrusted downloads;
inspecting a file and executing an unfamiliar loader are different risks.

## Practice

Find the installed Bash version and identify its package-owned files. Explain
why an older-looking version string is not sufficient proof of a vulnerability.

<details>
<summary>One Debian-family answer</summary>

```bash
dpkg-query -W bash
dpkg-query -L bash
apt-cache policy bash
```

Distributions may backport fixes. Consult the distribution advisory and package
changelog before judging security by the upstream-looking version alone.

</details>

[Manual: APT](https://manpages.debian.org/bookworm/apt/apt.8.en.html)
· [APT repository trust](https://manpages.debian.org/bookworm/apt/apt-secure.8.en.html)
· [DNF](https://dnf.readthedocs.io/en/latest/command_ref.html)
· [Previous](08-boot-services-and-logs.md) · [Index](README.md) · [Next](10-networking.md)
