# Linux, from the command line

Learn to work with files, understand what commands do, and investigate problems before changing the system. No Linux experience is assumed. The chapters explain small examples step by step, including what the results mean and what they cannot tell you.

## Start here

- **New to Linux?** Read chapters 1–5 in order. Identify your system, learn how the shell reads commands, then practice with paths, text and permissions.
- **Ready to understand the machine?** Continue through chapters 6–11: running programs, resources, storage, networking, services and software installation.
- **Ready to put the pieces together?** Chapters 12–16 cover troubleshooting, security, small scripts, remote connections and archives.

You do not need to finish a chapter in one sitting. Follow its connected example in order; later commands may depend on files or variables created earlier. Each chapter links back here and to its neighbors. If you are returning to solve a particular problem, use the contents below and follow references back to unfamiliar concepts.

## Contents

| Chapter | What you will learn to do |
| --- | --- |
| 1. [How a Linux system fits together](chapters/01-system.md) | Identify your distribution, kernel and shell, and understand why they have different names. |
| 2. [The shell and commands](chapters/02-shell.md) | Keep filenames together with quotes, save values, and connect commands while distinguishing results from errors. |
| 3. [Files, directories and paths](chapters/03-files-and-paths.md) | Find, copy, move and link files, and check the target before removing anything. |
| 4. [Reading and searching text](chapters/04-text.md) | Narrow a small log to useful lines and build a text-processing pipeline one step at a time. |
| 5. [Users, groups and permissions](chapters/05-permissions.md) | Read access rules and explain why a readable file can still be inaccessible through its directory. |
| 6. [Processes and signals](chapters/06-processes.md) | Identify a running command, move your own work between foreground and background, and understand signals. |
| 7. [CPU, memory and load](chapters/07-resources.md) | Distinguish processor use, waiting work and memory pressure without treating one number as a diagnosis. |
| 8. [Disks and filesystems](chapters/08-storage.md) | Connect a path to its storage and investigate space usage before deciding what to remove. |
| 9. [Networking from the command line](chapters/09-networking.md) | Separate name lookup, routing, connection and application failures, starting with a local web service. |
| 10. [Boot, services and logs](chapters/10-services.md) | Distinguish a service's current state from its startup settings and read logs before considering a restart. |
| 11. [Software and packages](chapters/11-packages.md) | Find the right package tools for your distribution and distinguish searching, refreshing, installing and upgrading. |
| 12. [Troubleshooting without guessing](chapters/12-troubleshooting.md) | Reproduce a small failure, test an explanation and check what a correction actually proves. |
| 13. [Security basics](chapters/13-security.md) | Limit access, protect sensitive information and understand the limits of individual safeguards. |
| 14. [Small shell scripts](chapters/14-shell-scripts.md) | Build a Bash script that handles filenames, checks inputs and reports failures. |
| 15. [Connect to another machine with SSH](chapters/15-ssh.md) | Check a server's identity, distinguish local from remote work, and understand keys and file-copy direction. |
| 16. [Archives and compression](chapters/16-archives.md) | Distinguish grouping files from compressing them, inspect an archive and choose an extraction destination carefully. |

## Before you start

You need a Linux terminal and an ordinary user account. Examples use Bash and common GNU command-line tools unless stated otherwise; chapters identify additional tools when needed. You do not need administrator access to begin. Installation and virtual-machine setup are outside this handbook's scope.

A disposable Linux virtual machine is useful for practicing administrative changes. Windows Subsystem for Linux supports many examples, but networking, startup and service management can differ. Minimal systems and containers may lack commands used here. A missing command is not evidence that Linux is broken; check your distribution's documentation before installing anything, and only install software when authorized.

## Reading commands and output

Command blocks contain text to enter in the terminal. Output blocks contain replies to read, not more commands to run. The examples generally omit the prompt: a leading `$` in other documentation usually marks the prompt and is not something to type. Dollar signs *inside* commands, such as `$HOME`, do have meaning.

Read the explanation before copying a block. Quotes, spaces, options such as `-d`, and symbols such as `>` affect what happens; the chapters introduce them as needed. A successful command may print nothing. Compare the meaning of your result, not just its appearance: names, paths, numbers, versions and service states vary between machines.

## Practice without risking existing work

Use the chapter's new practice directory and dummy files, not important documents. Stop if directory creation fails or a path is not what you expected. Writing with `>` can empty an existing file; deletion and archive extraction can also destroy existing work. Read cleanup instructions as carefully as setup instructions.

Do not add `sudo` merely to make an error disappear. Administrative changes, package operations and remote connections require permission and the right environment. Documentation hostnames and account names are placeholders, not working login details. On a shared or production system, follow its owner's procedures rather than experimenting.

## Scope and testing

The chapters include actual tested outputs alongside explicitly labeled schematic examples and conditional walkthroughs. Local checks used small practice files and selected read-only observations; that does not mean every command or every environment was tested. Remote SSH sessions, administrative changes and live-service behavior must not be inferred to have been exercised from the presence of a command block. Container testing was not completed because the Docker daemon was unavailable.

This is an introduction to common Linux command-line work, not exhaustive tool documentation, a complete security guide or a guarantee that an example fits your machine. Use each chapter's further reading and your installed help and manual pages for version-specific details.

## Inspiration and licensing

The teaching structure draws inspiration from [Ubuntu's command-line introduction](https://ubuntu.com/desktop/docs/en/latest/tutorial/the-linux-command-line-for-beginners/), [Software Carpentry's Unix Shell lessons](https://swcarpentry.github.io/shell-novice/), and [William Shotts's Learning the Shell](https://linuxcommand.org/lc3_learning_the_shell.php): gradual explanations, connected examples and visible intermediate results. These are acknowledgments of teaching approaches, not claims that their text was copied or that their licenses cover this handbook.

The explanations and examples in this edition were written and edited for this handbook. Its existing licensing status is unchanged; this README grants no new license. Links to other works do not grant permission to reuse them.
