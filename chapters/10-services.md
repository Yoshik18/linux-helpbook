# 10. Boot, services and logs

[Contents](../README.md) | [Previous: networking](09-networking.md) | [Next: packages](11-packages.md)

A Linux machine starts through firmware and a bootloader, which loads the kernel and an initial environment. The kernel brings up hardware and starts a first user-space process. Many distributions use systemd as that system and service manager, but not every Linux system does.

## Identify the service manager

```bash
ps -p 1 -o pid=,comm=,args=
```

On procps-ng systems this inspects process ID 1 and prints selected fields: PID, command name and arguments. PID 1 is the first process in a Linux process namespace. In a container, it may be a small init process rather than the host's service manager. A process name is evidence, not proof of a working service-management interface.

## Inspect a systemd service

If the machine uses systemd and `systemctl` can communicate with its manager, inspect a known service without changing it:

```bash
systemctl status ssh.service
```

The service might be called `sshd.service` on some distributions, and it may not be installed. `status` reports the manager's view of unit state and recent log lines. It is not a complete diagnosis. A container or restricted session may return an error because no systemd manager is available.

`systemctl is-active` returns a compact state and a status code:

```bash
systemctl is-active ssh.service
```

An inactive service is not necessarily a fault; some services run only when requested. Do not start, stop, enable or restart a service unless you are authorized and understand the impact. `enable` changes boot-time configuration; `start` changes current state; `restart` interrupts and recreates the service process.

## Read journal messages

On a system using systemd's journal, `journalctl` can show messages. For the current boot:

```bash
journalctl -b -n 50 --no-pager
```

`-b` selects the current boot, `-n 50` limits output to the latest fifty entries, and `--no-pager` prints directly. Access to some logs may be restricted. Service-specific logs can be selected with `-u name.service`. Times, retention and available records depend on the system's journal configuration.

Logs provide observations, not a guaranteed explanation. Check timestamps, service identity and the event preceding the symptom. A repeated error can be a consequence rather than the cause.

## When systemd is absent

Use the service manager and logging system documented for that distribution. Minimal containers often do not run a full init system. Avoid treating a failed `systemctl` call in such an environment as evidence the application itself is broken.

## Common confusion

- PID 1 in a container may not be the host init system.
- A service can be active but unable to serve requests correctly.
- `enable` and `start` are different operations.
- A log line is evidence at a time, not automatically a root cause.
- Service names and available logs vary between distributions.

## Further reading

- [systemd: systemctl](https://www.freedesktop.org/software/systemd/man/latest/systemctl.html)
- [systemd: journalctl](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html)
- [systemd: bootup](https://www.freedesktop.org/software/systemd/man/latest/bootup.html)
