# 9. Understand software packages and distribution tools

A distribution combines a Linux kernel with system libraries, tools, repositories, and package-management policy. Use the system's package manager for system software: it tracks files and dependencies and receives updates through configured repositories. A package name is not always the same as a command name. Query first; installing or upgrading changes the machine and belongs in a disposable VM or approved maintenance window.

## Identify the distribution and executable

```bash
cat /etc/os-release
command -v bash
command -v curl
```

`/etc/os-release` identifies distribution and release. `command -v` reports what this shell would execute from its current `PATH`; it does not establish package ownership or trust. A command missing from `PATH` may still exist elsewhere. Avoid installing a second copy until you know what is already selected.

## Debian and Ubuntu: query package state and repositories

```bash
dpkg-query -W bash
apt-cache policy bash
apt-cache search '^iproute2$'
apt-cache show iproute2
```

`dpkg-query -W` reads the local installed-package database. `apt-cache policy` compares installed and candidate versions and shows known origins; its metadata can be stale. `apt-cache search` searches available cached package metadata; `show` displays package metadata and dependencies. On Debian-family distributions, `ip` and `ss` are generally provided by `iproute2`.

## Fedora and RHEL-family systems: RPM database and DNF

```bash
rpm -q bash
rpm -ql bash
dnf info iproute
dnf provides '*/ss'
```

`rpm -q` queries installed package state; `rpm -ql` lists its recorded files. DNF queries configured repositories and may refresh or contact them depending on version/configuration. `info` describes a package; `provides` searches which package supplies a path or capability. DNF4 and DNF5 behavior and output can differ; consult `dnf --help` and the distribution's documentation. Older systems may use YUM commands, but do not assume every old instruction applies to current DNF.

## Install only after checking the proposed transaction

These are examples for a disposable lab, not permission to alter a real host:

```bash
# Debian/Ubuntu
sudo apt update
apt install --simulate iproute2 lsof
sudo apt install iproute2 lsof

# Fedora-family alternative; do not run both examples
sudo dnf install --assumeno iproute lsof
sudo dnf install iproute lsof
```

`apt update` refreshes package indexes over the network; it changes local metadata, not installed packages, and may require administrator authorization. Run it only when you intend to refresh the lab's package metadata. `apt install --simulate` previews a transaction without applying it. DNF's `--assumeno` declines confirmation after showing a proposed transaction; support/output may vary by version. Read package names, removals, dependencies, and repository origins before confirming an install. `apt upgrade` upgrades installed packages; `full-upgrade` may remove packages to resolve dependencies. In DNF, `upgrade` is the normal update operation (and `update` is commonly an alias), not the same distinction as APT.

Repository metadata/signatures help verify packages came through trusted configured sources; they are not a reason to disable verification. Do not add unknown repositories, pipe an internet download into a root shell, or accept a package transaction you do not understand. A configured repository can itself be untrusted or inappropriate: verify its identity and signing-key provenance with your administrator or distribution guidance.

For a Debian system, inspect the package's recorded Bash paths and ask the local database which package owns either common merged-`/usr` path:

```bash
type -a bash
dpkg-query -L bash | grep -E '/(usr/)?bin/bash$'
dpkg-query -S /bin/bash /usr/bin/bash
```

`type -a` shows shell resolution; `dpkg-query -L` lists recorded package files; `dpkg-query -S` searches the local ownership database. One path may return no match even when both aliases reach the same executable. Use the package-recorded path for conclusions. For RPM systems, `rpm -ql bash` lists files and `rpm -qf PATH` checks a path; use an actual path from that list. Local files in `/usr/local`, language environments, and bundled applications may not belong to an OS package.

For a trusted ELF executable, inspect dynamic dependencies without running it:

```bash
bash_path=$(command -v bash)
readelf -d "$bash_path"
```

The `NEEDED` entries name shared libraries. `PATH` finds executables; the dynamic loader's library search is a separate mechanism. `command -v` may select a local wrapper rather than the distro binary, so check the path and file type first. Avoid `ldd` on untrusted binaries because some implementations or unusual binaries can execute code during dependency inspection.

## Version strings and security fixes

```bash
dpkg-query -W bash
apt-cache policy bash
```

A distribution may backport a security fix while retaining an upstream-looking version. Conversely, a new-looking version does not alone prove a system is patched. Check the distribution advisory, package changelog, repository, and installed package revision. For RPM systems, `rpm -q bash` and the vendor security advisory are the corresponding starting points.

## Practice

On a lab system, identify the distribution, query the installed Bash package, and find its recorded executable path. Explain why `command -v bash` and package ownership answer different questions. Do not install or upgrade anything for this exercise.

[APT manual](https://manpages.debian.org/bookworm/apt/apt.8.en.html) · [APT repository authentication](https://manpages.debian.org/bookworm/apt/apt-secure.8.en.html) · [DNF command reference](https://dnf.readthedocs.io/en/latest/command_ref.html) · [Previous](08-boot-services-and-logs.md) · [Index](README.md) · [Next](10-networking.md)
