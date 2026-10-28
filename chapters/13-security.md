# 13. Security basics

[Contents](../README.md) | [Previous: troubleshooting](12-troubleshooting.md) | [Next: shell scripts](14-shell-scripts.md)

Suppose a program needs a small configuration file containing a server address and a password-like value. You want the program to read that file, but you do not want every account on the machine, every application you run, or everyone reading a support ticket to receive the password too.

That problem is small enough to reason about. Who needs access? What do they need to do? Where else might the contents go? Security becomes more manageable when you ask these questions about a particular file or service rather than looking for one command that makes the whole machine “secure.”

This chapter builds a configuration file containing an obviously fake secret. It then uses the same example to explain application access, software trust, network exposure, and recovery. Nothing here requires changing accounts, installing packages, opening ports, or switching off a protection.

## In this chapter

- [Give each task only the access it needs](#give-each-task-only-the-access-it-needs)
- [Create a private configuration file](#create-a-private-configuration-file)
- [Work out whether an application can read it](#work-out-whether-an-application-can-read-it)
- [Share useful evidence without sharing the secret](#share-useful-evidence-without-sharing-the-secret)
- [Choose software sources and keep updates working](#choose-software-sources-and-keep-updates-working)
- [Understand what a listening service exposes](#understand-what-a-listening-service-exposes)
- [Know what each protection does not cover](#know-what-each-protection-does-not-cover)
- [Prepare for mistakes and recovery](#prepare-for-mistakes-and-recovery)
- [Remove the example files](#remove-the-example-files)
- [Further reading](#further-reading)

## Give each task only the access it needs

A text editor needs to read and change the documents you open. It normally does not need to change the operating system's login rules. A program that sends a report may need to read its configuration and write a report, but not read another person's home directory.

Giving a task just enough access to do its job is called **least privilege**. This limits the consequences of both mistakes and malicious behavior. If a program cannot write a system file, a bug in that program cannot normally overwrite that file.

On Linux, a running program has an account identity. By default, a program you start from your terminal runs as your account. It does not become a different person just because its name is different. That matters: ordinary file permissions generally separate accounts, not all the applications running under one account.

Use an ordinary account for ordinary work. `sudo` can run an authorized command with another identity, commonly the administrator account called root. It is not a general repair for “Permission denied.” It can hide the real problem, produce files your ordinary account cannot later change, or let a typo damage more of the system. Before using it, understand the whole command, the files it will affect, and why the task requires extra access.

The read-only command `id` shows your account and group memberships. A group is a way to grant access to several accounts together. Its output contains machine-specific names and numbers; it does not show the identity of every service on the machine. See [users, groups and permissions](05-permissions.md) for the fuller model.

## Create a private configuration file

Use a writable practice directory, not a directory belonging to an installed application. The following commands create only a new directory named `security-example` and a dummy file inside it. If that directory already exists, choose a different name throughout rather than reusing unknown files.

First create the directory:

```bash
mkdir -m 700 security-example
```

`mkdir` creates a directory. The `-m` option sets its permission mode at creation. Here `700` gives its owner read, write, and search access, with no ordinary permission for the owning group or other accounts. Directory search access means being allowed to pass through the directory to reach a named file. This is different from executing a program.

A successful `mkdir` normally prints nothing. If it says `File exists`, stop and choose a fresh name; the error is not an invitation to delete the existing directory.

Now create the file:

```bash
(umask 077; printf '%s\n' 'endpoint=https://example.invalid' 'token=DEMO-NOT-A-REAL-SECRET' > security-example/client.conf)
```

This line is longer because it protects the file **while it is being created**, rather than leaving a readable file around and fixing it afterward. Read it in pieces:

- Parentheses run the enclosed commands in a separate shell environment. Changes made there do not change your terminal's later settings.
- `umask 077` removes group and other permissions from the permissions requested for newly created files. It does not change existing files.
- The semicolon separates the two commands, so `printf` follows `umask`.
- `printf` writes text. The format `'%s\n'` prints each following string with a newline after it. Single quotes keep the shell from interpreting the contents.
- `>` sends that text into the named file instead of displaying it. It would overwrite an existing file, which is why we started with a fresh directory.

The token is deliberately fake. Never replace it with a real token in a command you paste into your terminal: the command itself may be saved in shell history or captured by terminal recording. A real application's documented secret-entry method, or an approved secret manager, is a better starting point. A secret manager is a system that stores sensitive values and controls their retrieval; it still needs appropriate access rules.

Check the resulting permissions without displaying the contents:

```bash
stat -c '%a %n' security-example security-example/client.conf
```

On GNU `stat`, `-c` chooses a display format. `%a` prints the numeric permission mode and `%n` prints the name. The observed output from the local example was:

```text
700 security-example
600 security-example/client.conf
```

In `600`, the owner has read and write permission, and the group and others have none. The file is not executable because ordinary text-file creation does not request execute permission in the first place. A mask removes permissions; it does not grant missing ones.

These are the expected ordinary Linux results. Filesystems that map permissions differently, and directories with inherited access rules, can require additional inspection. The mode is useful evidence, not a complete description of every access decision.

If a configuration file you own already exists with overly broad permissions, this command sets its ordinary mode explicitly:

```bash
chmod 600 security-example/client.conf
```

`chmod` changes the permission mode of the named file. It normally prints nothing on success. Repeating the preceding `stat` command checks the result. Here it remains `600` because the file was already created that way. This command does not change ownership, erase copies, encrypt the contents, or make a different service account able to read it.

## Work out whether an application can read it

Before changing permissions in response to an error, separate two questions: “Did the program find the file?” and “Was the program allowed to open it?”

For example, this command contains a small filename mistake:

```bash
cat security-example/clients.conf
```

`cat` reads a file and writes its contents to the terminal. The actual error in the local example, using English diagnostic messages, was:

```text
cat: security-example/clients.conf: No such file or directory
```

The name has an extra `s`. Adding administrative access or granting everyone permission does not correct a spelling mistake. Correct the path instead:

```bash
cat security-example/client.conf
```

For this dummy file only, the observed output was:

```text
endpoint=https://example.invalid
token=DEMO-NOT-A-REAL-SECRET
```

The `.invalid` address is intentionally not a real service address. Reading the file does not contact it. Do not repeat this contents check with a real secret merely to prove that permissions work; displaying the secret creates another place it can be captured.

The successful read establishes something narrow: this `cat` process, started in this terminal, could read this file at that moment. It does not establish that an installed application can read it. Consider three cases.

### The application runs as your account

A program you start normally can generally read files that your account can read, including this `600` file. This is useful for a trusted command-line client that needs its token. It also means `600` does not protect the token from an untrusted program running as you. A private directory is not an application sandbox.

### The application runs as a dedicated service account

A background application may run under a separate account rather than yours. With this example's ownership and modes, that ordinary account has no permission to pass through the private directory or read the file. The restriction is working as designed, even if the application reports an error.

For an actual deployment, first read the application's documentation and service configuration to identify its running account and expected configuration location. Then decide how that account should receive the secret. The documented design might use a service-owned file, a narrowly scoped group, or a service manager's credential mechanism. Do not copy a secret into a public directory or grant everybody access just to make the error disappear. A group-readable file inside an inaccessible parent directory still cannot be reached, so review the full path, not just its final component.

No separate service account is created or tested in this example. The correct ownership changes for a real service depend on that service's design and the machine owner's policy.

### Another rule still denies access

Ordinary ownership and mode bits are only part of the decision. An **access control list**, or ACL, can name additional accounts or groups with access. SELinux and AppArmor can impose additional rules on what particular programs may do. These rules can refuse access even when the ordinary file mode looks suitable. SELinux commonly makes decisions using security labels; AppArmor commonly uses application profiles with rules about paths and operations.

A service can also have a restricted view of the filesystem, so a file visible in your terminal may not exist inside the service's environment. A filesystem mounted read-only can prevent writes regardless of a file's write bits.

If a correctly configured application still cannot read its file, gather its exact error, the configured path, the running identity, and relevant denial messages from its logs. Log access itself may require authorization. Follow distribution and application documentation to correct the specific problem. Disabling SELinux, AppArmor, or service isolation to see whether “it works” removes protection from more than the file you are investigating and is not a fix.

## Share useful evidence without sharing the secret

Suppose someone helping you needs to know the endpoint, but not the token. Rather than paste the whole configuration, select the one relevant line:

```bash
grep '^endpoint=' security-example/client.conf
```

`grep` prints lines matching a pattern. The `^` at the start of this quoted pattern means “start of the line,” so it selects lines beginning with `endpoint=`. It is not a shell operator because it is inside quotes. The observed output was:

```text
endpoint=https://example.invalid
```

This is a selection method, not a general-purpose secret remover. In another configuration, even an endpoint could contain a password in its address or reveal an internal system name. Review the selected text before sharing it. Starting with a small, known-safe excerpt is usually easier to review than trying to remove every possible secret from a large dump.

The same principle applies to screenshots, logs, copied commands, and bug reports. A token is a value that may let its holder act as an authorized user or application. Private keys and some connection strings can have similar power. Do not put them in public repositories, chat messages, or support attachments. An environment variable is not automatically a safe hiding place either: programs can inherit it, and diagnostic tools or logs may expose it.

Keep secrets outside source files where the application supports that design. A version-control ignore rule helps avoid accidentally adding a new file, but it does not remove a file that is already tracked or erase older commits. Backups and exported archives need access protection too; they can contain the same secret as the original file.

## Choose software sources and keep updates working

Our file permissions cannot help much if we willingly run a malicious program as the account that owns the file. Choosing software is therefore an access decision, not just a download decision.

Start with your distribution's supported package manager and repositories. A repository is a source from which the package manager obtains software and update information. The distribution normally maintains a process for checking that packages came from its authorized source. That process reduces the risk of receiving a substituted package; it does not promise that every authorized package is free of bugs.

Adding another repository or its signing key means trusting another party to supply software. Verify installation instructions through the responsible vendor's official documentation and your organization's policy. A script that downloads more code and runs it with administrator access may change the whole machine before you have inspected what it does. Do not treat a popular copied command as proof of trustworthiness.

Updates fix known problems, including security defects. Use the update procedure for your distribution as explained in [software and packages](11-packages.md). There is no universal update command across Linux distributions. Refreshing the list of available packages is also not the same thing as installing their updates.

On a managed machine, confirm who is responsible for updates and when maintenance is allowed. Some changes need a service restart or reboot before the running software uses the fix. Automatic updates vary by distribution and configuration, so check what is actually enabled and whether updates are succeeding. A release that has reached the end of its supported life needs a supported upgrade path; repeatedly asking its package manager for updates does not create fixes that are no longer published.

No package installation or update is required for the file example.

## Understand what a listening service exposes

The example client has an endpoint it would contact. That does not necessarily mean it accepts incoming connections itself. A server, in contrast, waits for connections on a particular address and numbered port. This waiting is called **listening**. A listening socket is a possible entry point, not evidence that somebody has broken in.

For an authorized, read-only inspection on a Linux machine with `ss` installed, you can use:

```bash
ss -lnt
```

`ss` reports socket information. The combined options mean show listening sockets (`-l`), keep addresses and ports numeric (`-n`), and select TCP (`-t`). TCP is one common transport used by network applications. This command does not inspect UDP listeners, open a port, or test access from another machine.

As a schematic example, not observed host output, a local-address field might contain `127.0.0.1:8000`, `0.0.0.0:8000`, or `[::]:8000`. These mean different things:

- `127.0.0.1` is an IPv4 loopback address, normally reachable only within the same network environment. On a conventional host, that generally means from the same machine.
- `0.0.0.0` means all local IPv4 addresses, not “nobody can connect.”
- `[::]` represents the IPv6 unspecified address, used for listening on all local IPv6 addresses. Whether that listener also accepts IPv4 connections depends on the application and system configuration.

A firewall may block traffic to a listener. A router, cloud network rule, port-forwarding rule, or reverse proxy may change who can reach it. A reverse proxy accepts requests and forwards them to an application, so even a loopback-only application can be reachable through that proxy. Containers introduce their own network environments and port mappings.

To judge exposure, identify the owning application, why it needs to listen, which users should reach it, and what controls exist along the connection path. The basic `ss` command above does not identify the owning process; an administrator may need additional process information and service configuration to make that connection. See [networking](09-networking.md) and [services and logs](10-services.md).

Do not stop an unfamiliar service or change a firewall merely because a port appears in a list. It could carry your remote login or an essential application. An authorized change needs a known recovery route if access is lost. Even a correctly configured firewall does not replace application updates, user authentication, or permission checks within the application. Authentication establishes who a user is; authorization decides what that user may do.

## Know what each protection does not cover

Several modest protections can cover different failure paths. The file mode limits ordinary account access. A dedicated service account limits what a compromised application can normally reach. SELinux or AppArmor may restrict it further. Network rules limit some connections. Updates repair known software defects.

None covers everything. A process with suitable administrative powers may bypass ordinary file permission checks. Software running as the file owner can normally read the file. Disk encryption can help protect a powered-off disk if its unlocking material is kept separately; it does not hide an unlocked file from an application already allowed to read it. Backups help restore lost data, but do not prevent an attacker from copying it.

Linux can divide some administrative powers into smaller units called **capabilities**, allowing certain tasks without every power of root. This is an advanced application-specific design choice, not a reason to grant capabilities to arbitrary programs after an error. Follow the service's documented deployment model.

A kernel-version display, package list, permission listing, or single port check is a limited observation. None certifies that a machine is secure. First decide what needs protection and from whom: another local account, an untrusted application, an internet client, or a stolen disk pose different problems. Administrators call this reasoning a **threat model**. You do not need an elaborate document to begin; clear answers about your configuration file are already useful.

## Prepare for mistakes and recovery

If a real token is pasted into a public issue, changing the local file to `600` does not undo the disclosure. Someone may already have copied it, and copies may remain in history, caches, logs, or backups.

Use the issuing service's procedure to revoke or rotate the token. Revoking makes the old value unusable; rotating replaces it with a new one. Update the legitimate application's approved secret location and confirm that it still works. Check for unexpected activity using the service's audit information, if available, and notify the responsible owner. Remove exposed copies where possible, but do not assume deletion alone restores secrecy. Whether to revoke first or arrange a brief replacement overlap depends on the incident and the service's supported process.

Keep a protected, recoverable copy of important configuration and data. Know how to restore it, and test restoration in a separate safe location before relying on it. A backup that nobody can unlock or that contains the same broken configuration may not help when needed. Restoring an old configuration can also reintroduce an exposed token, so recovery must include current credentials and updates, not just older files.

If you suspect a whole machine is compromised, follow the system owner's incident process. Do not improvise cleanup by deleting logs or randomly changing services: you may destroy evidence without removing the intruder's access. Depending on the incident, recovery may require rebuilding from trusted installation media and restoring checked data. That is a different task from correcting a mistyped filename.

## Remove the example files

Only if you created the dummy file and no longer need it, remove that exact file:

```bash
rm security-example/client.conf
```

`rm` removes the named file. It is not secure erasure of storage, backups, or previously shared copies. Then remove the now-empty directory:

```bash
rmdir security-example
```

`rmdir` removes an empty directory and refuses a nonempty one. If it refuses, inspect what remains instead of using a recursive deletion command. Both cleanup commands completed without output in the local example.

The useful outcome is not simply a file with mode `600`. It is being able to explain who should read it, how the application receives that access, what software you trust with it, and what to do if a copy escapes.

## Further reading

- [GNU Coreutils: Setting Permissions](https://www.gnu.org/software/coreutils/manual/html_node/Setting-Permissions.html)
- [Bash manual: Bourne Shell Builtins, including umask](https://www.gnu.org/software/bash/manual/html_node/Bourne-Shell-Builtins.html)
- [Linux man-pages: capabilities(7)](https://man7.org/linux/man-pages/man7/capabilities.7.html)
- [SELinux project documentation](https://selinuxproject.org/page/Main_Page)
- [AppArmor documentation](https://apparmor.net/)
- [Ubuntu Server: AppArmor](https://documentation.ubuntu.com/server/how-to/security/apparmor/)
- [NIST: Guide to General Server Security](https://csrc.nist.gov/pubs/sp/800/123/final)
