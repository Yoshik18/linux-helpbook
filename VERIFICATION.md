# Verification notes

This update was checked on Linux aarch64 with GNU Bash 5.2.37 and Python 3.14.
Results describe this environment, not every distribution or a production host.

## Checks run

- The selected examples passed thirteen regression tests: local scope,
  counters with `set -e`, cleanup preserving failure status, retry argument
  boundaries and errors, warning logging, configuration parsing, missing option
  arguments, the permissions lab and the disk-space lab, plus the fundamentals
  investigations for pipeline status, deleted open files and HTTP error handling.
- Bash/sh fenced blocks are checked with `bash -n`, and Python fences with Python's
  parser. These checks do not execute the blocks;
  illustrative blocks that need caller variables are not all runnable programs.
- Relative Markdown file links were checked. Heading fragments are not checked.
- Markdownlint CLI2 0.24.0 passed using `.markdownlint.json`. The configuration
  preserves existing long lines, heading/list/fence spacing and table alignment
  rather than reformatting the entire reference. Other rules remain enabled.
- The local HTTP server and curl exchange passed with an unused loopback port
  substituted for 8765. Only the temporary lab directory was served.
- The documented `ps` sorting commands, `free -h` and repeated `vmstat` sampling
  ran successfully. Permission failure and restoration were tested as a non-root
  user in a temporary directory. No production processes were signalled.
- `git diff --check` passed.

Run the dependency-free local checks from the repository root:

```bash
python3 tools/check_docs.py
python3 tools/test_examples.py
```

The tests create small temporary fixtures. Set `TMPDIR` to a scratch directory
if your environment requires it. Tests deliberately execute only selected,
reviewed snippets; do not use them to execute arbitrary Markdown from strangers.
Python's unittest output distinguishes skipped tests from passed ones.

## Limits and untested behavior

- The four introductory chapter labs (01–04) have not been executed. Their Bash
  syntax was checked, and they remain labelled untested. The later process,
  memory, sparse-file, package-query, loopback and isolation observations were
  run in this container where the required tools were available.

- `ss`, `dig` and `lsof` were not installed here. Their descriptions were checked
  against documentation where available; their output was not exercised locally.
- No working systemd journal was used. The `journalctl` example remains untested.
- No cloud resources, real service changes, intentional host-wide CPU/memory
  pressure, filesystem filling, production signals or permission repairs ran.
- Inode exhaustion was explained but not induced. The deleted-open-file behavior
  was tested only on the small temporary file in the practice lab, not on a live
  service. Other kernels, cgroups and filesystems can behave differently.
- ShellCheck was not available, so this update does not claim a ShellCheck pass.
- All 70 unique external Markdown URLs were attempted: 64 returned HTTP 200.
  Six GNU manual section URLs could not be rechecked because this
  environment reported network unreachable, not HTTP 404. An earlier retrieval
  of the official Bash manual supported the scope and exit-status explanations.
  HTTP 200 alone is not proof that a page's contents are correct.
- This repository had no license file at the start of the change. This PR does
  not choose a license or change the rights to existing content. Official source
  links support the explanations; linked material retains its own license.

[Back to the learning path](README.md)
