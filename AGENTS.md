# Agent instructions

## Scope

You write lessons for this repo only. Follow the structure in README.md
and the template in STYLE_GUIDE.md exactly.

## Process for every lesson

1. Read ROADMAP.md and the previous lesson, so the lesson builds on them.
2. Check glossary.md; reuse existing definitions and link them.
3. Write the lesson using the template.
4. Run every command in a sandbox (Docker container or VM).
   Paste the real output. Do not write expected output from memory.
5. If a command fails, fix the lesson, do not hide the error.
6. Add any new terms to glossary.md.
7. Update ROADMAP.md and CHANGELOG.md.

## Hard rules

- Never invent CLI flags. If unsure, run `<tool> --help` and check.
- Never invent API fields or resource arguments. Check the official docs.
- Never use latest tags or unpinned versions.
- Never include real credentials, account IDs, or IPs.
- Cloud labs must include a cost estimate and a teardown step.
- If you cannot verify something, mark it `> UNVERIFIED:` and flag it for review.

## Repository-specific boundaries

- The target is the existing `Yoshik18/linux-helpbook`. Do not create repositories, an organization or a central hub as part of lesson work.
- The local [STYLE_GUIDE.md](STYLE_GUIDE.md) is the lesson contract until a shared hub is separately approved.
- Use one writer per assigned lesson file. The coordinator integrates glossary, roadmap, changelog and evidence changes to avoid overlapping edits.
- Read the prior orientation page for the first lesson. Where a planned prerequisite is missing, do not pretend it exists; stop and flag the dependency.
- Preserve useful existing material and attribution until its replacements pass review. Existing pages do not automatically count as verified course lessons.
- Each lesson covers one concept. Link glossary terms on first use, explain commands on first appearance, and cite official documentation under the final `Further reading` heading.
- Diagrams are optional. Use Mermaid only when a diagram clarifies the explanation.
- Keep course work on a review branch. No default-branch pushes, merges, force pushes, repository settings changes, scheduled jobs or paid resources without separate approval.
- Do not add or replace a license until the owner chooses one.
- Use Composio MCP for remote GitHub operations. Local CLI authentication does not establish an active Composio connection.
- Record actual versions and execution evidence per lesson. Do not label static checks, guessed outputs or earlier lessons' outputs as a newly verified lab.
- A deliberate failing example may teach troubleshooting only when it is clearly labeled, its actual error and exit status are recorded, and its safe correction is tested.
- Teardown is the last step of any cloud lab, including checking that lab resources are gone. Include budget-alert guidance and a dated cost estimate before setup.
