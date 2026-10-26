# Linux course roadmap

This is the course plan for the existing `linux-helpbook` repository, not an organization-wide roadmap. The hub and other topic repositories are outside this change. Estimates below are suggested study time in hours, not measured completion times.

**Status:** the first two lessons have sandbox evidence and are under editorial review; the rest of the course is planned. Existing Helpbook pages remain available as source material, not as verified replacements for these lessons. A code-formatted planned path is intentionally not a link to a missing file.

## Start here

- [Practice environment](00-start-here/00-setup.md): scope, tested baseline and environment limits.
- [How to use the course](00-start-here/01-how-to-use-this-repo.md): prerequisites, commands, output and verification labels.
- [Glossary](glossary.md): one definition per term.

## Fundamentals

Each lesson has one concept and stays under 1,500 words. Follow the listed prerequisites rather than reading a broad command catalogue first.

| ID | Full relative path | Single concept | Hours | Prerequisites | Status |
|---|---|---|---:|---|---|
| linux-01-01 | `01-fundamentals/01-running-kernel.md` | Identify the running kernel | 0.33 | None | Under review |
| linux-01-02 | `01-fundamentals/02-distribution.md` | Identify the installed distribution | 0.33 | linux-01-01 | Under review |
| linux-01-03 | `01-fundamentals/03-command-structure.md` | Read a shell command | 0.5 | linux-01-02 | Planned |
| linux-01-04 | `01-fundamentals/04-command-help.md` | Find help for a command | 0.33 | linux-01-03 | Planned |
| linux-01-05 | `01-fundamentals/05-paths.md` | Resolve a file path | 0.5 | linux-01-03 | Planned |
| linux-01-06 | `01-fundamentals/06-file-operations.md` | Safely create, copy and remove practice files | 0.5 | linux-01-05 | Planned |
| linux-01-07 | `01-fundamentals/07-text-files.md` | Read text files | 0.5 | linux-01-06 | Planned |
| linux-01-08 | `01-fundamentals/08-streams.md` | Connect command input and output | 0.5 | linux-01-07 | Planned |
| linux-01-09 | `01-fundamentals/09-user-identity.md` | Inspect account and group membership | 0.5 | linux-01-04 | Planned |
| linux-01-10 | `01-fundamentals/10-permissions.md` | Interpret file access permissions | 0.75 | linux-01-06, linux-01-09 | Planned |
| linux-01-11 | `01-fundamentals/11-processes.md` | Inspect a running process | 0.5 | linux-01-03, linux-01-09 | Planned |
| linux-01-12 | `01-fundamentals/12-signals.md` | Request a process to stop safely | 0.5 | linux-01-11 | Planned |
| linux-01-13 | `01-fundamentals/13-cpu-use.md` | Interpret CPU use | 0.5 | linux-01-11 | Planned |
| linux-01-14 | `01-fundamentals/14-memory-use.md` | Interpret memory availability | 0.5 | linux-01-11 | Planned |
| linux-01-15 | `01-fundamentals/15-filesystems.md` | Understand mounted filesystems | 0.75 | linux-01-05 | Planned |
| linux-01-16 | `01-fundamentals/16-packages.md` | Manage a software package | 0.75 | linux-01-02, linux-01-10 | Planned |
| linux-01-17 | `01-fundamentals/17-network-addresses.md` | Identify a network interface's addresses | 0.5 | linux-01-04 | Planned |
| linux-01-18 | `01-fundamentals/18-routing.md` | Read a route to a destination | 0.5 | linux-01-17 | Planned |
| linux-01-19 | `01-fundamentals/19-dns.md` | Resolve a name | 0.5 | linux-01-18 | Planned |
| linux-01-20 | `01-fundamentals/20-sockets.md` | Inspect a listening socket | 0.5 | linux-01-11, linux-01-17 | Planned |
| linux-01-21 | `01-fundamentals/21-boot.md` | Understand the boot sequence | 0.5 | linux-01-01, linux-01-15 | Planned |
| linux-01-22 | `01-fundamentals/22-services.md` | Inspect a systemd service | 0.75 | linux-01-11, linux-01-21 | Planned |
| linux-01-23 | `01-fundamentals/23-journal.md` | Read service logs in the journal | 0.5 | linux-01-22 | Planned |

