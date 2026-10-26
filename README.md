# Linux Helpbook

Learn to understand a Linux system before changing it. This course is for students and junior engineers starting from the command line, with explanations of what each command does, how to read its output and when its results are not enough.

## Start here

1. Read [practice environment guidance](00-start-here/00-setup.md). The course uses disposable environments, never production systems.
2. Read [how to use the course](00-start-here/01-how-to-use-this-repo.md).
3. Follow [ROADMAP.md](ROADMAP.md) for the lesson order, prerequisites, level and estimated study hours.
4. Use the [glossary](glossary.md) when a term is unfamiliar.

**Build status:** this is the first course increment, not a completed fundamentals-to-advanced course. Two lessons have sandbox execution evidence and are under editorial review: [Identify the Running Kernel](01-fundamentals/01-running-kernel.md) and [Identify the Installed Distribution](01-fundamentals/02-distribution.md). Remaining lessons are explicitly marked planned. VM provisioning has not been tested end to end; the commands were run in an already provisioned isolated Debian sandbox.

## Course structure

```text
README.md
ROADMAP.md
AGENTS.md
STYLE_GUIDE.md
glossary.md
00-start-here/
01-fundamentals/
02-intermediate/     planned
03-advanced/         planned
labs/
  verification/
cheatsheets/         planned
CHANGELOG.md
```

Fundamentals introduce one concept at a time. Intermediate lessons apply prerequisite concepts to a bounded task. Advanced lessons examine one deeper mechanism or failure. Planned directories are not populated with placeholder lessons just to make the tree look finished.

Each lesson follows the [style guide](STYLE_GUIDE.md): learning outcomes, why the problem matters, a mental model, explained hands-on commands with real output, verification, common mistakes, troubleshooting, interview questions, takeaways, next steps and official further reading.

Separate labs and one-page cheatsheets will follow their prerequisite lessons. No cloud lab or paid resource is required by the initial lesson. Future cloud labs must state costs and end with verified teardown.

## Verification you can inspect

[CHANGELOG.md](CHANGELOG.md) records per-lesson dates, exact tool versions, evidence and limitations. Execution evidence lives under [labs/verification](labs/verification/). A dated check proves behavior in that environment, not on every Linux installation.

Anything not exercised is marked `UNVERIFIED`. Syntax checks and link checks are reported separately from command execution. The current environment does not establish working systemd service management or a tested VM lifecycle.

## Existing Helpbook material

These pages remain available while reviewed replacements are built. They do not yet follow the new lesson template or its complete command-verification contract:

- [Existing fundamentals](fundamentals/README.md)
- [Command reference](commands/commands.md)
- [Shell scripting](shell-scripting/scripting.md)
- [Troubleshooting](troubleshooting/)
- [Vim](vim/vim.md)
- [Earlier verification scope](VERIFICATION.md)

Useful explanations, attribution and safe test tooling will be preserved during migration. Do not assume the earlier verification notes cover the new course.

## Contributing and maintenance

Read [AGENTS.md](AGENTS.md) and [STYLE_GUIDE.md](STYLE_GUIDE.md) before writing. Read the roadmap, prior lesson and glossary before each new lesson. Verify its commands in a suitable isolated environment, then update its evidence, roadmap and changelog.

Re-check lessons every three to six months and after relevant tool changes. This is a maintenance policy, not a scheduled automation. Changes go through a review branch and pull request; the owner retains merge control.

No license has been selected for this repository. This change does not add or imply a license.
