---
id: linux-01-01
title: Identify the Running Kernel
level: fundamentals
prerequisites: []
est_time: 20 min
tool_versions: Debian 13.7; Bash 5.2.37; GNU coreutils 9.7; Linux 6.1.158+
last_verified: "2026-10-26"
---

# Identify the Running Kernel

## What you'll learn

- Read the name and release of the running [kernel](../glossary.md#kernel).
- Identify the machine [architecture](../glossary.md#architecture) reported by that kernel.
- Combine two information requests in one command.
- Recognize and correct an ambiguous option.

## Why this matters

A bug report asks which kernel you are running. The version of an installed package might not answer that question: a newly installed kernel may not be running yet. You need information from the kernel currently serving this environment.

## Mental model

Programs rely on the running kernel to manage access to the processor, memory, and devices. The `uname` command asks for identifying information about that running system. It reports what is active now, not a list of kernels installed on disk.

Open a [terminal](../glossary.md#terminal) and enter each command at the [shell](../glossary.md#shell) prompt. The command name is `uname`. A space separates it from an [option](../glossary.md#option), which selects the information to print. The examples below request one field at a time before combining two fields.

## Hands-on

**Prerequisites and scope:** Use a disposable Linux environment you control, with GNU coreutils available. No earlier lessons are required. These commands only read system information. They need no elevated privileges, create no files or resources, and require no cleanup.

The recorded run used an isolated Composio Debian 13.7 sandbox whose virtualization detector reported KVM, with Bash 5.2.37, GNU coreutils 9.7, and Linux 6.1.158+. Outputs below come from that run, not from a requirement for your machine. See the [execution evidence](../labs/verification/linux-01-01.json) for the recorded commands and results.

1. **Read the kernel name.** The `-s` option selects the kernel name.

   ```bash
   uname -s
   ```

   ```text
   Linux
   ```

   This identifies the kernel as Linux. It does not identify the installed [distribution](../glossary.md#distribution), such as Debian.

2. **Read the kernel release.** The `-r` option selects the running kernel's release string.

   ```bash
   uname -r
   ```

   ```text
   6.1.158+
   ```

   Keep the entire string, including the `+`, when reporting this result. Your system may print a different release or suffix. The string alone does not establish whether all security fixes are present.

3. **Read the reported machine architecture.** The `-m` option selects the machine hardware name, used here to identify the [architecture](../glossary.md#architecture) reported by the running system.

   ```bash
   uname -m
   ```

   ```text
   x86_64
   ```

   This result identifies the reported architecture as 64-bit x86. Other environments can report different values. It is not the name of a processor model or a complete description of the physical host.

All three commands returned [exit status](../glossary.md#exit-status) `0`, meaning success, with no error output. Each displayed line ended with a newline. There is nothing to remove after these read-only steps.

## Verify it worked

Combine the already introduced `-s` and `-r` options as `-sr` to request the kernel name and release together. Compare the two fields with steps 1 and 2.

```bash
uname -sr
```

```text
Linux 6.1.158+
```

The recorded command returned exit status `0` with no error output. Both fields match the individual results. This confirms that the combined request reports the same kernel identity; it does not prove that the kernel is current, secure, or the newest one installed.

## Common mistakes

- **Mistake:** Treating `Linux` as the distribution name. **Symptom:** A report gives no distribution information. **Fix:** Label this value as the kernel name; distribution identification is the next lesson.
- **Mistake:** Expecting the recorded release on every machine. **Symptom:** A different release looks like a failed exercise. **Fix:** Record your actual output rather than trying to make it match this sandbox.
- **Mistake:** Dropping a release suffix. **Symptom:** A report loses part of the identifying string. **Fix:** Preserve the complete release exactly as printed.
- **Mistake:** Assuming an installed kernel is already active. **Symptom:** A package version differs from the reported release. **Fix:** Use the running release for this question; these commands do not inventory installed kernels.

## Troubleshooting

This is a **deliberate failure demonstration**. GNU tools accept some shortened long options, but the abbreviation `--kernel` does not uniquely select a field. Run this example only to observe that error:

```bash
uname --kernel
```

The command produced no normal output. Its exact error output was:

```text
uname: option '--kernel' is ambiguous; possibilities: '--kernel-name' '--kernel-release' '--kernel-version'
Try 'uname --help' for more information.
```

It returned exit status `1`. The abbreviation matches three different options, so the tool cannot choose one. This is a command syntax problem, not evidence of a damaged kernel.

To request the kernel name without ambiguity, use the already verified `-s` option:

```bash
uname -s
```

```text
Linux
```

That command succeeded with exit status `0` and no error output in the recorded run. It only reads information; the failed command made no changes to undo.

## Interview questions

1. **How do you distinguish the kernel name from its release?** The `-s` option selects the name; `-r` selects the release.
2. **Does the reported release identify every installed kernel?** No. It describes the running kernel, not an inventory of installed files.
3. **Does a successful combined check prove the system is secure?** No. It verifies identity fields, not patch coverage or configuration.

## Key takeaways

- Ask the running system for its kernel identity instead of inferring it from installed packages.
- Kernel name, release, and reported architecture are separate fields.
- Preserve the full release string in reports.
- A successful identity check is not a security assessment.

## Next

Continue to [Identify the Installed Distribution](02-distribution.md), `linux-01-02`.

## Further reading

- [GNU coreutils: uname invocation](https://www.gnu.org/software/coreutils/manual/html_node/uname-invocation.html): official command reference. Retrieval failed during this verification, so page availability was not confirmed. The installed upstream help was successfully run and confirmed the options used here.
- [Linux kernel documentation: README](https://docs.kernel.org/admin-guide/README.html): official background on the Linux kernel. This page was retrieved during verification.
