# 11. Software and packages

[Contents](../README.md) | [Previous: services](10-services.md) | [Next: troubleshooting](12-troubleshooting.md)

You want a command that draws a directory as a branching tree. A guide mentions a program called `tree`, but your shell cannot find it. Downloading a file with that name is not enough: you need the right version for your system, any other software it needs, and a way to receive fixes later.

Linux distributions usually provide a way to handle these jobs together. This chapter follows the decision from “is it already installed?” through finding a package, reading a proposed change, and understanding removal. You can do much of the investigation without permission to change the machine. Installation is a separate decision.

## In this chapter

- [What a package manager keeps track of](#what-a-package-manager-keeps-track-of)
- [Choose the instructions for your distribution](#choose-the-instructions-for-your-distribution)
- [Start with what is already installed](#start-with-what-is-already-installed)
- [Find which package supplied a file](#find-which-package-supplied-a-file)
- [Look for tree in the available packages](#look-for-tree-in-the-available-packages)
- [Refreshing information is not upgrading software](#refreshing-information-is-not-upgrading-software)
- [Preview an APT change before installing](#preview-an-apt-change-before-installing)
- [What installation and removal really do](#what-installation-and-removal-really-do)
- [Follow the same reasoning on a DNF system](#follow-the-same-reasoning-on-a-dnf-system)
- [When the package manager does not tell the whole story](#when-the-package-manager-does-not-tell-the-whole-story)
- [Further reading](#further-reading)

## What a package manager keeps track of

A program often needs more than its executable file. It may also need help pages, default settings, and shared code that other programs use. A **package** collects files together with information about them: a name, a version, which files belong to it, and what else must be present for it to work. Some packages contain only shared code, documentation, or settings rather than a command you run directly.

The program that installs these packages also keeps records of them. That is the **package manager**. Rather than dropping unknown files into system directories, it records which package supplied which paths. Later it can replace those files with a newer version or remove the package.

Packages are normally obtained from a **repository**, a maintained collection of packages with a searchable catalogue. A distribution configures repositories appropriate for its release. Your machine keeps a local copy of catalogue information so that every search does not need to download the full catalogue again. That information is called **metadata**. It describes packages; it is not the installed programs themselves.

These are three different things:

- The installed-package database says what the machine records as installed.
- The local repository metadata says what software the machine knows it can obtain.
- The repositories themselves hold packages that may be newer than the last local metadata refresh.

A package may be available but not installed, like a book listed in a library catalogue that you have not borrowed. Conversely, an installed package can remain on a machine after the repository that supplied it is disabled. “Installed” and “available” answer different questions.

If a program needs shared code supplied by another package, that relationship is a **dependency**. Installing one requested package can therefore mean installing several packages. Dependencies can require particular versions, not just particular names. The package manager works out a compatible set of changes, often called a **transaction**, before applying it. Read that whole set, not just the name you requested.

A package installation can also run setup instructions with administrative authority. Those instructions may create a service account, prepare settings, or start a service. Packages are not merely compressed downloads, and trusting their source matters.

## Choose the instructions for your distribution

Use the distribution and release identified in [chapter 1](01-system.md). If you need to check again, `cat` prints a file's contents, and `/etc/os-release` is the system's distribution identification file:

```bash
cat /etc/os-release
```

Look for `ID`, `VERSION_ID`, and the human-readable `PRETTY_NAME`. Do not choose a package manager just because its command happens to exist. A machine can have extra package tools installed without using them to manage its operating system.

**Debian and Ubuntu** use APT to search repositories and calculate changes, with `dpkg` maintaining the installed Debian-package records. Their package archives usually end in `.deb`. The next sections use this family.

**Fedora and many Red Hat Enterprise Linux-related systems** use DNF with RPM package records. Their package archives usually end in `.rpm`. There is a separate [DNF walkthrough below](#follow-the-same-reasoning-on-a-dnf-system). DNF 4 and DNF 5 are different implementations; the command named `dnf` depends on the distribution and release.

**openSUSE** commonly uses Zypper, not APT or DNF. Other distributions have other managers. Also, image-based editions such as Fedora Atomic desktops manage the base system differently from conventional package-managed installations. Use the documentation for that edition rather than treating all Fedora systems alike.

Even within one family, package names and repository contents can differ between releases. A Debian package is not automatically appropriate for Ubuntu, nor is every RPM appropriate for every RPM-based distribution.

## Start with what is already installed

Before looking for new software, see what the local records can tell you. We will first inspect Bash, the shell used throughout this handbook, so that there is an installed package to examine before investigating `tree`.

On Debian or Ubuntu, `dpkg-query` reads the local package database. `-W` requests a package record. `-f` chooses the fields to print, and the final word, `bash`, is the package name:

```bash
dpkg-query -W -f='${Package} ${Version} ${Status}\n' bash
```

The single quotes tell the shell to leave the text inside them alone. Otherwise it could try to expand `${Package}` as a shell variable before `dpkg-query` sees it. Here those expressions belong to `dpkg-query`, which replaces them with database fields. The `\n` asks it to end the output with a newline.

Exact output observed on a Debian 13 system:

```text
bash 5.2.37-2+b8 install ok installed
```

The first field is the package name, followed by its version. Do not expect your version to match. Distribution versions can include extra revision text because a distribution may apply fixes to the version it maintains.

The important part for our question is `install ok installed`: the package is recorded as installed. A successful query by itself is not enough. Some removed packages retain records because configuration files remain; those records have a different status.

Now ask the same question about `tree`:

```bash
dpkg-query -W -f='${Package} ${Version} ${Status}\n' tree
```

Exact error observed on the same system:

```text
dpkg-query: no packages found matching tree
```

This query exited with status 1 rather than 0, indicating that it did not find the requested record. It does **not** mean that `tree` cannot be installed. It means this local database has no matching package record. It also does not rule out a separately installed executable with that name. We have answered the local-record question, not the repository question.

## Find which package supplied a file

Sometimes you know the file's path but not the package's name. `dpkg-query -S` searches recorded package file lists. The capital `-S` means search for a path, not show package status:

```bash
dpkg-query -S /usr/bin/bash
```

Exact output on the same Debian system:

```text
bash: /usr/bin/bash
```

This says the package named `bash` records `/usr/bin/bash` as one of its paths. “Owns” in this context means supplied by a package. It is not the user or group ownership shown by `ls -l` in the permissions chapter.

There is a useful trap here. You might know Bash as `/bin/bash` and try:

```bash
dpkg-query -S /bin/bash
```

On the inspected system, that produced this exact error:

```text
dpkg-query: no path found matching pattern /bin/bash
```

The program was not missing. Many current systems make `/bin` a link to `/usr/bin`, while package records use one particular spelling of the path. `readlink -f` follows links and prints the resolved path:

```bash
readlink -f /bin/bash
```

Exact output there:

```text
/usr/bin/bash
```

Querying that resolved path with the earlier `dpkg-query -S /usr/bin/bash` command found the owner. On an older layout, `/bin/bash` itself may be the recorded path. Investigate the spelling before concluding that a system file came from an unknown installer.

A no-owner result can also be entirely reasonable. A file might have been created by a user, generated by a running program, or installed outside the distribution's package manager. File ownership queries search recorded package contents, not the history of everything ever written to disk.

## Look for tree in the available packages

APT searches local package descriptions rather than only installed-package records. On Debian or Ubuntu, `apt search` looks for matching text in package names and descriptions:

```bash
apt search tree
```

This does not install anything or refresh repository metadata. It can return many results because `tree` also appears in descriptions of unrelated software. Finding a result is a reason to read further, not a reason to install the first match.

If the local metadata includes the `tree` package, `apt show` displays its description and other fields:

```bash
apt show tree
```

**Conditional example, not captured output:** in metadata that includes this package, look for a `Package: tree` field, a `Version:` field, and a description saying it displays a directory tree. Read `Depends:` to see required packages, when that field is present. `Recommends:` lists additional software considered useful but not a hard dependency; APT normally installs recommendations too. `Installed-Size:` estimates the package's unpacked size, not the total space for all dependencies.

Neither search results nor `apt show` prove installation. For that, return to the installed-status query. To compare an installed version with the version APT would choose, use `apt-cache policy`:

```bash
apt-cache policy bash
```

`apt-cache` is another APT information tool. `policy` reports version choices. Exact output on the inspected Debian system:

```text
bash:
  Installed: 5.2.37-2+b8
  Candidate: 5.2.37-2+b8
  Version table:
 *** 5.2.37-2+b8 100
        100 /var/lib/dpkg/status
```

`Installed` is what the package database records. `Candidate` is the version APT would currently select under its configuration. A different candidate version can indicate an upgrade is available. `(none)` in the installed field means no installed version is recorded.

Here the only source shown is `/var/lib/dpkg/status`, the installed-package database. This machine had no downloaded repository indexes. The equal versions therefore do **not** demonstrate that Bash is up to date with the distribution's repositories. APT can only reason from the information it has. The numbers such as `100` are selection priorities; changing those priorities is not needed for this investigation.

This limitation also affected the `tree` search. `apt search tree` returned unrelated installed packages, while `apt show tree` ended with `Error: No packages found`. That is a real example of incomplete local information, not proof that Debian has no `tree` package.

APT may also print a warning that its command-line interface is not stable. The warning concerns relying on its output format in scripts. These are interactive inspection examples; for automation, use the dedicated APT tools and documented interfaces rather than parsing this chapter's screen layout.

## Refreshing information is not upgrading software

Suppose the package is not found, or the metadata is old. The next question is whether the machine has the right repository configuration and current catalogue information, not whether to download a random installer.

APT reads repository configuration from `/etc/apt/sources.list`, where present, and files under `/etc/apt/sources.list.d/`. Common file formats end in `.list` or `.sources`. They identify repository locations and which release and components to use; configuration can also specify signing keys. Some systems use only the directory and have no main `sources.list` file.

On a machine you are authorized to administer, this command refreshes APT's local catalogue:

```bash
sudo apt update
```

**Administrative example, not executed here.** `sudo` requests permission to run the command with administrative authority under the machine's policy. `update` downloads package information from configured repositories and writes local metadata. It does not install newer programs. It is not a read-only inspection, even though it leaves installed package versions alone.

After a successful refresh, repeat the search, description, and candidate checks. If the refresh reports failed downloads or signature errors, do not assume that all information is current just because some sources succeeded. Check the configured release, connectivity, and repository status before continuing. Do not bypass signature checks to make an error disappear.

Installing the newer versions is a separate operation:

```bash
sudo apt upgrade
```

**Administrative example, not executed here.** This calculates and applies available upgrades to installed packages. It can download packages, replace files, and run package setup instructions. Services may restart, and some changes need a reboot before they fully take effect. On an important machine, use its approved maintenance process, including appropriate backups and a recovery plan.

`apt upgrade` can add packages needed by upgrades but does not remove installed packages to make the upgrade work. `apt full-upgrade` can remove packages when resolving a wider set of changes. It is not a harmless alternative to try when something is held back. Also, `apt-get upgrade` has different defaults about adding dependencies from `apt upgrade`; similar names do not make all APT tools interchangeable.

The same distinction applies to security fixes: refreshing metadata may reveal them, but does not apply them. Conversely, a package version that looks older than the software developer's newest release may still contain fixes maintained by the distribution. Follow that distribution's security notices rather than comparing version strings alone.

## Preview an APT change before installing

Return to the `tree` decision. You have checked the package's purpose and source; now ask what installing it would change. `apt-get` is a separate APT command suited to explicit operations. Its `--simulate` option calculates a change without downloading or installing packages:

```bash
apt-get --simulate install tree
```

There is deliberately no `sudo`. Simulation normally works as an ordinary user, although unreadable configuration can make a user's preview incomplete. It also does not lock the package database against other changes, so a later real transaction can differ.

On the inspected system, which lacked repository indexes, the command failed. Its exact final error was:

```text
E: Unable to locate package tree
```

The preceding lines said that it was a simulation and that APT was reading package lists and state information. Exit status was 100. No installation occurred. The correction, on an authorized machine, is to check sources and arrange a successful metadata refresh, then repeat the preview. Adding `sudo` to the failed simulation does not supply the missing catalogue. The refresh was not performed for this example.

**Conditional example, not captured output:** with appropriate metadata, a simulation may list new packages, upgrades, removals, and packages left unchanged. Lines beginning `Inst` describe planned unpacking or installation, `Conf` describes planned package configuration, and `Remv` describes planned removal. These describe what would happen, not changes already applied. Read dependency names as well as `tree`. If the plan includes removing something important or upgrading far more than expected, stop and investigate.

We can still see a successful simulation using a package already known locally:

```bash
apt-get --simulate install bash
```

The exact closing lines on the inspected system were:

```text
bash is already the newest version (5.2.37-2+b8).
bash set to manually installed.
0 upgraded, 0 newly installed, 0 to remove and 0 not upgraded.
```

Even “set to manually installed” was only a proposed change because `--simulate` was present. APT tracks whether a package was explicitly requested or brought in as a dependency; that record helps decide what might later be unnecessary. The simulation did not change that record. “Newest” here still means newest according to this machine's limited local information, not a fresh comparison with Debian's servers.

## What installation and removal really do

The `sudo` commands in this section are **conditional administrative examples, not commands executed for this chapter**. Use them only on a machine you own or are authorized to manage, after checking its metadata and proposed changes. The separate removal simulation only calculates a proposal; it does not approve or apply it.

For an approved installation on Debian or Ubuntu:

```bash
sudo apt install tree
```

Without `--simulate`, this is a real change. APT normally presents a proposed transaction and asks for confirmation when changes are needed. Read the package source, any new dependencies, upgrades, removals, download size, and disk-space estimate. Answer no if the plan is not what you intended. Do not add `-y` to skip the decision: that option automatically answers yes to prompts.

APT then obtains packages, checks them using its configured trust information, and arranges installation. Trust checks help establish that packages come from the configured source without undetected alteration. They do not make every third-party repository safe. Adding a repository or importing its signing key is a trust decision about future system software, not just a way to get one command.

After a successful installation, repeat the `dpkg-query` status command for `tree`. A recorded installed status answers whether the package is present. If its command is still missing, check the command's name and location rather than immediately reinstalling. A package name and executable name need not match.

### Use the command you installed

An installed-package record is one check. Running the intended command is another. After an authorized `tree` installation, create a tiny directory arrangement in a writable practice location:

```bash
mkdir package-example && mkdir package-example/notes package-example/reports
```

The first `mkdir` creates the outer directory. Only if it succeeds does `&&` run the second command, which creates two directories inside it. If a name already exists, stop rather than reusing unknown content. Now ask the newly installed program to display this exact directory:

```bash
tree package-example
```

This is a **conditional post-installation walkthrough, not an executed `tree` result here**. A schematic excerpt, with the final summary omitted, is:

```text
package-example
├── notes
└── reports
```

`package-example` is the starting directory. Each branch leads to a directory inside it. There are no files in this example. Colors and drawing characters can differ. The useful result is that this invocation finds the command and displays the two names you created, not merely that the package database has an entry.

If the shell still says `tree: command not found`, check `command -v tree`. As explained in chapter 2, that asks how this shell resolves a command name; it does not install anything. Compare the package's installed file list and your shell's search path before repeating an installation. This use of `tree` also applies after an approved DNF installation below.

When finished with this empty example, remove its directories:

```bash
rmdir package-example/notes package-example/reports
rmdir package-example
```

`rmdir` refuses a nonempty directory, so extra files are a reason to inspect rather than delete more broadly. The directory setup and cleanup can be used independently of `tree`; no installation is needed just to understand their arrangement.

Removal also deserves a preview:

```bash
apt-get --simulate remove tree
```

This calculates removal using current local information without removing packages. If `tree` is unknown locally, it may fail as the installation preview did. If it is installed, inspect the entire proposed removal list: removing a package needed by another application can require removing that application too.

For a removal you have reviewed and approved:

```bash
sudo apt remove tree
```

`remove` removes the package's installed software but can retain package-managed configuration so that reinstalling can reuse settings. For Debian packages, removing those configuration leftovers as well is a separate action:

```bash
sudo apt purge tree
```

`purge` can apply to a package whose software was already removed. It is not a general cleanup of everything the application ever touched. Neither removal nor purging should be treated as a promise to erase files in your home directory or application data elsewhere. Back up data you care about before consequential changes.

APT may report automatically installed packages that are no longer required. `apt autoremove` is a further removal operation, not a synonym for refreshing metadata. It proposes removing packages according to dependency records. Review that proposal separately; an application you still use may once have arrived as someone else's dependency.

Installing a service package is also different from proving that the service is running correctly. Installation records belong here; process, service, and log checks belong in [chapter 10](10-services.md).

## Follow the same reasoning on a DNF system

This section applies to a conventional DNF-managed Fedora or related system, **not to the Debian system used for the observed output above**. DNF and RPM were unavailable there, so the following is a documentation-based conditional walkthrough, with no claim of captured DNF output. Use your distribution's supported DNF version. The examples use the command name `dnf`; on a system that documents `dnf5` explicitly, follow that documentation.

### Check the installed record and file owner

RPM can answer local installed-package questions without consulting repositories. `rpm -q` means query an installed package by name:

```bash
rpm -q bash
```

If installed, it normally prints a name with version, distribution release information, and processor architecture. Those extra parts identify the package build. If absent, it reports that the package is not installed. This is a local-record check, not a search for downloadable packages.

To ask which installed package supplied a particular file, combine `-q` with `-f`, the file-selection option:

```bash
rpm -qf /usr/bin/bash
```

This asks for the package owning that installed path. As with Debian, locally generated or separately installed files may have no owner. An ownership result does not prove that the file has never been modified since installation.

### Search and read without refreshing metadata

For this walkthrough, `--cacheonly` tells DNF to use cached repository information instead of refreshing it over the network:

```bash
dnf --cacheonly search tree
```

`search` looks for matching package text. Once the name is identified, `info` displays details:

```bash
dnf --cacheonly info tree
```

Read whether the information is about an installed package or an available package. Do not infer installation merely from a description being displayed. Depending on the DNF version and metadata, the information includes a version, architecture, repository, summary, and description.

If cached metadata is missing, these commands may report that they cannot proceed or provide incomplete results. Cache-only mode is useful for avoiding a network refresh; it cannot invent missing information. It also is not a blanket promise that DNF writes no logs or other bookkeeping. Without `--cacheonly`, even an information command can refresh expired metadata, depending on the command, version, and configuration.

When the question is “which repository package contains this path?” rather than “which installed package owns it?”, DNF has `provides`:

```bash
dnf --cacheonly provides /usr/bin/tree
```

This can find a provider in the cached repository information even when the program is not installed. The corresponding Debian installed-file query cannot do that: `dpkg-query -S` only searches local package records. Debian's separate `apt-file` tool can search repository file lists, but it needs suitable file-list metadata and may not be installed. Do not install extra tools just to make a read-only investigation appear complete.

### Calculate a change, then decline it

DNF does not use APT's `--simulate` option. A common way to inspect its proposed transaction is `--assumeno`, which answers no to confirmation questions. Combining it with `--cacheonly` also avoids refreshing repository metadata:

```bash
dnf --cacheonly --assumeno install tree
```

If the cached information is sufficient, DNF calculates what it would install and then declines the transaction. Read the package and dependency list, repositories, sizes, and summary. This is not an APT-style guarantee that no other bookkeeping is written; plugins and local configuration can affect behavior. Some systems may require additional permission even to reach a transaction proposal. Do not work around that by dropping `--assumeno`.

For an actual authorized installation, the command is:

```bash
sudo dnf install tree
```

**This is a real installation, not a preview.** Without cache-only mode, DNF may refresh metadata as needed before calculating the transaction. Review the proposal before confirming. To verify installation afterward, use `rpm -q tree`, applying the same installed-record query explained above.

The corresponding removal preview is:

```bash
dnf --cacheonly --assumeno remove tree
```

An approved real removal is:

```bash
sudo dnf remove tree
```

DNF can include packages that depend on the removed package and, under its normal settings, dependencies it considers no longer needed. Do not assume its removal list will match APT's. RPM configuration handling also differs from Debian's `remove` and `purge` distinction: modified configuration may be preserved, sometimes with an `.rpmsave` suffix. Review the package's behavior and preserve data you need; there is no general DNF `purge` command equivalent to assume here.

### Refresh and upgrade are separate here too

On an authorized DNF system, the following asks DNF to refresh repository metadata and build its cache:

```bash
sudo dnf --refresh makecache
```

`--refresh` requests fresh metadata; `makecache` prepares the local cache. This contacts repositories and writes metadata but does not install package upgrades. It was not executed for this chapter.

To install available package upgrades instead:

```bash
sudo dnf upgrade
```

This is a real system-changing operation, also not executed here. In DNF, `update` is commonly an alias for `upgrade`. That is an important difference from `apt update`, which refreshes information only. Translate the intended action between distributions, not the English word in the command.

DNF repository files normally live under `/etc/yum.repos.d/`, with general settings under `/etc/dnf/dnf.conf`. A “no match” error can mean a wrong name, disabled repository, missing cache, unsupported release, or a package unavailable for this system. Investigate those possibilities before adding a third-party source or disabling trust checks.

## When the package manager does not tell the whole story

Distribution packages are only one way software arrives. A command copied into `/usr/local/bin`, a program installed in your home directory, a Python environment, a Flatpak application, or software inside a container may not appear in the operating system's installed-package database. Different installation methods have their own update and removal procedures.

That explains two common mismatches: “the command works, but no package is recorded” and “the package is recorded, but the service is not working.” Neither is fixed merely by repeating an installation command. First identify what is actually running and which installation method owns it.

For any installation, you should be able to explain where the software comes from, what additional packages it needs, what will change, and how it will receive updates and eventually be removed. Avoid running an unaudited downloaded script directly in a privileged shell. That gives code from the download the account's authority without the package review described here.

The useful habit is to keep four questions separate: what is installed, what the configured sources offer, what a proposed transaction would change, and what actually happened after approval. Package managers provide different answers to each. Knowing which question you are asking makes their output much easier to read.

## Further reading

- [Debian: apt documentation](https://manpages.debian.org/apt/apt.8.en.html)
- [Debian: apt-get, including simulation options](https://manpages.debian.org/apt-get)
- [Debian: dpkg-query](https://manpages.debian.org/dpkg-query)
- [Fedora: DNF documentation](https://docs.fedoraproject.org/en-US/quick-docs/dnf/)
- [DNF 4 command reference](https://dnf.readthedocs.io/en/latest/command_ref.html)
- [DNF 5 command reference](https://dnf5.readthedocs.io/en/latest/dnf5.8.html)
- [RPM: package queries and file selection](https://rpm.org/docs/6.0.x/man/rpm.8)
- [openSUSE: Zypper reference](https://en.opensuse.org/SDB:Zypper_manual)
