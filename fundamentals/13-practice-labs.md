# 13. Practice with failures, not just happy paths

Use the [practice setup](01-how-linux-works.md). Run these exercises as your
ordinary user. They change only new lab files or a loopback server you start.
Expected results below describe the fixture, not a real production incident.

## 1. Find why a log-checking pipeline lies

Try this in Bash:

```bash
(
    set +e
    set +o pipefail
    grep ERROR "$LINUX_LAB/missing.log" | wc -l
    printf 'without pipefail: %s\n' "$?"
    set -o pipefail
    grep ERROR "$LINUX_LAB/missing.log" | wc -l
    printf 'with pipefail: %s\n' "$?"
)
```

**Before opening the answer:** did a successful line count prove the log was read?
What should a script do if no matches is a normal result?

<details>
<summary>Read the result</summary>

`wc` can successfully count zero input lines even when grep could not open the
file. Without pipefail, the pipeline reports wc's status, usually 0. With
pipefail, Bash reports the rightmost nonzero status, here GNU grep's read-error
status 2. A valid search with no matches instead returns 1. Handle the command's
contract explicitly; do not equate all nonzero statuses with the same failure.

</details>

## 2. Read a file after removing its name

Run the complete block, which creates and removes only its own dummy file:

```bash
(
    printf 'still readable\n' > "$LINUX_LAB/data/unlinked.txt"
    exec 3< "$LINUX_LAB/data/unlinked.txt"
    rm -- "$LINUX_LAB/data/unlinked.txt"
    readlink "/proc/$BASHPID/fd/3"
    cat <&3
    exec 3<&-
)
```

<details>
<summary>Read the result</summary>

The pathname disappears, but descriptor 3 still references the open file. The
link target normally ends in `(deleted)`, and cat prints `still readable`.
Closing the last open reference after the last link is removed lets storage be
released. File length does not directly measure a change in filesystem free
blocks. `$BASHPID` identifies this Bash subshell; `$$` can still name its parent.

On a real system, investigate with approved open-file inspection. Do not remove
an active service's files or truncate descriptors as a recovery experiment.

</details>

## 3. Distinguish HTTP 404 from a failed connection

Terminal one, from this repository's root:

```bash
source fundamentals/labs/setup.sh
python3 -m http.server 8765 --bind 127.0.0.1 --directory "$LINUX_LAB/notes"
```

Terminal two:

```bash
curl --max-time 3 --output /dev/null --write-out 'HTTP %{http_code}\n' http://127.0.0.1:8765/missing
printf 'plain curl: %s\n' "$?"
curl --fail --max-time 3 http://127.0.0.1:8765/missing
printf 'curl with fail: %s\n' "$?"
curl --fail --max-time 3 http://127.0.0.1:8765/todo.txt
```

Use another unused port in both terminals if needed. Stop your own server with
Ctrl+C. It serves only the temporary notes directory on loopback.

<details>
<summary>Read the result</summary>

Expect HTTP 404 and plain curl status 0, then `--fail` status 22. The last request
returns the three todo lines. The 404 proves an HTTP server answered that request;
it is not a DNS or TCP connection failure. This lab uses an IP and plain HTTP,
so it does not test DNS or TLS. After stopping the server, repeat the final
request: a connection error is a different observation from a 404.

</details>

## 4. Build a small incident note from the fixture

Without changing the source logs, produce:

1. Number of 500 responses.
2. Most frequent error message.
3. A list of client addresses with request counts.
4. A separate file containing only ERROR lines.

<details>
<summary>One answer</summary>

```bash
awk '$4 == 500 {n++} END {print n+0}' "$LINUX_LAB/logs/access.log"
grep '^ERROR ' "$LINUX_LAB/logs/app.log" | sort | uniq -c | sort -nr
awk '{print $1}' "$LINUX_LAB/logs/access.log" | sort | uniq -c
grep '^ERROR ' "$LINUX_LAB/logs/app.log" > "$LINUX_LAB/incident-errors.log"
```

There are two 500 responses. `ERROR api timeout` occurs twice. This tells you
what this tiny fixture contains, not the cause of a real outage. A useful note
separates those observations from hypotheses and records the time window.

</details>

## After the exercises

Inspect the printed practice path before removing anything. You can keep it
for another session; the setup never automatically deletes an earlier lab.
If you choose to clean it up interactively, use `rm -ri -- "$LINUX_LAB"` only
after verifying that exact path belongs to your practice run. Do not substitute
a home, application, mount or production path.

[Manual: Bash](https://man7.org/linux/man-pages/man1/bash.1.html)
· [unlink](https://man7.org/linux/man-pages/man2/unlink.2.html)
· [curl](https://curl.se/docs/manpage.html)
· [Previous](12-performance-and-debugging.md) · [Guide index](README.md)
