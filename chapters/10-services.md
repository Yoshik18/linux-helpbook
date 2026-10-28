# 10. Boot, services and logs

[Contents](../README.md) | [Previous: networking](09-networking.md) | [Next: packages](11-packages.md)

A machine has just rebooted. You can use its keyboard and screen, but another computer can no longer connect to it with SSH. SSH, short for Secure Shell, provides an encrypted connection for remote login. The machine accepting the connection runs an SSH server. Did that server fail to start? Is it running but refusing connections? Was it never configured to start during boot?

Those questions need different evidence. Rebooting again or repeatedly restarting SSH may hide the useful clues without fixing the problem. This chapter follows a read-only investigation: identify who manages services, find the right service name, compare its present state with its startup configuration, and read the messages around the failure.

SSH is the worked example because it makes the consequences clear: stopping the program that provides remote access can lock you out. You do not need to install or start an SSH server to read this chapter. If your machine has no SSH service, that is a valid stopping point, not an instruction to add one.

## In this chapter

- [What happens between power-on and a login prompt](#what-happens-between-power-on-and-a-login-prompt)
- [A process is not the same thing as a service](#a-process-is-not-the-same-thing-as-a-service)
- [Find the manager before asking it questions](#find-the-manager-before-asking-it-questions)
- [Find the right systemd unit](#find-the-right-systemd-unit)
- [Read status as several separate facts](#read-status-as-several-separate-facts)
- [Running now and enabled for startup are different](#running-now-and-enabled-for-startup-are-different)
- [Follow the failure into the journal](#follow-the-failure-into-the-journal)
- [Read the service definition without changing it](#read-the-service-definition-without-changing-it)
- [Why restarting is a decision, not a diagnostic test](#why-restarting-is-a-decision-not-a-diagnostic-test)
- [When there is no systemd manager](#when-there-is-no-systemd-manager)
- [Further reading](#further-reading)

## What happens between power-on and a login prompt

The programs you use cannot start until something has prepared memory, found the operating system, and made its files available. On a typical Linux computer, that happens in several stages.

1. **The machine's built-in startup software runs.** This is the **firmware**, often UEFI on modern computers. It performs initial hardware setup and chooses what to boot.
2. **A small startup program loads Linux.** This is the **bootloader**, such as GRUB or systemd-boot. It loads the Linux kernel into memory and usually supplies an early startup environment too. Some firmware can load the kernel directly, so a separate bootloader is not universal.
3. **The kernel takes control.** The kernel is the part of Linux that manages hardware, memory, and processes. It initializes enough of the machine to run programs.
4. **Early startup code finds the main system files.** Many distributions use a temporary set of files in memory, called an **initramfs**. It can load storage drivers, unlock encrypted storage, and make the main root filesystem available. The root filesystem is the filesystem containing `/`, the top of the system's directory tree. Not every installation needs a separate initramfs.
5. **The system's first main management process brings up the rest.** It arranges necessary filesystems, background services, login terminals, and possibly a graphical login screen.

The last step is why a boot can reach a login prompt even though one particular service failed. A working terminal does not mean that every background task succeeded.

On many distributions, the program coordinating that last stage is **systemd**. It starts work according to relationships between tasks rather than following one simple list from top to bottom. Independent tasks can start at the same time. A task that needs a filesystem must wait for that filesystem, but it need not wait for an unrelated printer service.

Systemd also groups tasks into named milestones called **targets**. For example, `multi-user.target` commonly represents a working non-graphical system, while `graphical.target` adds a graphical login environment. Reaching a target is not a guarantee that every application is healthy. It describes a stage in the startup arrangement, not an end-to-end test of your machine.

If the bootloader cannot load the kernel, service commands cannot help yet: there is no running system manager to ask. If Linux starts and a particular application fails, the later parts of this chapter become useful. First locate the stage of the problem instead of treating all startup failures as the same thing.

## A process is not the same thing as a service

A program that is currently executing is a **process**. It has a process ID, usually shortened to **PID**. Your shell, a text editor, and the SSH server all run as processes.

A **service** is a task the system manages on your behalf. It might keep accepting SSH connections, maintain the system clock, or perform a short cleanup and exit. A long-running background program is often called a **daemon**. Not every process is a daemon, and not every service keeps a process running all the time.

The service manager remembers more than a process list can tell you:

- which command should start the task;
- which account should run it;
- what it needs before it can start;
- whether it should be started automatically;
- whether its previous attempt failed;
- whether an automatic restart is configured.

A service can create several processes. Its main process can disappear and be replaced with a different PID after a restart, while the service keeps the same name. Conversely, a short setup service can finish successfully and have no process left at all.

This distinction matters in our SSH investigation. Seeing an SSH-related process is a clue, but it does not by itself establish which service owns it or whether a new connection will work. Seeing no permanent process is not automatically an error for every kind of service.

## Find the manager before asking it questions

The first process in the system's main process view has PID 1. It is often called the **init process**. Besides coordinating startup, it has special responsibilities for collecting the completion status of certain processes left without a parent. A program is not a complete init system merely because it happens to have PID 1.

Inspect that process with:

```bash
ps -p 1 -o pid=,comm=,args=
```

`ps` displays information about processes. With the procps-ng version common on Linux:

- `-p 1` selects only PID 1.
- `-o` chooses the output fields.
- `pid` is the process ID, `comm` is the command name, and `args` is the command with its arguments.
- The commas separate fields within one option argument. The `=` after each field suppresses its column heading; it does not assign a shell variable.

A **schematic systemd result**, not output captured for this chapter, is:

```text
1 systemd /sbin/init
```

The important clue is `systemd`, not the exact path. Distributions can arrange the startup program differently.

There is an extra boundary in containers. A container can have its own numbered view of processes, called a **PID namespace**. PID 1 inside it may be a small supervisor, a shell, or the application itself. It is not necessarily PID 1 on the host computer. Containers normally share the host kernel; starting a container is not the same as booting a whole machine through firmware and a bootloader.

Even a process named `systemd` does not prove that your current session can communicate with its service-management interface. The next commands require both the `systemctl` program and an accessible systemd system manager.

**Execution boundary for this chapter:** the writing environment had `s6-svscan` as PID 1 and did not have `systemctl` or `journalctl`. The process inspection ran successfully. Read-only attempts to use those two missing commands returned a command-not-found error. The systemd investigation below is therefore a conditional walkthrough, not an executed service diagnosis. Its displayed service and journal output is schematic. No live service was started, stopped, enabled, reloaded, or restarted.

If your machine also lacks systemd, go to [When there is no systemd manager](#when-there-is-no-systemd-manager). Do not install systemd just to make this example match.

## Find the right systemd unit

Suppose you are on a systemd machine where the management interface is available. Systemd describes each managed item as a **unit**. A unit has a name and a type. The name `ssh.service` means a service unit named `ssh`.

Services are not the only unit type. A name ending in `.socket` describes a communication endpoint that can trigger another unit when a connection arrives. A `.timer` unit schedules work. A `.mount` unit describes a mounted filesystem, and a `.target` unit groups other units. The suffix tells you what kind of thing you are examining.

First find the local service name rather than assuming every distribution uses the same spelling:

```bash
systemctl list-unit-files --type=service --no-pager
```

`systemctl` asks the systemd manager questions or requests changes. Here it is only reading information:

- `list-unit-files` lists known unit files and their enablement states. A unit file contains the instructions for a managed task.
- `--type=service` limits this listing to service units. Here the equals sign attaches `service` to the option; it is not a shell assignment.
- `--no-pager` prints directly to the terminal instead of opening a separate scrolling viewer, called a pager.

A **schematic excerpt**, with unrelated rows omitted, could be:

```text
UNIT FILE       STATE     PRESET
ssh.service     enabled   enabled
```

`UNIT FILE` is the name you can use in later commands. `STATE` describes enablement, which we will separate from running state shortly. `PRESET`, when shown, is the distributor's or administrator's preset policy, not proof of what is running now.

On some distributions the name is `sshd.service` instead. If that is the name your listing shows, substitute `sshd.service` for `ssh.service` in every following command. Do not run both names and treat the missing one as a second failure. If neither exists, SSH may not be installed, may be managed another way, or may belong to a different environment.

Now inspect the exact name found:

```bash
systemctl status ssh.service --no-pager --full
```

`status` requests a human-readable report for the named unit. `--no-pager` again avoids the viewer. `--full` asks systemctl not to shorten long fields and lines with ellipses. Your terminal may still wrap a long line.

A plausible naming mistake produces a message such as this **schematic error**:

```text
Unit ssh.service could not be found.
```

That is not the same as “SSH crashed.” It says systemd could not find that unit name. If the earlier listing showed `sshd.service`, the correction is:

```bash
systemctl status sshd.service --no-pager --full
```

Only the target name changes. Keep investigating the unit your own system actually has. If you have no matching unit, stop this branch rather than guessing a start command.

## Read status as several separate facts

For our continuing example, assume the correct name is `ssh.service`. A **schematic status excerpt** for a running server is:

```text
ssh.service - OpenBSD Secure Shell server
     Loaded: loaded (/usr/lib/systemd/system/ssh.service; enabled; preset: enabled)
     Active: active (running)
   Main PID: 742 (sshd)
```

This is a shortened teaching example, not the exact full layout of any measured machine. Paths, descriptions, PIDs, timestamps, and available fields vary.

Read each line as a different claim:

**`Loaded: loaded` means systemd has read a usable unit definition.** The path points to the definition it loaded. The same line often includes `enabled`, but that is a separate startup-configuration fact, not a synonym for `loaded`.

**`Active: active (running)` means the manager considers the service active and currently running.** It does not prove that a firewall permits access, that an account can log in, or that the application is answering correctly. For SSH, a connection test from the affected client is still separate evidence. The networking chapter covers that side of the investigation.

**`Main PID: 742 (sshd)` identifies the main process systemd associates with this service at this moment.** The number is not permanent. A later status report may show another PID after an automatic or administrative restart. Other processes can belong to the same service too.

Status usually includes a small selection of recent messages. It is a convenient first view, not the full log history. Long-standing problems may have scrolled out of that selection.

Other states require different interpretations:

- **`inactive (dead)`** means the unit is not active now. That can be normal for a task that has completed or has not been requested.
- **`active (exited)`** can be normal for a one-time setup task whose successful result is meant to remain in effect. It does not mean a server process is still running.
- **`failed`** means systemd recorded a failure, such as an unsuccessful process exit, timeout, or too many rapid startup attempts. Read the accompanying result and logs before deciding what caused it.
- **`activating`** or **`deactivating`** means a transition is still in progress. A momentary observation is not enough to call it stuck.

For a compact current-state answer:

```bash
systemctl is-active ssh.service
```

`is-active` reports an activity state for the named unit. In our schematic running case it would print:

```text
active
```

It also returns a numeric exit status to the shell. Zero means the named unit is active; a nonzero status needs interpretation alongside the text and any error message. An inactive unit and a failed attempt to contact the manager are not the same diagnosis. Similarly, `systemctl status` can return nonzero simply because the unit is not running. A nonzero return does not always mean the inspection command itself malfunctioned.

## Running now and enabled for startup are different

The next question is not “is it running?” but “how is it arranged to start?” Ask separately:

```bash
systemctl is-enabled ssh.service
```

`is-enabled` reads the unit's enablement state. A **schematic answer** is:

```text
enabled
```

`enabled` generally means links have been configured so another unit, commonly a boot target, pulls this unit into its startup. It does not mean the most recent start succeeded.

The useful contrast is:

| State now | Startup configuration | What it can mean |
| --- | --- | --- |
| Active | Enabled | It is active now and has enablement links. |
| Inactive | Enabled | It is arranged to be requested, but it may have stopped, failed, or not been reached yet. |
| Active | Disabled | Something started it without enablement links, such as an administrator, a dependency, or another activation mechanism. |
| Inactive | Disabled | It is not active and has no enablement links of its own. That may be intentional. |

The table describes two independent questions, not four health ratings. In particular, `disabled` does not mean “broken” or “cannot start.”

You may see other answers. **`static`** usually means the unit has no instructions for ordinary enablement; another unit can still request it. **`masked`** means the unit has been blocked from starting. These are not reasons to change the configuration immediately. Find out why it was arranged that way.

On some installations, SSH is activated through a socket unit. The socket can wait for connections and start the service when needed, so a quiet service need not have a permanent running process. An inactive service therefore needs to be interpreted with its activation setup. Enabling the service itself is not automatically the right repair.

The names of the management operations help keep the distinction straight. The following are explanations of **unexecuted, state-changing operations**, not instructions to try on your current machine:

- `start` requests activation now. It does not by itself enable future startup.
- `stop` requests deactivation now. It does not by itself remove enablement links.
- `enable` sets up enablement links. By itself it does not start the service.
- `disable` removes enablement links. By itself it does not stop an already running service or prevent every other activation route.
- `restart` stops and starts the service; if it was inactive, it normally starts it.

The `--now` option changes the meaning of an enable or disable request by adding a start or stop operation immediately. Do not add it casually to an example you found elsewhere. It crosses from startup configuration into changing current behavior.

## Follow the failure into the journal

Return to the reboot problem. Suppose status shows `failed`, rather than the running state above. The next useful step is to read what happened during the failed start.

Many systemd machines collect messages in a structured store called the **journal**, maintained by `systemd-journald`. Applications can send messages there, and systemd commonly sends service output there too. Applications may instead write some messages to their own files, so the journal is not guaranteed to contain everything.

Read the current boot's recent messages for our unit:

```bash
journalctl -b -u ssh.service -n 50 --no-pager
```

`journalctl` reads stored journal entries; this command does not restart or alter the service.

- `-b` limits the selection to the current boot. This avoids mixing an old boot's failure with today's attempt.
- `-u ssh.service` selects entries associated with that unit, including relevant manager messages about it.
- `-n 50` limits the result to the latest fifty matching entries. It is a maximum, not a promise that fifty exist.
- `--no-pager` prints directly rather than opening a viewer.

The usual short format puts a timestamp first, followed by the machine name, the program and often its PID, then the message. This **schematic diagnostic excerpt** uses `example-host` as an invented machine label. The wording illustrates a possible configuration failure; it was not observed during this chapter's checks:

```text
Oct 28 09:12:03 example-host sshd[742]: /etc/ssh/sshd_config line 18: Bad configuration option: ExampleOption
Oct 28 09:12:03 example-host systemd[1]: ssh.service: Main process exited, code=exited, status=255/EXCEPTION
Oct 28 09:12:03 example-host systemd[1]: ssh.service: Failed with result 'exit-code'.
```

Read from the application message toward the manager's summary. The first line identifies a file, a line number, and a rejected setting. The next line says that the main process exited with a nonzero result. `status=255/EXCEPTION` is an exit-status description here; it does not establish that a programming-language exception occurred. The final line records the overall failure.

The last line alone does not tell you how to repair SSH. The earlier application message is a better lead. An authorized administrator would inspect that configuration entry and validate the proposed correction using the installed SSH server's documented validation method. This chapter does not edit the file or attempt a repair on a live server.

If instead the first useful message says a file is missing or access is denied, follow that evidence. Repeatedly starting the same program cannot make a missing file appear or establish the intended permissions. Avoid changing permissions broadly just to silence an error.

### When the narrow log view is not enough

A unit-only view is useful, but the cause can be outside the unit. To widen the view to the latest fifty accessible messages from this boot:

```bash
journalctl -b -n 50 --no-pager
```

This removes `-u ssh.service`; the other options keep their meanings. Look for events near the failure time, such as a filesystem becoming unavailable. The latest fifty entries may not reach far enough back on a busy machine. A missing clue in this small window is not proof that nothing happened.

If the symptom began before the reboot, first find out whether older boots are available:

```bash
journalctl --list-boots --no-pager
```

`--list-boots` lists the boots represented in the journal you are allowed to read, with identifiers and their first and last available message times. In that listing, boot offset `0` refers to the current boot, and `-1` to the previous available boot. Do not share the listing without checking it for identifying details.

If a previous boot is listed, this selects its latest fifty SSH-related entries:

```bash
journalctl -b -1 -u ssh.service -n 50 --no-pager
```

Here `-1` is the value supplied to `-b`, meaning the previous boot. It is not a command to move back through the shell's history. The unit and count options work as before.

Older entries may not exist. Some systems retain the journal only in memory, so rebooting discards it. Stored logs can also be removed as retention limits are reached. A request for a previous boot cannot recover messages that were never preserved.

An empty selection may show `-- No entries --`, or journalctl may report that no journal files were found. Check the unit name, boot, retention, and your access before concluding that the service never ran. An ordinary account may see only part of the system journal. If the required records are restricted, ask an authorized administrator for the relevant excerpt rather than assuming you should elevate privileges or join a powerful group.

Logs can contain account names, addresses, paths, and secrets accidentally printed by applications. Review and redact them before sharing. A log line is evidence that something was reported at a particular time, not a guarantee that its explanation is complete or even correct. Timestamps can also be confusing if the clock was corrected during startup.

### Is this the only failed service?

If the SSH failure appears to be part of a larger startup problem, ask for failed service units:

```bash
systemctl --failed --type=service --no-pager
```

With no explicit command, systemctl uses its unit-listing operation. `--failed` restricts the view to units in the failed state, and `--type=service` restricts it to services. `--no-pager` keeps the result in the terminal.

This is a different listing from `list-unit-files`: it reports units known to the running manager, not every installed unit file. Its `LOAD` column describes whether the definition was loaded, `ACTIVE` gives the broad state, and `SUB` gives the more specific state. For a failed service, the latter two can both say `failed`. `DESCRIPTION` is the unit's human-readable label.

An empty list means this query found no failed service units. It does not prove that all network paths, applications, or hardware work. Several failures close together may share one cause, so avoid treating each row as an unrelated repair job.

## Read the service definition without changing it

If the command that failed or the service's configuration is still unclear, inspect the instructions systemd has on disk:

```bash
systemctl cat ssh.service --no-pager
```

In this context, `cat` is a systemctl operation, not a shell command reading an arbitrary file. It displays the unit's backing files, including additional configuration fragments where available. These fragments are often called **drop-ins** because they add to or override parts of the main definition. Comments in the output identify the source paths. `--no-pager` has the same direct-output meaning as before.

Useful settings to recognize include:

- `ExecStart=`, which describes the command used to start the service;
- `User=`, which can select the account for its processes;
- `Restart=`, which describes automatic restart policy;
- `Wants=` or `Requires=`, which express relationships that request other units;
- `After=`, which expresses ordering relative to other units;
- `WantedBy=`, which can describe where enablement links should be created.

These are unit-file settings, not Bash commands to paste into a terminal. A full explanation of writing unit files is beyond this chapter, but two distinctions already help with diagnosis.

First, `After=` is about order. It does not, by itself, request that the other unit start. Dependencies and ordering are related but separate instructions.

Second, a policy such as `Restart=on-failure` can cause a new startup attempt after a failure. That helps explain changing PIDs or repeated log messages. Rapid failures can eventually hit systemd's start-rate limit, producing messages such as “Start request repeated too quickly.” That message can be a consequence of the original fault, not its cause. Look back for the first application error.

`systemctl cat` shows files on disk. If someone edited those files without asking the manager to reread them, the running manager may still be using an older definition. Do not assume the text displayed is proof that a change is already in effect. Also review unit contents before sharing them: service commands and settings can contain sensitive values.

## Why restarting is a decision, not a diagnostic test

By this point, our investigation should have a specific finding: the unit is absent, the service is active but the connection still fails, or a startup attempt failed with a useful message. These findings lead to different next steps. None automatically justifies a restart.

A restart can interrupt users, discard in-memory work, close connections, and trigger dependent services. The details depend on the unit definition and the application. For SSH, some arrangements leave existing sessions alone and some changes affect the ability to reconnect. Do not rely on your current session surviving as a recovery plan.

Before any authorized change to a remote access service, arrange another way back in, such as an approved console. Understand the intended configuration, who depends on the service, how to validate a change, and how to undo it. On a shared machine, use its owner's change procedure.

Two more operations are easy to confuse:

- A service **reload** asks the application to reread its own configuration, if the unit supports that operation. It is not universally available, and its effect depends on the application.
- A systemd **daemon-reload** asks the manager to reread unit definitions and rebuild its dependency information. It is not a request for SSH to reread `sshd_config`, and it does not by itself restart the service.

Both are state-changing requests and were **not executed for this chapter**. A reload should not be described as automatically harmless just because it usually avoids replacing the main process.

After an approved repair, an administrator still needs to check the new status, examine fresh messages, and verify the behavior users actually need. “The restart command succeeded” is weaker evidence than “the service is running, the new logs are clean for this attempt, and the previously failing connection works.”

## When there is no systemd manager

There are two common failures at the boundary of this walkthrough.

If the program is missing, Bash may report:

```text
bash: systemctl: command not found
```

This is a **schematic shortened error**; Bash may include a line number. It says the shell could not find the command. It says nothing about whether SSH itself is healthy.

If systemctl is installed but cannot reach a suitable manager, a **schematic error** may instead include:

```text
System has not been booted with systemd as init system (PID 1). Can't operate.
```

Other environments produce a bus-connection error, referring to the communication channel used to talk to the manager. That is not the same as a unit entering the failed state.

A conventional distribution may use OpenRC, runit, s6, or another arrangement instead of systemd. Use that distribution's documented service names, inspection commands, and log locations. A `service` command on one distribution may be a compatibility wrapper and behave differently elsewhere. Guessing a systemd-equivalent command from memory is not a reliable repair procedure.

Minimal containers often have only a small supervisor or a single application as PID 1. Their logs may be captured by the container platform rather than stored in a systemd journal. Inspect the application's state and the platform's logs using the owner's documented access path. Restarting a container, if later authorized, is a separate platform operation, not a substitute spelling for a systemd service restart.

There is also a distinction within systemd: the **system manager** manages machine-wide units, while a **user manager** can manage units belonging to one logged-in account. The commands in this chapter target the system manager by default. Systemctl's `--user` option selects the calling user's manager instead. It does not provide elevated privileges or make an unavailable system manager appear. A user manager and the requested user unit must actually exist for that separate investigation.

The useful method survives these differences. Find who owns the task, establish its present state, understand how it is meant to start, and read the messages from the relevant attempt. Then decide what evidence is still missing before changing anything.

## Further reading

- [systemd: systemctl](https://www.freedesktop.org/software/systemd/man/latest/systemctl.html)
- [systemd: journalctl](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html)
- [systemd: bootup](https://www.freedesktop.org/software/systemd/man/latest/bootup.html)
