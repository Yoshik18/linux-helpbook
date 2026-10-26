# How to use the Linux course

Copying a command is not the same as understanding its result. Read the explanation, run the example in the stated practice environment, and compare the meaning of your output rather than expecting every version string to match.

## Follow the learner path

1. Read [practice environment guidance](00-setup.md).
2. Start at the first implemented lesson in [ROADMAP.md](../ROADMAP.md). Check its prerequisites before continuing.
3. Follow [glossary](../glossary.md) links when a term is unfamiliar. Definitions live there once, rather than being repeated in each lesson.
4. Run the guided examples only in the environment the lesson describes.
5. Complete the verification check before moving to the next lesson.

The roadmap labels planned content explicitly. It is not a claim that all lessons have been written. Older Helpbook pages are preserved as reference material during migration; they do not yet meet the new course verification contract.

## Read commands and output separately

A `bash` code block contains the [command](../glossary.md#command) to type into the [shell](../glossary.md#shell). A following `text` block contains output captured from a real run. The command name, [options](../glossary.md#option) and other [arguments](../glossary.md#argument) are explained on first appearance. No prompt character needs to be copied.

Some commands write results to [standard output](../glossary.md#standard-output) and diagnostics to [standard error](../glossary.md#standard-error). Both may appear in the terminal. A command can also return an [exit status](../glossary.md#exit-status); this is not the same as its printed output.

The first lesson is read-only. Later commands may create files or change system state. Read the effects and target before running them. Do not add administrator permissions as a reflex when a command fails.

## Understand the levels

- **Fundamentals:** one concept, its mental model, explained examples and a check you can interpret. Each lesson stays under 1,500 words.
- **Intermediate:** one administration or investigation task, built on prerequisite lessons.
- **Advanced:** one deeper mechanism or failure analysis, including tradeoffs and limits.

Study-time estimates are planning suggestions, not promises. Move on when you can explain what the example establishes and what it does not.

## What verified means

A lesson's `last_verified` date records a run and review using the versions in its metadata. The changelog links its execution evidence, including commands, output and exit status. This establishes behavior in that environment, not universal behavior on every Linux system.

A syntax check only checks whether a shell can parse an example; it does not establish that the command ran successfully. A deliberately failing troubleshooting example is labeled and followed by a tested correction.

> UNVERIFIED: This label identifies an instruction or behavior that was not exercised. Treat it as a review gap, not as a working lab step.

Setup provisioning remains outside the verified scope of the first increment. Future service, storage and privileged labs need suitable disposable environments and their own evidence.

## Use references after the lesson

Each lesson ends with official documentation under `Further reading`. Use it for detail beyond the lesson's single concept. Planned cheatsheets will provide command / purpose / example tables for later lookup, not replace the explanation.

## Further reading

- [GNU Bash manual](https://www.gnu.org/software/bash/manual/)
- [GNU coreutils manual](https://www.gnu.org/software/coreutils/manual/)
