# 8. Inspect boot, services, schedules, and logs

This chapter describes systems using systemd. Many containers use another process as PID 1 or no service manager at all. PID 1 is the first process in a PID namespace; on a conventional systemd host it is systemd, which manages services and other units. A container's PID 1 may instead be the application process.

## Identify the environment and inspect units

```bash
cat /proc/1/comm
systemctl --no-pager --failed
systemctl --no-pager list-units --type=service --state=running
systemctl --no-pager list-unit-files --type=service
```

`/proc/1/comm` shows the command name of PID 1. `systemctl` queries need a reachable systemd manager and may fail in containers or other init environments. `list-units` shows currently loaded runtime units; `list-unit-files` shows installed unit files and enablement information. A unit may be enabled for future activation but not currently running; a running unit need not be enabled. Unit states such as `active`, `inactive`, and `failed` answer different questions from enablement states such as `enabled`, `disabled`, or `static`.

## Inspect one unit and its recent journal

Choose a unit that exists and that you are authorized to inspect. `systemd-journald.service` is only an example; not every system exposes it as expected.

```bash
unit=systemd-journald.service
systemctl --no-pager status "$unit"
systemctl show "$unit" -p ActiveState -p SubState -p MainPID -p FragmentPath
systemctl cat "$unit"
journalctl -b -u "$unit" -n 20 --no-pager
```

`status` summarizes state and recent log lines; it can return nonzero for an inactive or failed unit. `show -p` requests selected properties. `cat` displays unit source and drop-ins, which may contain sensitive paths or arguments. `journalctl -b` selects the current boot, `-u` filters by unit, `-n` limits the number of entries, and `--no-pager` prints directly. Reading permissions vary. A healthy unit state does not prove the application is serving requests.

Other useful focused journal queries:

```bash
journalctl --list-boots --no-pager
journalctl -b -p warning --no-pager
journalctl --since '30 minutes ago' --until '5 minutes ago' --no-pager
journalctl -b -k -n 30 --no-pager
```

`-p warning` includes warning and more severe priorities; `-k` selects kernel messages. Combine time and unit filters to avoid dumping unrelated logs. `-o short-monotonic` helps compare event order within one boot. Old boot records may be absent because of retention policy or volatile storage, not because no event occurred.

## Find scheduled work without changing it

```bash
systemctl list-timers --all
crontab -l
```

The first lists systemd timers visible to the manager; the second lists the current user's cron table. Cron is not necessarily installed or enabled. Cron jobs run with a smaller, different environment than an interactive shell, so use explicit paths and controlled output when authoring one. Do not inspect another user's schedule or add a job without authorization.

## Logs may live elsewhere

If the practice setup provides a log file:

```bash
tail -n 5 "$LINUX_LAB/logs/app.log"
grep -n -E 'ERROR|WARN' "$LINUX_LAB/logs/app.log"
```

`tail -n` shows the last lines; `grep -n -E` finds matching alternatives and prints line numbers. `tail -F` follows a filename across common rotation patterns until Ctrl+C. Applications may log to a file, the journal, standard output, or a remote collector; determine the configured destination before concluding logs are missing.

## State-changing actions

Most learners should stick to the inspection commands above. For a service you
created in a disposable systemd VM, these actions have different effects; do not
run them against an unfamiliar or production unit:

| Action | What it does | Main risk |
|---|---|---|
| `systemctl daemon-reload` | Makes the manager reread unit definitions. It does not reload an application's configuration. | A bad unit file can change how future starts behave. |
| `systemctl start UNIT` | Requests activation now. | The service may perform work or contact other systems. |
| `systemctl reload UNIT` | Asks a service that supports reload to reread configuration without a full stop. | Unsupported units may reject it; application behavior varies. |
| `systemctl restart UNIT` | Stops and starts the service. | Can interrupt requests, jobs or data writes. |
| `systemctl enable UNIT` | Arranges activation during a future boot; it does not start the unit now. | Changes future boot behavior. |
| `systemctl enable --now UNIT` | Combines enablement and starting. | Both immediate and future behavior change. |

`UNIT` is a placeholder, not a literal unit name. Only substitute a service you
created and verified in the disposable VM, after reviewing its unit and recovery
plan. These commands require suitable permissions; the guide does not ask you to
create or alter a system service.

## Practice

On a disposable systemd VM, select a unit you confirmed exists and read only its active state and last ten records from the current boot. Do not restart it. Replace the placeholder below with that unit name before running:

```bash
unit=YOUR_EXISTING_UNIT.service
systemctl show "$unit" -p ActiveState -p SubState
journalctl -b -u "$unit" -n 10 --no-pager
```

[systemctl manual](https://www.freedesktop.org/software/systemd/man/latest/systemctl.html) · [journalctl manual](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html) · [Previous](07-storage-and-filesystems.md) · [Index](README.md) · [Next](09-packages-and-software.md)
