# 8. Inspect services, startup and logs

This chapter needs a Linux systemd host. Many containers do not run systemd as
PID 1. The service examples are inspection recipes, not commands to restart a
real application as part of a lesson.

## Check the init system and failed units

```bash
cat /proc/1/comm
systemctl --no-pager --failed
systemctl --no-pager list-units --type=service --state=running
systemctl --no-pager list-unit-files --type=service
```

If PID 1 is not systemd or no manager is reachable, the `systemctl` queries can
fail even though the container is healthy. `list-units` shows loaded runtime
units; `list-unit-files` describes installed unit files and enablement states.
A running service need not be enabled, and an enabled unit need not be running.

## Inspect one service without changing it

Replace the unit with an existing service you are authorized to inspect. The
journald example below is appropriate only where that unit exists.

```bash
unit=systemd-journald.service
systemctl --no-pager status "$unit"
systemctl --no-pager cat "$unit"
systemctl show "$unit" -p ActiveState -p SubState -p MainPID -p FragmentPath
```

`status` is a summary and may return nonzero for inactive/failed units. `cat`
shows backing unit files and drop-ins. `show` exposes selected properties.
Neither establishes that an application endpoint is ready. Do not post private
unit files or arguments publicly without checking them.

## Ask the journal a narrower question

```bash
journalctl --list-boots --no-pager
journalctl -b -u systemd-journald.service -n 30 --no-pager
journalctl -b -p warning --no-pager
journalctl --since '30 minutes ago' --until '5 minutes ago' --no-pager
journalctl -b -k -n 30 --no-pager
```

`-b` selects a boot, `-u` a unit and `-k` kernel records. `-p warning` includes
warning and more severe priorities. `-n` limits the last entries. Combine unit
and time filters instead of dumping the whole journal. Reading access varies.
No older boot entries can mean retention limits or volatile storage, not that
nothing happened. `-o short-monotonic` helps compare ordering within one boot.

## Follow a plain log when there is no journal

With the [practice setup](01-how-linux-works.md):

```bash
tail -n 3 "$LINUX_LAB/logs/app.log"
grep -n -E 'ERROR|WARN' "$LINUX_LAB/logs/app.log"
```

For a live file, `tail -F filename` follows its name across common rotation
patterns; Ctrl+C stops it. A process may log to stdout, a file, a journal or a
remote system. Find the configured destination before assuming a missing file
means no logs exist.

## Understand the change before running it

These are **state-changing commands for a disposable systemd VM only**. Substitute
a service you created in that VM, not a production or built-in service:

```bash
systemctl daemon-reload
systemctl reload practice.service
systemctl restart practice.service
```

They are not a sequence you must run. `daemon-reload` rereads manager unit files;
`reload` asks an application to reread its config when supported; `restart` stops
and starts it and can interrupt work. Permissions/policy apply. `enable` arranges
future activation links, while `start` requests activation now.

For schedules, inspect `systemctl list-timers --all` or your own `crontab -l`.
Cron has a different environment from your interactive shell. Do not add jobs
or print another account's schedule without authorization.

## Practice

On a disposable systemd VM, choose one existing service and display only its
active state and last ten journal entries from this boot. Do not restart it.

<details>
<summary>One answer, if journald exists and access permits</summary>

```bash
systemctl show systemd-journald.service -p ActiveState -p SubState
journalctl -b -u systemd-journald.service -n 10 --no-pager
```

</details>

[Manual: systemctl](https://www.freedesktop.org/software/systemd/man/latest/systemctl.html)
· [journalctl](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html)
· [Previous](07-storage-and-filesystems.md) · [Index](README.md) · [Next](09-packages-and-software.md)
