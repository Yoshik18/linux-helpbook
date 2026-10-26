# Verification notes

The current whole-repository revision was checked on Linux aarch64 with GNU Bash
5.2.37 and Python 3.14.7. These results describe this environment, not every
Linux distribution or production host.

## Checks run

- Reviewed all 23 tracked Markdown files for navigation, technical explanation,
  consistency, safety notes, duplication and intended audience. The three
  troubleshooting checklists were retained because they already provided
  task-based diagnostics and safe examples; the learning path now links them.
- All 17 selected behavior tests passed with no skips. They cover the sourced
  fixture and Bash quoting/arguments, temporary-file cleanup status, file copy
  and rename, links, archive round-trip, fixture log/field results, permissions,
  umask, child-process termination, sparse/deleted-open files, pipeline status,
  and a loopback HTTP request.
- The lab setup script passed `bash -n`. Sourcing it created the expected private
  practice files and mode; running it with `bash fundamentals/labs/setup.sh`
  returned status 2 with source-only usage guidance.
- `tools/check_docs.py` checked 119 Bash fences with `bash -n`, 95 local Markdown
  file links and zero heading fragments. This checks syntax and paths, not the
  behavior of every example. The test harness executes only selected reviewed
  examples from temporary directories.
- Markdownlint CLI2 0.24.0 passed across all 23 Markdown files. The config now
  checks heading/list/fence spacing; it preserves the repo's existing long-line
  and table-alignment choices and allows only `details`/`summary` HTML elements.
- `git diff --check` passed.
- A separate reachability pass checked 42 unique external URLs: 41 returned HTTP
  200. The GNU Bash reference URL was unreachable from this environment, not
  confirmed broken. HTTP success does not establish that linked documentation
  supports every sentence beside it.

Run the local checks from the repository root:

```bash
bash -n fundamentals/labs/setup.sh
python3 tools/check_docs.py
TMPDIR=/path/to/scratch python3 tools/test_examples.py
npx --yes markdownlint-cli2@0.24.0 '**/*.md'
git diff --check
```

The tests use Python's standard library, Bash/GNU utilities, `tar`, `stat` and
`curl`. They bind the HTTP lab to loopback, choose an unused port, and serve only
the fictional fixture directory. Set `TMPDIR` to a scratch location if needed.
Do not use this harness to execute arbitrary Markdown from an unreviewed source.

## Not tested

- The 17 behavioral tests are selected examples, not execution of all code blocks.
  Remaining syntax-only snippets, host-dependent observations and cross-platform
  behavior have not been proven by these results.
- `ss`, `dig`, `lsof`, `systemctl`, `journalctl`, `strace`, `pidstat`, `iostat`,
  and ShellCheck were unavailable here. The guides identify where those tools are
  optional; this environment's output for them is not claimed.
- Real systemd services/journals, RPM/DNF package transactions, package
  installation, interactive job control, production tracing, host-wide pressure,
  inode exhaustion, mounts and live filesystem changes were not exercised.
- Signals were tested only against a child process created by the lab. The
  deleted-open-file example was exercised with a small temporary file, not a
  service log. Kernels, filesystems, cgroups and distribution packaging differ.
- External URL status was checked, not every page's contents or every claim against
  every vendor release. The GNU Bash manual was unreachable, not confirmed broken.
- This repository had no license file at the start of the revision. The external
  tutorial link is further reading/inspiration only; its text and examples were
  not copied. This revision does not establish a new license for the repository.

[Back to the Linux learning path](README.md)
