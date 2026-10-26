# Linux course style guide

This file is the local lesson contract for this topic repository. A shared learning-hub style guide is not yet in scope. Follow this file and [AGENTS.md](AGENTS.md) before writing lessons.

## Reader and scope

Write for a student or junior engineer who can use a keyboard but has not administered Linux. Start with a concrete problem. Explain the mechanism before expecting the reader to interpret commands. One lesson teaches one concept; related concepts get their own lessons and prerequisite links.

Use plain language, short paragraphs, descriptive headings and consistent terms. Link each glossary term on its first use in a page. Define terms once in [glossary.md](glossary.md), not again in every lesson. Explain the concept in context without repeating a glossary entry. Do not add filler, promotional openings or arbitrary length targets. Fundamentals lessons must stay under 1,500 words.

## Lesson template

Use these metadata keys, in this order. The bracketed values below are template placeholders, not publishable values. `last_verified` is a quoted ISO date only after command execution and review; use `null` in an unfinished draft and add a visible `> UNVERIFIED:` warning. List exact verified versions, not version ranges. A null date must not pass the ready-for-review lesson gate.

```yaml
---
id: <topic-level-sequence>
title: <lesson title>
level: <fundamentals | intermediate | advanced>
prerequisites: []
est_time: <minutes> min
tool_versions: <exact verified environment and tool versions>
last_verified: null
---
```

Use a single H1 title matching `title`, followed by these H2 sections in this exact order:

1. **What you'll learn**: three to five concrete outcomes about the single concept.
2. **Why this matters**: one short paragraph starting with a practical problem.
3. **Mental model**: explain how the concept works. Use an analogy only when it helps. A diagram is optional; use Mermaid if a diagram clarifies relationships better than prose.
4. **Hands-on**: numbered steps in a disposable environment, with explanation before each command and its real output immediately after. State prerequisites, effects, privilege needs and normal variation.
5. **Verify it worked**: an explained check, its real output and the limits of what it proves.
6. **Common mistakes**: three to five mistake, symptom and fix entries.
7. **Troubleshooting**: an actually observed error, its cause and a safe fix. Record intentionally failing demonstrations as such, with their real exit status. An unexpected failure must be fixed and rerun, not hidden.
8. **Interview questions**: two to four questions with short answers.
9. **Key takeaways**: three to five useful points.
10. **Next**: link the next implemented lesson. If it is not implemented, give its roadmap ID and path as plain code, explicitly marked planned. Do not create a dead link.
11. **Further reading**: official project, distribution or upstream documentation. This must be the final section.

## Command rules

- Explain a command on first appearance, including each option and any quoting, expansion, redirection or other shell syntax it needs. Do not introduce pipelines merely to shorten version output.
- Show only the command the reader types in a `bash` fence. Put observed output in a separate `text` fence. Do not include a prompt that readers might copy.
- Run every example, including verification and error examples, in an isolated Docker container or VM. Record environment, tool versions, date, exact command, stdout, stderr and exit status in a lesson-specific evidence file under `labs/verification/`.
- Never reconstruct output or replace machine-dependent values with invented ones. Explain variation outside the output. Avoid examples that expose private identifiers in the first place. If redaction is essential, label it and preserve no secret in evidence.
- Pin image digests and exact tool versions when provisioning. Do not use floating tags, `latest` tags, unpinned downloads or guessed flags. Existing verification-environment versions are observations, not an installation lockfile.
- Use upstream documentation and the installed tool's help to resolve syntax. Never invent API fields or resource arguments.
- Prefer read-only inspection for beginner lessons. Explain all changes and their targets before state-changing commands. Never run a lesson against production, personal data or work accounts.
- Mark every unverified instruction or behavior `> UNVERIFIED:` and flag it for review. Syntax checking is not execution. Installing a service client is not proof that a service manager runs.

## Labs, costs and cleanup

Every lab states its environment, prerequisites, scope, verification and cleanup. A read-only local lab must explicitly say that it creates no files or resources and requires no cleanup.

Every cloud lab starts with a cost warning and an estimated amount or range, currency, region, assumed duration, pricing source and date. Identify additional cost drivers such as disks, addresses and data transfer. Use a sandbox account with budget alerts; alerts are not spending caps. No paid resources may be created by the agent without explicit approval.

Teardown is the final lab step. Explain and test `terraform destroy` or the equivalent for the actual tool, then verify the lab resources are gone as part of that step. Do not add resource-creating checks after cleanup. A lab is not verified until teardown has been exercised.

## Navigation and maintenance

- Paths use lowercase kebab-case and numeric reading-order prefixes.
- [ROADMAP.md](ROADMAP.md) lists full relative lesson paths, levels, estimated hours and prerequisites. Estimates describe learner time, not measured execution time. Planned and implemented content must be visibly distinct.
- Glossary entries use one `### Term` heading per term with stable links. Link only existing files and headings.
- Cheatsheets are one page each, with a table of command, what it does and one example. They are lookup aids, not lessons.
- Update the roadmap and [CHANGELOG.md](CHANGELOG.md) for every verified lesson. Record its last verified date, exact versions, evidence and limitations.
- Re-verification should happen every three to six months and after relevant tool changes. This is a maintenance policy, not an activated scheduled job.
- Preserve useful existing content and attribution until reviewed replacements are complete. Do not add a license without the owner's choice. Do not merge or push to the default branch.
