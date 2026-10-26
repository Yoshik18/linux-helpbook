# 12. Troubleshooting without guessing

[Contents](../README.md) | [Previous: packages](11-packages.md) | [Next: security](13-security.md)

Troubleshooting is a way to reduce uncertainty, not a search for a command that makes the symptom disappear. Start with a precise symptom, gather read-only evidence, form one testable hypothesis, and change one thing at a time only when you are authorized to do so.

## Define the symptom

Record what failed, where, when, and what changed shortly before it began. Distinguish the user's visible symptom from a suspected cause. "The service is broken" is broad; "requests to this hostname time out from one subnet since the deployment at 14:10" is testable.

## Move through layers

For a failed web request, test in order:

1. Does the local interface have the expected address? Inspect with `ip address show`.
2. Is there a route toward the destination? Inspect with `ip route show` or `ip -6 route show`.
3. Does the system resolve the hostname? Query the configured resolver with `getent ahosts name`.
4. Can the client connect and receive an application response? Use an approved client such as `curl` with a bounded timeout.
5. Is the expected service listening locally, and what do its logs say? Inspect `ss` and the system's supported logging tools.

Each check answers a limited question. For example, successful name resolution does not prove a TCP connection, and a listening socket does not prove the application is healthy. Keep the hostname, address family, port, timestamp and client location consistent when comparing tests.

## Compare a known-good case

Compare the failing case with one that works: same service, different client; same client, different hostname; or same destination, different time. Change one variable at a time. This can separate client-specific, network-path and server-side symptoms without assuming a root cause.

## Preserve evidence

Capture exact command, time, exit status and relevant output. Redact credentials, tokens, private addresses and personal data before sharing. Logs can contain sensitive values even when the command itself is read-only. Keep a copy of original evidence before rotating logs or restarting services.

## Make a change only with a plan

Before a state change, identify the exact target, expected effect, owner approval, maintenance impact, rollback and success check. Avoid broad actions such as flushing firewall rules, recursively changing permissions, restarting unrelated services or killing processes by name. If the system is production and the change is not covered by an approved runbook, stop and involve the service owner.

## Common mistakes

- Changing several variables at once, which obscures the cause.
- Treating a timeout, DNS failure and HTTP error as the same failure.
- Assuming that a single healthy check proves the whole path works.
- Running destructive diagnostics on production to reproduce a problem.
- Sharing raw logs or command output without checking for secrets and personal data.

## Further reading

- [Google SRE Book: troubleshooting](https://sre.google/sre-book/effective-troubleshooting/)
- [Linux man-pages: proc(5)](https://man7.org/linux/man-pages/man5/proc.5.html)
- [curl manual](https://curl.se/docs/manpage.html)
