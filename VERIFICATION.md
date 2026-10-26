# Verification notes

The command-led guide was checked on Linux aarch64 with GNU Bash 5.2.37 and
Python 3.14.7. Results describe this environment, not every distribution or a
production host.

## Checks run

- All 22 selected regression tests passed. They cover shell scope, counters,
  cleanup preserving failure status, retries, logging, configuration parsing,
  missing option arguments, the existing permissions/disk labs, copying and
  renaming, hard/symbolic links, an archive round trip, log counts, field filtering,
  executable permissions, umask, terminating a lab child, a sparse file,
  misleading pipeline success, a deleted-open file and HTTP error handling.
- The tests source the actual `fundamentals/labs/setup.sh` into new temporary
  directories. Direct execution of that script was separately checked: it
  returns status 2 and explains how to source it.
- All 124 Bash/sh fences passed `bash -n`. This parses syntax without executing
  the examples. Commands requiring optional tools, an administrator or an
  interactive terminal are not made executable merely by this check.
- All 85 relative Markdown file links resolved. Heading fragments are not checked.
- Markdownlint CLI2 0.24.0 passed across 23 Markdown files. The configuration
  preserves the existing long-line/spacing style and allows `details`/`summary`
  for expandable exercise answers; other HTML elements are still checked.
- The HTTP test substitutes an unused loopback port for 8765 and serves only
  temporary fictional notes. It verifies a successful file request and that
  curl handles HTTP 404 differently with and without `--fail`.
- `git diff --check` passed.

Run the local checks from the repository root:

```bash
python3 tools/check_docs.py
python3 tools/test_examples.py
bash -n fundamentals/labs/setup.sh
```

For Markdown linting, install or use Markdownlint CLI2 0.24.0 separately. The
Python checks use the standard library; the selected examples also require the
Bash/GNU command-line tools they exercise and curl for the HTTP test.

The tests create small temporary fixtures and remove their own test directories.
Set `TMPDIR` to a scratch directory if required. They execute selected reviewed
snippets, not every block in the repository. Do not run the harness against
unreviewed Markdown from strangers. Unittest distinguishes skipped tests from
passed ones; this run had no skips.

## Limits and untested behavior

- Not every example in chapters 1–13 was executed. Syntax checks and manual
  reference checks are not behavioral tests. Host observations vary; illustrative
  output is not a snapshot of the reader's machine.
- `ss`, `dig`, `lsof`, `systemctl`, `journalctl`, `strace`, `pidstat`, `iostat` and
  ShellCheck were unavailable in this environment. No pass or output is claimed
  for these tools. Their examples must be tried separately on a suitable system.
- Interactive job control, real systemd services/journals, package installation,
  RPM/DNF systems, live tracing and network capture were not exercised.
- No cloud resources, real service changes, host-wide CPU/memory pressure,
  filesystem filling, mounts or production permission repairs ran. Signals in
  the tests targeted only the child created by that test.
- Inode exhaustion was not induced. The deleted-open-file test uses a tiny
  temporary file, not a live service. Filesystems, kernels and cgroups can differ.
- External URL reachability is checked separately from content correctness.
  GNU Bash manual section URLs were unreachable from this environment, not
  confirmed broken. Accessible upstream manual mirrors support the references.
- This repository had no license file at the start of the change. This update
  does not choose a license or change the rights to existing content. Linked
  projects and documentation retain their own licenses and attribution.

[Back to the learning path](README.md)
