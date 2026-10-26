# 11. Software and packages

[Contents](../README.md) | [Previous: services](10-services.md) | [Next: troubleshooting](12-troubleshooting.md)

A distribution's package manager installs and tracks software from configured repositories. It records dependencies, versions and files. Package managers differ between distributions, so use the tool and documentation for the system you identified in chapter 1.

## Inspect package state before changing it

On Debian and Ubuntu, `dpkg-query` can inspect the local package database without changing it:

```bash
dpkg-query -W -f='${Package} ${Version} ${Status}\n' bash
```

`-W` requests information about matching package records; `-f` chooses the output fields. Single quotes preserve the field expressions for dpkg-query rather than expanding them as shell variables. The query asks about `bash`, printing its recorded name, version and status. `install ok installed` indicates an installed package. Removed packages can retain database records, so a successful query or a version alone does not prove installation. An unknown package can produce an error. This is a Debian-family example, not a universal Linux command.

To inspect configured apt sources, read the files under `/etc/apt/sources.list` and `/etc/apt/sources.list.d/` where present. Repository configuration determines where software comes from and which signing keys are trusted. Do not add a repository or import a key just because an installation guide says to; verify the vendor and follow your organization's policy.

## Updates change the system

On Debian-family systems, `apt update` refreshes local package metadata from configured repositories. It does not install package upgrades. `apt upgrade` installs available updates and changes system files. Both commands contact configured repositories; the latter changes the machine and can affect running services. Do not run them on production systems without an approved change process, backups where appropriate, and a rollback plan.

Other distributions use different tools, such as DNF or Zypper. Never copy apt commands to a different distribution without checking its documentation.

## Find, preview, install and remove a package

On an apt-based system, inspect a package and preview a transaction before changing it:

```bash
apt show tree
apt-get --simulate install tree
```

`apt show` describes the package from local metadata, including version and dependencies. The package `tree` displays directory trees; it is an example, not a required tool. The simulation asks apt-get to calculate an installation without performing it. It may use stale metadata and, when run without root, may not be able to read all configuration. A preview is useful, but not a guarantee that a later real transaction will be identical.

On a machine you own or are authorized to administer, `sudo apt install tree` performs the installation after showing the proposed transaction and asking for confirmation. `sudo` requests administrative execution under local policy; apt downloads packages and changes files. Check every proposed dependency and service change before accepting. Do not add `-y` merely to avoid reading the prompt.

`sudo apt remove tree` removes the package but can leave configuration files. `sudo apt purge tree` also removes package-managed configuration; it does not necessarily remove files created in users' home directories. Review the full removal list before confirming, especially dependencies. These are real changes, not commands to run as part of diagnosis on someone else's machine.

## Package names and files

A package manager tracks ownership of many installed files. On Debian-family systems, `dpkg -S /path/to/file` can identify which installed package owns a path. It may return no owner for files created locally, generated at runtime, or installed outside the package manager. A package inventory is not a complete software inventory if applications were installed by other methods.

## Safer installation reasoning

Before installing software, answer these questions:

1. Which distribution and release is this?
2. Which official repository provides the package?
3. What dependencies and services will be added or changed?
4. How will the package be updated and removed?
5. Is the machine managed by an organization with its own repository policy?

Package installation usually needs administrative privileges. Review the package manager's proposed transaction before confirming it. Avoid piping an unaudited internet script directly into a privileged shell; that grants the downloaded code the authority of the account running it.

## Common confusion

- Refreshing package metadata is not the same as installing upgrades.
- A package being installed does not mean its service is running.
- Package-manager ownership does not cover every file on the machine.
- Repositories and package names differ by distribution and release.
- Installing or updating software is a system change, not a harmless diagnostic.

## Further reading

- [Debian: apt documentation](https://manpages.debian.org/apt/apt.8.en.html)
- [Debian: dpkg-query](https://manpages.debian.org/dpkg-query)
- [Fedora: DNF documentation](https://docs.fedoraproject.org/en-US/quick-docs/dnf/)
- [openSUSE: Zypper reference](https://en.opensuse.org/SDB:Zypper_manual)
