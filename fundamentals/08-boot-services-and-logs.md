# 8. Boot, services and logs

[Previous: Storage and filesystems](07-storage-and-filesystems.md) · [Index](README.md) · [Next: Packages and software](09-packages-and-software.md)

Boot moves control from firmware to userspace. Understanding its stages separates
a missing root filesystem from an application failure. This chapter describes a
Linux systemd host; other init systems and containers differ.

## How control reaches the service manager

Firmware initializes enough hardware to select something bootable. A boot loader
such as GRUB loads a kernel and often an initramfs; some firmware can load the
kernel directly. An **initramfs** is an early userspace archive unpacked into
memory. It supplies programs and drivers needed to discover and prepare the real
root filesystem, perhaps unlocking encrypted storage or activating storage
layers first. It is common, not mandatory for every Linux configuration. [bootup](https://www.freedesktop.org/software/systemd/man/latest/bootup.html)

After the real root is available, early userspace switches to it and hands
control to the installed init system. PID 1 is the first userspace process in
its PID namespace. On a typical systemd host, systemd occupies that role and
coordinates mounts and services. Containers often start a supervisor or an
application as their own PID 1 instead; their startup is not a replay of the
host's firmware and kernel boot.

An emergency environment unable to find root points toward drivers, storage
discovery or root configuration. A working login with a failed web service calls
for unit and application evidence, not boot-loader changes.

## Units describe relationships, not a serial script

A systemd **unit** describes a managed object. `.service` units describe service
execution, `.mount` units describe mounts, and `.target` units group related work.
Many independent units can start in parallel. [systemd.unit](https://www.freedesktop.org/software/systemd/man/latest/systemd.unit.html)

Two relationships are easily confused:

- `Wants=` and `Requires=` pull other units into an activation transaction.
  `Wants=` is weaker: a wanted unit's failure does not by itself prevent the
  requesting unit from starting. `Requires=` creates stronger failure and
  lifecycle relationships, with details depending on ordering and unit state.
- `After=` and `Before=` specify ordering **if both units are being started**.
  They do not pull the other unit in by themselves. `Requires=` alone likewise
  does not establish startup ordering. [systemd.unit](https://www.freedesktop.org/software/systemd/man/latest/systemd.unit.html)

Ordering a process after another service is not proof that its API is ready.
Readiness depends on the service type and protocol; applications still need to
handle temporarily unavailable dependencies.

## Configuration changes have different effects

`systemctl daemon-reload` makes the manager reread unit files and rebuild its
dependency view. It does not restart the application or make it reread its own
configuration. A service `reload` requests application-specific reconfiguration
when supported. A `restart` stops and starts the service and can interrupt work.
They are not troubleshooting synonyms. [systemctl](https://www.freedesktop.org/software/systemd/man/latest/systemctl.html)

Similarly, enabling a unit arranges activation links, commonly for boot; it does
not inherently start it now. A running unit need not be enabled: it could have
been started manually or pulled in by another unit. No state-changing commands
are needed for the inspection below.

## Inspect before changing anything

**Prerequisite:** a systemd host with a reachable system manager and permission
to read its journal. These systemd and journal commands are **untested on this
container**, whose PID 1 is not systemd. They inspect an existing host without
installing or restarting services.

```bash
cat /proc/1/comm
systemctl --no-pager --failed
systemctl --no-pager status systemd-journald.service
systemctl --no-pager cat systemd-journald.service
systemctl show systemd-journald.service -p ActiveState -p SubState -p FragmentPath
journalctl --list-boots --no-pager
journalctl -b -u systemd-journald.service -n 30 --no-pager
journalctl -b -k -n 30 --no-pager
```

`status` summarizes runtime state and may exit nonzero for inactive or failed
units. `cat` shows backing configuration, including drop-ins; edited disk files
may differ from the manager's loaded view before daemon-reload. Journal queries
show available records, not a guarantee that every event was captured. [systemctl](https://www.freedesktop.org/software/systemd/man/latest/systemctl.html) [journalctl](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html)

## Logs need time and retention context

`-b` selects the current boot; older boots appear only if their journal data was
retained. Volatile journal storage under `/run/log/journal` is lost on reboot.
Persistent storage normally uses `/var/log/journal`; `Storage=auto` chooses based
on that directory's existence. Defaults and overrides vary with systemd version,
build and distribution, so never assume persistence from the directory name
alone. Retention limits and rate limiting can also remove or suppress evidence. [journald.conf](https://www.freedesktop.org/software/systemd/man/latest/journald.conf.html)

Wall-clock timestamps can jump during synchronization; timezone display also
changes comparisons. Within one boot, `journalctl -b -o short-monotonic` displays
time relative to boot, useful for ordering events. Compare boot identities and
timezones before correlating different machines. [journalctl](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html)

Cron launches commands on time-based rules, generally with a smaller environment
than an interactive shell. It is not continuous service supervision. Systemd
timers are an alternative; see the [systemd.timer manual](https://www.freedesktop.org/software/systemd/man/latest/systemd.timer.html)
for calendar and monotonic scheduling behavior.

## Check your understanding

1. What does an initramfs solve before the real root becomes usable?
2. Why does `After=database.service` neither start the database nor prove readiness?
3. Why might yesterday's journal be absent even though logging works today?