## Intermediate

These are bounded administration and investigation tasks. Each page must still teach one central concept, not combine several lessons under a longer title.

| ID | Full relative path | Single concept | Hours | Prerequisites | Status |
|---|---|---|---:|---|---|
| linux-02-01 | `02-intermediate/01-script-exit-status.md` | Handle a script's failures | 1 | linux-01-03, linux-01-08 | Planned |
| linux-02-02 | `02-intermediate/02-text-search.md` | Find matching text reliably | 0.75 | linux-01-07, linux-01-08 | Planned |
| linux-02-03 | `02-intermediate/03-disk-space.md` | Explain filesystem space use | 1 | linux-01-15 | Planned |
| linux-02-04 | `02-intermediate/04-inodes.md` | Diagnose inode exhaustion | 0.75 | linux-02-03 | Planned |
| linux-02-05 | `02-intermediate/05-service-failure.md` | Diagnose a failed service start | 1 | linux-01-22, linux-01-23 | Planned |
| linux-02-06 | `02-intermediate/06-connection-failure.md` | Locate a failed connection stage | 1 | linux-01-18, linux-01-19, linux-01-20 | Planned |
| linux-02-07 | `02-intermediate/07-process-cpu.md` | Attribute CPU use to a process | 1 | linux-01-11, linux-01-13 | Planned |
| linux-02-08 | `02-intermediate/08-process-memory.md` | Interpret a process's memory use | 1 | linux-01-11, linux-01-14 | Planned |
| linux-02-09 | `02-intermediate/09-privilege.md` | Limit administrative privilege | 1 | linux-01-09, linux-01-10 | Planned |
| linux-02-10 | `02-intermediate/10-troubleshooting-hypotheses.md` | Test a troubleshooting hypothesis | 1 | linux-02-03, linux-02-05, linux-02-06 | Planned |

## Advanced

Advanced pages explain internals, tradeoffs and failure evidence. Never use a shared sandbox for host-level experiments it cannot support.

| ID | Full relative path | Single concept | Hours | Prerequisites | Status |
|---|---|---|---:|---|---|
| linux-03-01 | `03-advanced/01-namespaces.md` | Understand a process's isolated resource view | 1.5 | linux-01-11, linux-01-15, linux-01-17 | Planned |
| linux-03-02 | `03-advanced/02-cgroups.md` | Understand resource limits for process groups | 1.5 | linux-01-13, linux-01-14, linux-03-01 | Planned |
| linux-03-03 | `03-advanced/03-system-calls.md` | Trace a process's system calls | 1.5 | linux-01-11, linux-02-10 | Planned |
| linux-03-04 | `03-advanced/04-io-latency.md` | Investigate storage wait time | 1.5 | linux-02-03, linux-02-10 | Planned |
| linux-03-05 | `03-advanced/05-packet-capture.md` | Use packet evidence for one connection | 1.5 | linux-02-06, linux-02-09 | Planned |
| linux-03-06 | `03-advanced/06-boot-recovery.md` | Recover from one reproducible boot failure | 1.5 | linux-01-21, linux-02-05 | Planned |

## Labs and cheatsheets

Guided steps live in each lesson. Separate combined labs will be added only after their prerequisite lessons have been reviewed. `labs/verification/` holds execution evidence, not more lessons. No cloud lab is included in this first increment.

Planned lookup pages under `cheatsheets/` will cover commands, file access, processes, services and networking. Each must be a one-page command / purpose / example table, and must not silently introduce unverified commands.

## Existing material and migration

Keep the existing [fundamentals](fundamentals/README.md), [commands](commands/commands.md), [shell scripting](shell-scripting/scripting.md), [troubleshooting](troubleshooting/) and [Vim](vim/vim.md) material while the new path is built. Read the relevant original before replacing it. Preserve accurate explanations and attribution; remove duplicates only when replacements pass review.

## Verification and maintenance

Per-lesson execution dates, versions and evidence belong in [CHANGELOG.md](CHANGELOG.md). Review command behavior every three to six months and after tool changes. This policy does not create an automated job. systemd, privileged operations, networking mutations and boot recovery require an environment designed for those tasks; the initial read-only sandbox checks do not verify them.
