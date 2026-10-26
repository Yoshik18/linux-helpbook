# Linux, from the command line

A practical manual for understanding Linux and investigating it safely. Start with the shell, paths and text, then work through access control, processes, system resources, storage, networking and services.

## Chapters

1. [How a Linux system fits together](chapters/01-system.md)
2. [The shell and commands](chapters/02-shell.md)
3. [Files, directories and paths](chapters/03-files-and-paths.md)
4. [Reading and searching text](chapters/04-text.md)
5. [Users, groups and permissions](chapters/05-permissions.md)
6. [Processes and signals](chapters/06-processes.md)
7. [CPU, memory and load](chapters/07-resources.md)
8. [Disks and filesystems](chapters/08-storage.md)
9. [Networking from the command line](chapters/09-networking.md)
10. [Boot, services and logs](chapters/10-services.md)
11. [Software and packages](chapters/11-packages.md)
12. [Troubleshooting without guessing](chapters/12-troubleshooting.md)
13. [Security basics](chapters/13-security.md)
14. [Small shell scripts](chapters/14-shell-scripts.md)
15. [Connect to another machine with SSH](chapters/15-ssh.md)
16. [Archives and compression](chapters/16-archives.md)

The chapters are written as a start-to-finish path, but each can also be read on its own. Concepts build from earlier material, especially shell quoting, paths and process identity.

## Before you start

Use a Linux machine or Linux virtual machine with an ordinary user account and a terminal. A disposable VM is a useful choice if you intend to try administrative changes. Windows Subsystem for Linux also works for many command-line examples, but networking and service management can differ from a conventional Linux host. Installation and VM setup are outside this manual's scope.

Shell examples use Bash and common GNU utilities unless stated otherwise. Minimal containers may omit `man`, `less`, `file`, SSH, procps or networking utilities. A missing command does not mean Linux is broken: identify the distribution, then use its supported package manager if installation is authorized. You do not need root access for most inspection examples.

Read chapters 1–5 first if you are new to the command line, then continue in order. Later chapters refer back to quoting, streams, permissions and process identity rather than reteaching them. No separate labs or helper scripts are required.

## How to use the examples

Commands are shown as text for a terminal. A leading `$` in other documentation is usually a prompt, not part of the command. Read each explanation before running a command. Some examples only inspect information; others create files, contact remote services, change permissions or affect running processes. Those effects are called out in the chapter.

Displayed output is illustrative unless identified otherwise. Your distribution and machine will report different names, versions, addresses, counts and service states. Check the help and manual pages installed on your system when options or output differ.

## Scope

This manual covers common Linux command-line concepts and basic administration. It is not a distribution installation guide, a security certification, or authorization to change a production system. For consequential changes, follow the system owner's approved procedures.

The explanations and examples in this edition were written and edited for this manual. Technical references link to the upstream project or standard that documents each tool or behavior. The repository's existing licensing status is unchanged; no new license is granted here.
