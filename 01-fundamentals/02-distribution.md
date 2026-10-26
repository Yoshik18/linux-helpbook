---
id: linux-01-02
title: Identify the Installed Distribution
level: fundamentals
prerequisites: [linux-01-01]
est_time: 20 min
tool_versions: Debian 13.7; Bash 5.2.37; GNU coreutils 9.7
last_verified: "2026-10-26"
---

# Identify the Installed Distribution

## What you'll learn

- Find the installed [distribution](../glossary.md#distribution) without guessing from its kernel.
- Read its name, release and identifier from a standard file.
- Know which release file takes precedence when two are available.

## Why this matters

An installation guide has separate Debian and Ubuntu instructions. Both systems use Linux, so the kernel name cannot tell you which instructions apply. Before installing anything, identify the distribution in the environment where the software will run.

## Mental model

The [kernel](../glossary.md#kernel) reports its own identity, as you saw in the [previous lesson](01-running-kernel.md). Distribution information comes from a different source: a small text file maintained by the operating-system vendor.

The standard location is `/etc/os-release`. Each line pairs a field name with a value. Read it as identification data, not as a script you need to execute. Do not edit it to make your machine match a tutorial.

Think of the distribution name and kernel release as two separate labels. Knowing one does not give you the other. In a [container](../glossary.md#container), the distribution information describes the environment's installed software, not necessarily the host's distribution.

## Hands-on

**Prerequisites and scope:** Complete `linux-01-01` and use the disposable environment described in [setup](../00-start-here/00-setup.md). This example reads one existing file. It installs nothing, requires no administrative permissions, creates no resources and needs no cleanup.

Output was captured on 2026-10-26 in the isolated Debian 13.7 sandbox, using Bash 5.2.37 and GNU coreutils 9.7. See the [execution record](../labs/verification/linux-01-02.json).

1. **Read the distribution's identity.** The `cat` [command](../glossary.md#command) writes the contents of a named file to the [terminal](../glossary.md#terminal). Here `/etc/os-release` is its file [argument](../glossary.md#argument), not an option. The leading `/` makes it a full path from the system's top-level directory, so the command does not depend on your current directory.

   ```bash
   cat /etc/os-release
   ```

   ```text
   PRETTY_NAME="Debian GNU/Linux 13 (trixie)"
   NAME="Debian GNU/Linux"
   VERSION_ID="13"
   VERSION="13 (trixie)"
   VERSION_CODENAME=trixie
   DEBIAN_VERSION_FULL=13.7
   ID=debian
   HOME_URL="https://www.debian.org/"
   SUPPORT_URL="https://www.debian.org/support"
   BUG_REPORT_URL="https://bugs.debian.org/"
   ```

   The command returned [exit status](../glossary.md#exit-status) `0`, with no error output. The quotes shown above belong to the file's format; they are not part of the name you would say aloud.

2. **Interpret the fields that answer the question.** `PRETTY_NAME` is a human-readable label. `ID` is the short distribution identifier used by software. `VERSION_ID` identifies the distribution release. Here the answer is Debian, release 13, code name trixie. The optional Debian-specific `DEBIAN_VERSION_FULL` field reports 13.7; it is not a field every distribution must provide.

   Your file can have different values, additional fields or no `VERSION_ID`, particularly on continuously updated distributions. Preserve what it actually says. Do not assume a missing optional field means the file is damaged.

## Verify it worked

Read `/etc/os-release` again using the same command, then check that `ID` and the displayed name describe the same distribution. The repeated command produced the same output shown above in the recorded environment.

That check establishes the vendor-reported identity of this environment. It does not inventory installed packages, prove the machine is fully patched, or identify every software component.

The vendor's alternative file is `/usr/lib/os-release`. Use it **only if `/etc/os-release` is absent**. When both exist, `/etc/os-release` takes precedence; do not combine fields from both files.

The following read was also verified in this sandbox. `cat` has the same behavior as before; only its file argument changes:

```bash
cat /usr/lib/os-release
```

```text
PRETTY_NAME="Debian GNU/Linux 13 (trixie)"
NAME="Debian GNU/Linux"
VERSION_ID="13"
VERSION="13 (trixie)"
VERSION_CODENAME=trixie
DEBIAN_VERSION_FULL=13.7
ID=debian
HOME_URL="https://www.debian.org/"
SUPPORT_URL="https://www.debian.org/support"
BUG_REPORT_URL="https://bugs.debian.org/"
```

It returned status `0` with no error output. The files matched here; matching is an observation, not a requirement to test on every system. If both files are absent, stop and consult that environment's official documentation instead of guessing a distribution from a kernel string.

## Common mistakes

- **Mistake:** Choosing a package guide because the kernel says Linux. **Symptom:** Instructions target the wrong distribution. **Fix:** Check distribution identity before following distribution-specific steps.
- **Mistake:** Treating `VERSION_ID` as the kernel release. **Symptom:** A report mixes two unrelated version numbers. **Fix:** Label distribution and kernel results separately.
- **Mistake:** Expecting every field in this example. **Symptom:** An optional missing field looks like a failure. **Fix:** Use the fields actually provided and consult the distribution's documentation.
- **Mistake:** Combining the two release files. **Symptom:** A report can mix conflicting vendor data. **Fix:** Prefer `/etc/os-release`; use the alternative only when it is absent.

## Troubleshooting

A misspelled filename causes a read failure, not an operating-system failure. This **deliberate error example** omits the final `e` from the filename. The command still only attempts to read a file:

```bash
cat /etc/os-releas
```

Actual error output, with exit status `1` and no normal output:

```text
cat: /etc/os-releas: No such file or directory
```

Compare the path with the documented `/etc/os-release` spelling. Repeat the corrected command from step 1, which was verified successfully with the output shown there. Do not create a replacement file or add administrative privileges to fix a typo. If the correctly spelled file is genuinely absent, use the fallback rule above.

## Interview questions

1. **Why is the kernel name insufficient for choosing Debian instructions?** Several distributions use Linux; the distribution has its own identity and release policy.
2. **Which release file takes precedence?** `/etc/os-release`. Use `/usr/lib/os-release` only when the first is absent.
3. **Does this file establish that packages are current?** No. It supplies operating-system identification data, not package or security verification.

## Key takeaways

- Read vendor-provided distribution data before using distribution-specific instructions.
- Keep distribution and kernel identities separate.
- Treat optional fields as optional, and do not merge the two release files.

## Next

**Planned:** `linux-01-03`, at `01-fundamentals/03-command-structure.md`, will explain how to read a shell command. It is not yet an implemented lesson.

## Further reading

- [Official os-release specification](https://www.freedesktop.org/software/systemd/man/latest/os-release.html): field meanings, optional values and file precedence.
- [GNU coreutils: cat](https://www.gnu.org/software/coreutils/manual/html_node/cat-invocation.html): the command used to display the file.
