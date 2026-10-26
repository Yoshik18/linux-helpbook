# Practice investigations

These labs combine the earlier chapters. Work in a disposable Linux environment
as your ordinary user. They do not require root, a cloud account or a production
service. Keep a short record of the symptom, observations, explanation and next
check. Do not change several things at once and then guess which change helped.

## 1. Did the search succeed, find nothing or fail?

**Question:** a log-checking script prints `0` and exits successfully. Does that
mean the log file was read successfully and had no errors?

This Bash lab creates a small fixture, then deliberately queries a missing file.
The parentheses isolate shell-option changes from your interactive shell.

```bash
(
    set +e
    set +o pipefail
    lab=$(mktemp -d) || exit 1
    printf 'INFO started\nERROR request failed\n' > "$lab/app.log"

    grep -q ERROR "$lab/app.log"
    printf 'Match status: %s\n' "$?"

    grep -q WARNING "$lab/app.log"
    printf 'No-match status: %s\n' "$?"

    grep -q ERROR "$lab/missing.log"
    printf 'Read-error status: %s\n' "$?"

    grep ERROR "$lab/missing.log" | wc -l
    printf 'Pipeline without pipefail: %s\n' "$?"

    set -o pipefail
    grep ERROR "$lab/missing.log" | wc -l
    printf 'Pipeline with pipefail: %s\n' "$?"
    printf 'Lab directory: %s\n' "$lab"
)
```

With GNU grep, the first three statuses should be `0`, `1` and `2`. A matching
line, no match and a read failure are three different outcomes. A script that
handles only zero/nonzero without considering the command's contract can hide
a real error or treat a normal no-match result as a failure.

Without `pipefail`, the pipeline takes the status of its last command, `wc`,
which can successfully count zero input lines even though grep failed to open
its file. With Bash `pipefail`, the pipeline returns the rightmost nonzero status,
here `2`. The option does not repair the failed read, and it does not make every
nonzero result unexpected. Handle the cases your script actually cares about.

**Check your understanding:** what happens if grep successfully reads a file and
finds no matching lines while `pipefail` is enabled? Why might `set -e` need care
in a script that expects that result?

Source: [GNU grep exit status](https://www.gnu.org/software/grep/manual/html_node/Exit-Status.html)
and [Bash pipelines](https://www.gnu.org/software/bash/manual/html_node/Pipelines.html).

## 2. Where did the deleted file go?

**Question:** someone removes a file, but the process using it still reads its
contents. Is the directory listing wrong?

This Python 3 lab creates a 1 MiB file in a private temporary directory and keeps
one descriptor open while removing that file's name. It never unlinks an
existing application file. Linux `/proc` must be mounted for the descriptor-path
observation.

```python
import os
import tempfile
from pathlib import Path

with tempfile.TemporaryDirectory(prefix="linux-open-file-") as directory:
    path = Path(directory) / "sample.bin"
    path.write_bytes(b"x" * (1024 * 1024))

    with path.open("rb") as stream:
        path.unlink()
        info = os.fstat(stream.fileno())
        print("Name exists:", path.exists())
        print("Link count:", info.st_nlink)
        print("Logical bytes:", info.st_size)
        print("Still readable:", stream.read(4))
        descriptor = Path(f"/proc/{os.getpid()}/fd/{stream.fileno()}")
        print("Descriptor target:", os.readlink(descriptor))
```

Expect `Name exists: False`, link count `0`, logical bytes `1048576` and readable
bytes `b'xxxx'`. The descriptor target normally ends in `(deleted)`. The directory
entry is gone, but the open descriptor still references the file. When there are
no remaining links and the last open reference closes, its storage can be
released. The file's logical length is not a precise measure of allocated disk
blocks or of filesystem-wide free-space changes.

In a real investigation, this is a reason to inspect open files, not a reason
to truncate random `/proc` descriptors or restart a database without approval.
Use the [disk-space checklist](../troubleshooting/disk-space.md) to investigate
capacity, inode usage and other causes of `df`/`du` disagreement.

Source: [`unlink(2)`](https://man7.org/linux/man-pages/man2/unlink.2.html)
and [`proc_pid_fd(5)`](https://man7.org/linux/man-pages/man5/proc_pid_fd.5.html).

## 3. Is the HTTP service broken, or is the request wrong?

**Question:** a client reaches a server but receives HTTP 404. Should you start by
changing DNS, restarting the service or checking the requested path?

Use Python 3 and curl in two terminals. In terminal one, serve only a temporary
lab directory on loopback. If port 8765 is occupied, use another unused port in
both terminals. Do not expose the server on a public interface.

```bash
lab=$(mktemp -d) || exit 1
printf 'service is reachable\n' > "$lab/index.html"
python3 -m http.server 8765 --bind 127.0.0.1 --directory "$lab"
```

In terminal two:

```bash
curl --max-time 3 --output /dev/null --write-out 'HTTP %{http_code}\n' http://127.0.0.1:8765/missing
printf 'curl status without --fail: %s\n' "$?"

curl --fail --max-time 3 http://127.0.0.1:8765/missing
printf 'curl status with --fail: %s\n' "$?"

curl --fail --max-time 3 http://127.0.0.1:8765/
```

The first request should show HTTP 404 while curl itself returns `0`. A completed
HTTP exchange is not the same as a successful application response. With `--fail`,
curl returns `22` for this HTTP error. The final request should return the text
from `index.html`. These exit statuses follow curl's contract, not a universal
meaning shared by all programs.

Stop your server with Ctrl+C in terminal one. Record the evidence: TCP connected,
an HTTP server answered and one path was missing. This lab does not test DNS or
TLS, because the URL uses an IP address and plain HTTP. A successful root path
does not prove every endpoint or dependency is healthy.

Source: [curl exit codes and `--fail`](https://curl.se/docs/manpage.html)
and [Python's lab HTTP server](https://docs.python.org/3/library/http.server.html).

## Turn observations into a useful answer

For any lab or interview scenario, practice answering:

1. What exactly failed, and for which user, process or client?
2. Which observation narrows the problem? Which conclusion would be too strong?
3. What is the smallest next check that separates the remaining possibilities?
4. If a change is needed, what could it break and how would you reverse it?

The goal is to understand why a command is useful, not to run every command in a
list. Repeat these labs after a few days and explain the result before executing
them. Then try the shorter troubleshooting guides against your own disposable
service.

[Previous: performance and debugging](12-performance-and-debugging.md) · [Guide index](README.md)
