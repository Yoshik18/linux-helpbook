# Changelog

## Unreleased: first Linux course increment

- Add a local style guide with the exact lesson template, command explanation rules, official further reading, one-concept scope, glossary links and verification gates.
- Replace the bundled topic outline with a single-concept course roadmap. Unwritten lessons remain explicitly planned.
- Add orientation pages and a heading-based glossary. Keep existing Helpbook material available until reviewed replacements are ready.
- Add lessons `linux-01-01` and `linux-01-02`, identifying the running kernel and installed distribution, with captured sandbox output. Editorial integration is under review.

## Per-lesson verification

| Lesson | Last command run | Exact baseline | Evidence | Scope |
|---|---|---|---|---|
| `linux-01-01` | 2026-10-26 | Debian 13.7; Bash 5.2.37; GNU coreutils 9.7; Linux 6.1.158+; x86_64 | [Execution record](labs/verification/linux-01-01.json) | Four successful read-only invocations and one deliberate ambiguous-option failure; editorial review pending |
| `linux-01-02` | 2026-10-26 | Debian 13.7; Bash 5.2.37; GNU coreutils 9.7 | [Execution record](labs/verification/linux-01-02.json) | Read both distribution-identification files, repeated the primary read, demonstrated a misspelled path and verified its correction; editorial review pending |

The sandbox's virtualization probe reported KVM. The provider provisioned the sandbox; VM creation and deletion were not exercised. No cloud resources, state-changing commands, service management, package changes or boot recovery were tested. No claim is made that the whole course is complete or that the existing material has been reverified under this contract.

Review completed lessons every three to six months and after relevant tool changes. Set `last_verified` only when execution and lesson review are complete. No recurring job is activated by this policy.
