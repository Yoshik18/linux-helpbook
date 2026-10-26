# 13. Practice: turn symptoms into testable hypotheses

These short investigations use the disposable fixture and your own loopback server. Work as an ordinary user. Start by writing down: observed symptom, scope, time, one hypothesis, and a result that would weaken it. A command is useful when you can say what its output does and does not establish.

## Lab 1: a pipeline reports success when input could not be read

The lab setup intentionally does not create `missing.log`: this reproduces the read error being investigated. If Bash reports that `$LINUX_LAB` is unset or the setup script cannot be found, that is a separate lab-setup issue.

```bash
(
    set +e
    set +o pipefail
    grep ERROR "$LINUX_LAB/missing.log" | wc -l
    printf 'pipeline status without pipefail: %s\n' "$?"
    set -o pipefail
    grep ERROR "$LINUX_LAB/missing.log" | wc -l
    printf 'pipeline status with pipefail: %s\n' "$?"
)
```

Predict whether the count proves the file was read. `wc` can successfully count empty input, so without `pipefail` its zero status hides grep's read error. With Bash `pipefail`, the pipeline is nonzero (GNU grep commonly returns 2 for an error). A valid search with no matches commonly returns 1 instead. A script should handle “no matches” separately from unreadable input when that distinction matters.

## Lab 2: local HTTP symptoms at different layers

From the repository root in terminal one:

```bash
source fundamentals/labs/setup.sh
python3 -m http.server 8765 --bind 127.0.0.1 --directory "$LINUX_LAB/notes"
```

In terminal two:

```bash
ss -lnt 'sport = :8765'
curl --connect-timeout 2 --max-time 5 --fail http://127.0.0.1:8765/todo.txt
curl --max-time 5 --output /dev/null --write-out 'HTTP %{http_code}\n' http://127.0.0.1:8765/missing
```

Use another unused port consistently if needed; stop your own server with Ctrl+C. The listener entry proves a local TCP socket is listening in the observed network namespace, not that remote clients can reach it. The file request proves this HTTP endpoint answered successfully; 404 proves an HTTP response arrived but the requested path was not found. This numeric loopback exercise tests neither DNS nor TLS. After stopping the server, repeat the request: connection failure is not the same as HTTP 404.

## Lab 3: permissions are more than the final file mode

```bash
stat -c '%A %a %n' "$LINUX_LAB/config/private.txt"
namei -l "$LINUX_LAB/config/private.txt"
find "$LINUX_LAB/config" -type f -perm /077 -print
```

`stat` checks the file's mode; GNU `namei -l` traces parent components; GNU `find -perm /077` selects any group/other mode bit. These are read-only checks. Explain why a final file's read bit cannot guarantee successful path access, and why a match from `find` deserves review rather than automatic `chmod`.

## Lab 4: follow an evidence trail for a slow request

Scenario: a request times out, but host CPU appears mostly idle. Do not assume the network is the cause. Write two competing hypotheses—for example, no listener versus a request accepted but waiting on an application dependency. For each, name an observation that would support it and one that would weaken it. A bounded sequence might be:

1. From the affected client, run `getent ahosts HOST` for the exact hostname. This tests system name lookup, not the application's private resolver or connection.
2. On the authorized server, run `ss -lnt` and inspect the expected address/port. This checks visible local listeners, not firewall reachability from the client.
3. Run `curl --connect-timeout 2 --max-time 5 --verbose https://HOST/` only for an endpoint you may contact. Separate lookup, connect, TLS and HTTP progress; verbose output can contain private details.
4. If connection and HTTP response work but the operation is slow, align application logs and bounded `vmstat 1 5` samples to the same interval. `vmstat` describes system activity, not the specific request.

Record what remains unknown. A successful ping or idle CPU does not prove the application is healthy. Stop when evidence distinguishes the hypotheses or state what access/data is missing; do not make live configuration changes as part of the exercise.

## Lab 5: explain a small fixture without overclaiming

```bash
awk '$4 == 500 {n++} END {print n+0}' "$LINUX_LAB/logs/access.log"
grep '^ERROR ' "$LINUX_LAB/logs/app.log" | sort | uniq -c | sort -nr
awk '{print $1}' "$LINUX_LAB/logs/access.log" | sort | uniq -c
```

The access fixture has two 500 responses; the most frequent error is `ERROR api timeout`. These commands summarize only the supplied fictional records. They do not establish why a real service failed. Write a two-sentence incident note separating observation from a hypothesis and include the log time window if present.

[Manual: Bash pipelines](https://man7.org/linux/man-pages/man1/bash.1.html) · [curl](https://curl.se/docs/manpage.html) · [Previous](12-performance-and-debugging.md) · [Guide index](README.md)
