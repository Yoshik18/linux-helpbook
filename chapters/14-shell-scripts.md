# 14. Small shell scripts

[Contents](../README.md) | [Previous: security](13-security.md) | [Next: ssh](15-ssh.md)

Suppose you keep several text files and want to check how much is in each one. You can type a counting command repeatedly, but sooner or later you will mistype a name or forget which files you checked. You can instead put the steps in a file and ask Bash to run them.

That file is a **shell script**. It contains the same kinds of commands you type at a terminal, together with instructions about which commands to run, when to repeat them, and what to do if something fails. Saving commands does not make them safer. It makes their behavior easier to repeat, including their mistakes.

We will start with a file that prints a greeting, then build a script that reports newline counts for files you name. The finished script reads the named files without rewriting them. It handles spaces in names, rejects directories, explains missing inputs, and reports failure without abandoning every remaining file.

## In this chapter

- [Put a command in a file](#put-a-command-in-a-file)
- [Give the greeting an argument](#give-the-greeting-an-argument)
- [Prepare a small counting example](#prepare-a-small-counting-example)
- [Find out whether a command succeeded](#find-out-whether-a-command-succeeded)
- [Write a report for one file](#write-a-report-for-one-file)
- [Repeat the report for several files](#repeat-the-report-for-several-files)
- [Read the finished script from top to bottom](#read-the-finished-script-from-top-to-bottom)
- [Try good and bad inputs](#try-good-and-bad-inputs)
- [Understand the limits of automatic stopping](#understand-the-limits-of-automatic-stopping)
- [Check scripts without trusting them blindly](#check-scripts-without-trusting-them-blindly)
- [Further reading](#further-reading)

## Put a command in a file

Use a new practice directory that you own, not a directory containing important documents. Create one with a generated name, enter it only if creation succeeded, and check the location:

```bash
script_work=$(mktemp -d "$HOME/script-notes.XXXXXX") && cd "$script_work" && pwd
```

`mktemp -d` creates a new directory, replacing the final six `X` characters with a generated ending. `$(...)` captures its path into `script_work`; `$HOME` chooses your home directory. The double quotes keep that path together. Each `&&` runs the next command only after success. If setup reports an error, stop before creating any script. Keep this shell open if you want to use the saved path later.

All the script files and small example files in this chapter belong there. Creating these examples changes that directory; running the finished report does not change the contents of its inputs. No administrator access is needed.

In your text editor, create `hello-first.sh` with exactly these contents:

```bash
#!/usr/bin/env bash
printf 'Hello, world!\n'
```

Save it as plain text. The `.sh` ending helps people recognize a shell script, but Bash does not require that ending.

There are only two lines to understand:

- `#!/usr/bin/env bash` selects the program for direct execution. The opening `#!`, often called a **shebang**, tells the system that this file needs an interpreter, a program that reads and runs its instructions. `/usr/bin/env` finds `bash` using the command-search directories in `PATH`. This assumes that `env` is available at that path and that the Bash found there is one you trust.
- `printf` writes text. The single quotes keep the enclosed text literal while Bash reads it. `printf` then interprets `\n` as a newline, which moves the next output to a new line. The exclamation mark is ordinary text inside these quotes.

From the directory containing the file, run:

```bash
bash hello-first.sh
```

Output:

```text
Hello, world!
```

Here `bash` is the program you start and `hello-first.sh` is the file it reads. This invocation selects Bash explicitly, so it does not rely on the shebang to choose an interpreter. The first line is still useful when someone later runs the file directly.

Use `bash`, not `sh`, for this chapter. Some later syntax belongs to Bash and is not supported by every shell that might be installed as `sh`.

## Give the greeting an argument

A script becomes more useful when the person running it can supply information. Words supplied after the script name are its **arguments**. Replace the simple greeting with this version, saved as `hello.sh`:

```bash
#!/usr/bin/env bash
set -u

name=${1:-world}
printf 'Hello, %s!\n' "$name"
```

Run it without an argument:

```bash
bash hello.sh
```

```text
Hello, world!
```

Then supply a name:

```bash
bash hello.sh 'Ada Lovelace'
```

```text
Hello, Ada Lovelace!
```

The quotes around `'Ada Lovelace'` make the two words one argument. The shell removes these quotes before passing the value to the script. The value contains a space, not quote marks.

### Store a value, then use it

`name=...` stores a value under the name `name`. This is a **variable**: a named value the script can use later. Do not add spaces around the assignment's `=`. `name = ...` would mean something different: Bash would try to run a command named `name`.

`$1` means the first argument. Bash provides numbered values such as `$1` and `$2` for the first and second arguments. The full expression `${1:-world}` means “use the first argument if it is set and not empty; otherwise use `world`.” The braces mark the extent of this expression, and `:-` introduces the fallback. Neither the braces nor `:-` become part of the stored name.

An explicitly empty argument also selects the fallback:

```bash
bash hello.sh ''
```

```text
Hello, world!
```

`''` passes one argument containing no characters. That is not the same as passing no arguments, even though this particular fallback deliberately handles both cases the same way.

In the output line, `"$name"` substitutes the stored value while keeping it one argument. Double quotes allow the `$name` substitution but prevent the resulting space from splitting the value. Single quotes around `'$name'` would instead print the literal characters `$name`.

The first argument to `printf`, `'Hello, %s!\n'`, is a **format** describing the output. `%s` is a slot for a string, filled here by `"$name"`. Keep the format under your control and pass user-provided text as a separate value. Do not turn a name into the format itself: a name containing `%` should remain a name, not become printing instructions.

### Catch an unset variable without rejecting a valid default

`set -u` asks Bash to treat many attempts to use an unset variable as errors. For example, a script containing these lines fails if run without arguments:

```bash
set -u
printf '%s\n' "$1"
```

Saved as `unset.sh` and run with `bash unset.sh`, it produced:

```text
unset.sh: line 2: $1: unbound variable
```

Bash ended that run with status `1`. The wording and line number can differ if you change the file. The greeting avoids this error by using the explicit fallback `${1:-world}`.

`set -u` is useful for catching mistakes such as a misspelled variable name. It does not check whether a file exists, whether an argument is sensible, or whether a command succeeds. We still need to make those decisions ourselves.

## Prepare a small counting example

In the practice directory, create two text files and one directory:

```bash
printf 'buy bread\nread notes\n' > 'My Notes.txt'
printf 'one\ntwo' > unfinished.txt
mkdir reports
```

`>` sends a command's normal output into a file instead of displaying it. It creates the file if necessary and **overwrites it if it already exists**. That is why these names belong in a new practice directory. `mkdir reports` creates a directory named `reports`; it will complain if that name already exists. These setup commands normally produce no output.

The first file contains two lines, each ending with a newline. The second contains `one`, a newline, and then `two` without a final newline. We intentionally made them different.

Before scripting a command, understand what it does on its own:

```bash
wc -l < 'My Notes.txt'
```

```text
2
```

`wc` counts parts of its input. The option `-l`, a lowercase letter L, asks for the number of newline characters. `<` opens the named file as the command's input. Unlike `>`, it does not overwrite the file. With input supplied this way, `wc` prints the count without adding a filename.

Now try:

```bash
wc -l < unfinished.txt
```

```text
1
```

There are two pieces of visible text, but only one newline character. `wc -l` counts newlines, not “every visible row including an unfinished last row.” Our report will say `newline(s)` so its label matches the measurement. The counts shown here were observed with GNU `wc` and these exact file contents.

Passing the file through `<` also means its name is not an option to `wc`. A name beginning with `-` does not become a `wc` flag in this arrangement. Quoting the path is still necessary to preserve spaces and other special characters.

## Find out whether a command succeeded

A command gives the shell a small numeric result when it finishes. This **exit status** is separate from the text it prints. Status `0` means success; a nonzero status means failure or another condition defined by that command. Different commands use different nonzero values.

Bash keeps the most recent status in `$?`. Try this harmless failure:

```bash
false
printf 'status: %s\n' "$?"
```

```text
status: 1
```

`false` is a command whose job is to return an unsuccessful status. It does not print an error or change files. This illustrates why absence of error text does not prove success.

Check `$?` immediately. Even another successful `printf` replaces it with a new status. When a script must make a decision, it is usually clearer to place the important command directly inside an `if` test rather than run other commands and hope `$?` still refers to the right one.

We will use three statuses for our own script:

- `0`: every requested file was reported successfully.
- `1`: at least one requested file could not be reported.
- `2`: the caller did not supply the required arguments.

These are choices for this script, not a universal meaning of `1` and `2` in every Linux program.

## Write a report for one file

Save the following complete script as `count-one.sh`. It checks the argument before using it, then checks the file before trying to count it:

```bash
#!/usr/bin/env bash
set -u

if (( $# != 1 )); then
  printf 'usage: bash count-one.sh FILE\n' >&2
  exit 2
fi

path=$1
if [[ ! -f "$path" ]]; then
  printf 'not a regular file: %s\n' "$path" >&2
  exit 1
fi
if [[ ! -r "$path" ]]; then
  printf 'not readable: %s\n' "$path" >&2
  exit 1
fi

if lines=$(wc -l < "$path"); then
  printf '%s: %s newline(s)\n' "$path" "$lines"
else
  printf 'could not count lines: %s\n' "$path" >&2
  exit 1
fi
```

### Decide whether to continue

An `if` statement runs a test and selects commands based on its status. `then` begins the commands for a successful test. `else`, when present, begins the commands for an unsuccessful test. `fi` ends the statement: it is `if` spelled backward. The semicolon before `then` separates it from the preceding test on the same line. It could instead be placed on a new line.

`$#` is the number of arguments. Inside Bash's `(( ... ))`, the contents are interpreted as arithmetic. `!=` means “not equal.” Thus `(( $# != 1 ))` succeeds when the argument count is anything other than one. An arithmetic test succeeds when its expression has a nonzero value; the test's resulting shell status is then `0`. It is important not to confuse the arithmetic value with the shell status.

On a wrong argument count, the script prints a usage message and runs `exit 2`. `exit` ends the whole script with the supplied status. `FILE` in the message is a placeholder for a filename, not a word the reader should type literally.

The unusual-looking `>&2` sends that message to **standard error**, the output channel used for diagnostics. Ordinary `printf` output goes to **standard output**, the channel used for results. A terminal normally displays both, but another program can collect them separately. Keeping diagnostics separate prevents an error message from pretending to be a valid report.

Only after the argument check does `path=$1` store the first argument. This order matters: with no arguments, bare `$1` would cause an unset-value error under `set -u` before we could explain the usage.

### Test the kind of input

`[[ ... ]]` is Bash's conditional-test syntax. It needs spaces after `[[` and before `]]`.

- `-f "$path"` succeeds if the path resolves to a regular file, such as a text document, rather than a directory or device. It can also succeed for a symbolic link pointing to a regular file.
- `-r "$path"` tests whether the file is readable by the current process.
- `!` reverses a test. Therefore `! -f "$path"` succeeds when the regular-file check fails, which is when we want to print an error.

The first failed check ends the single-file script. A directory named `reports` is not a regular file. A missing path also fails `-f`; the message deliberately covers both cases.

These checks explain likely problems, but they are not a promise that a subsequent read will succeed. Permissions or file contents can change, a file can disappear, or a storage device can fail between the check and the read.

### Capture output and handle the actual read failure

`$( ... )` runs the command inside it and substitutes its standard output. This is called **command substitution**. In `lines=$(wc -l < "$path")`, Bash stores the count in `lines` instead of displaying it immediately. The substitution removes trailing newline characters from the captured output, so the value is `2`, not `2` followed by a newline.

An assignment containing this substitution has the status of the substituted command. That is why it can appear directly after `if`: success means we have a count to print; failure goes to `else`. A failure to open the file for `<` also takes the failure branch. Any diagnostic from Bash or `wc` still goes to standard error; it is not captured into `lines`.

Only after a successful count do we print the report. We do not print a filename and then hope that `wc` finishes the rest of the line. That avoids leaving a half-written result when the count fails. The two `%s` slots receive the path and the count, in that order.

Try the successful case:

```bash
bash count-one.sh 'My Notes.txt'
```

```text
My Notes.txt: 2 newline(s)
```

With no argument:

```bash
bash count-one.sh
```

Diagnostic on standard error, with script status `2`:

```text
usage: bash count-one.sh FILE
```

With a missing name:

```bash
bash count-one.sh missing.txt
```

Diagnostic, with status `1`:

```text
not a regular file: missing.txt
```

`bash count-one.sh reports` likewise returns `1` and prints `not a regular file: reports`. The script reports the problem rather than trying to count a directory as text. Supplying two files returns the usage message and status `2`: this version intentionally accepts exactly one.

## Repeat the report for several files

The next change is organizational, not a new counting method. We will put the single-file work inside a named group of commands, then repeat that group for every supplied argument.

A named group is a **function**. `report_file() { ... }` defines one called `report_file`. The empty parentheses are part of the definition syntax. The braces enclose its commands; they do not execute the function immediately. Later, `report_file "$path"` calls it like a command.

A function has its own numbered arguments during a call. Inside `report_file`, `$1` means the first argument to the function, not necessarily the first argument originally passed to the script. `local path=$1` stores that value in a variable belonging to this function call. `local lines` declares another function-local variable. We only read `lines` after the counting assignment has succeeded.

`return 1` leaves the function with status `1`, allowing the rest of the script to decide what to do. This differs from `exit 1`, which would end the entire script on the first bad file.

### Preserve the caller's argument boundaries

`"$@"` expands to all the supplied arguments, preserving each one separately. If the caller supplies `'My Notes.txt' unfinished.txt`, it represents two arguments: `My Notes.txt` and `unfinished.txt`.

The double quotes are essential. Unquoted `$@` can split values into words and expand filename patterns such as `*`. `"$*"` is not a replacement: it joins the arguments into a single argument, using the first character of Bash's `IFS` separator setting between them, a space with the usual setting. For forwarding a list of separate filenames, use `"$@"`.

Our loop will be:

```bash
for path in "$@"; do
  if report_file "$path"; then
    :
  else
    status=1
  fi
done
```

`for` takes each supplied value in turn, stores it in `path`, and runs the commands between `do` and `done`. With two arguments, the body runs twice. With no arguments, it would not run at all, which is why the complete script checks for that case first.

The `if` tests the function's status. `:` is Bash's do-nothing command; it succeeds without output. On success, no extra work is needed. On failure, `status=1` remembers that something went wrong, and the loop continues. We initialize `status=0` before the loop and never reset it to `0` inside the loop. A good final file must not erase an earlier failure.

## Read the finished script from top to bottom

Save this complete version as `count-lines.sh`:

```bash
#!/usr/bin/env bash
set -u

report_file() {
  local path=$1
  local lines

  if [[ ! -f "$path" || ! -r "$path" ]]; then
    printf 'not a readable regular file: %s\n' "$path" >&2
    return 1
  fi

  if lines=$(wc -l < "$path"); then
    printf '%s: %s newline(s)\n' "$path" "$lines"
  else
    printf 'could not count lines: %s\n' "$path" >&2
    return 1
  fi
}

if (( $# == 0 )); then
  printf 'usage: bash count-lines.sh FILE...\n' >&2
  exit 2
fi

status=0
for path in "$@"; do
  if report_file "$path"; then
    :
  else
    status=1
  fi
done
exit "$status"
```

Two small pieces of syntax changed from the previous version:

- `||` inside `[[ ... ]]` means “or.” Reject the path if it is **not** a regular file **or** it is **not** readable. We combine the two checks into one diagnostic.
- `==` inside the arithmetic test means “equal.” We now reject exactly zero arguments, rather than rejecting everything except one. `FILE...` in the usage message means one or more file arguments; the dots are explanatory text, not shell syntax.

Bash first defines `report_file`, then checks the argument count, then starts the loop. On a successful function call, its last executed command is the result-printing `printf`, so that command supplies its success status. If even that output operation fails, the caller can record the nonzero status too. Explicit `return 1` handles the known input and counting failures.

After all arguments have been attempted, `exit "$status"` returns the remembered overall outcome. Nothing in this script deletes files, changes their contents, or requires `sudo`. It still reads the files you name, so do not treat the output as safe to publish if the names themselves are private.

## Try good and bad inputs

These outputs were observed with the supplied small files on Linux using Bash and GNU utilities. They are not invented reports of files on your machine.

First, keep the name containing a space intact:

```bash
bash count-lines.sh 'My Notes.txt' unfinished.txt
```

Standard output, with status `0`:

```text
My Notes.txt: 2 newline(s)
unfinished.txt: 1 newline(s)
```

Now ask for a good file, a missing file, a directory, and another good file:

```bash
bash count-lines.sh 'My Notes.txt' missing.txt reports unfinished.txt
```

Standard output:

```text
My Notes.txt: 2 newline(s)
unfinished.txt: 1 newline(s)
```

Standard error:

```text
not a readable regular file: missing.txt
not a readable regular file: reports
```

The script's status is `1`. It reached `unfinished.txt` despite the two earlier errors. The streams are shown separately because a terminal or output collector can display their interleaving differently.

With no arguments:

```bash
bash count-lines.sh
```

Standard error, with status `2`:

```text
usage: bash count-lines.sh FILE...
```

To see a failure status directly in your terminal:

```bash
bash count-lines.sh missing.txt
printf 'status: %s\n' "$?"
```

The diagnostic is `not a readable regular file: missing.txt`, and the following `printf` prints `status: 1`. That `printf` itself usually succeeds, so the two-command sequence ends with its own status `0`, not the script's earlier status `1`. This is another reason to distinguish printed status values from the final status of a longer command sequence.

### Make a quoting mistake, then correct it

If you omit the caller's quotes:

```bash
bash count-lines.sh My Notes.txt
```

The diagnostic is:

```text
not a readable regular file: My
not a readable regular file: Notes.txt
```

The script received two names. Its careful use of `"$@"` cannot reconstruct a space that the calling shell already treated as an argument separator. Correct the invocation by quoting `'My Notes.txt'`, as in the successful example.

Names beginning with a dash are also worth checking. Create one only in the practice directory:

```bash
printf 'keep\n' > ./-draft.txt
bash count-lines.sh ./-draft.txt
```

```text
./-draft.txt: 1 newline(s)
```

`./` means the current directory. It makes the path's role clear. The report's use of input redirection keeps the filename away from `wc`'s option parser. This does not establish a general rule that every command accepts dash-leading names safely: other commands may need an explicit `--` end-of-options marker or a path beginning with `./`.

### Know what the checks cannot guarantee

`-r` checks access for the process actually running the script. A privileged account may be able to read files that an ordinary account cannot, so removing read permission is not a reliable unreadability test when running as root. Do not use root merely to make an example succeed.

The files can also change after the tests. The explicit `if lines=$(...)` handles a failing read or counting command rather than assuming the earlier checks were sufficient. If that operation fails, the function prints its `could not count lines` diagnostic and returns failure. It does not print an empty count as though the operation succeeded. The script deliberately translates such failures into its own overall status `1`; it does not promise to preserve every individual command's original failure code.

This report is for ordinary files whose names you can read as text. A filename containing a newline can make its output span several lines. A very large file can take time to read. A changing file is not a stable snapshot. Those limitations matter before turning a small personal report into a tool used by other programs.

## Understand the limits of automatic stopping

You will often see scripts begin with `set -e` or `set -euo pipefail`. The latter combines `-e`, `-u`, and `-o pipefail` in one command. We have used `-u`; the other two are explained below. These settings can help expose mistakes, but they are not a substitute for deciding what a failure means.

Our script deliberately does not use `set -e`. A missing input is something we want to report and remember while continuing with the next file. Essential operations have explicit checks.

### A pipeline can hide an earlier failure

A **pipeline**, written with `|`, sends one command's standard output into another command's standard input. By default, Bash reports the pipeline status using the final command's status.

Save this small, harmless example as `pipeline-default.sh`:

```bash
false | true
printf 'pipeline status: %s\n' "$?"
```

`true` is the counterpart of `false`: it does nothing and returns success. Neither command needs any input. Run `bash pipeline-default.sh`:

```text
pipeline status: 0
```

The first command failed, but the final command succeeded. Now save this version as `pipeline-checked.sh`:

```bash
set -o pipefail
false | true
printf 'pipeline status: %s\n' "$?"
```

`set -o` enables the named Bash option, here `pipefail`. Running `bash pipeline-checked.sh` produces:

```text
pipeline status: 1
```

With `pipefail`, a pipeline succeeds only when all its commands succeed. If several fail, its status is the rightmost nonzero status, not a complete list of the failures. `pipefail` does not itself stop execution or print a diagnostic. Both demonstration scripts continue to `printf`, whose successful completion makes each script's final status `0`. What changed is the pipeline status inspected immediately afterward.

Even with `pipefail`, you need to decide whether a nonzero status is an error for your task. For example, a search command can use a nonzero status for “no matches.” A downstream command that stops reading early can also cause an upstream writer to fail. Simply enabling the option cannot explain those situations for you. Our file report has no pipeline, so it does not need this option.

### `set -e` depends on where a command runs

`set -e`, also called `errexit`, tells Bash to leave the script after certain unhandled failures. “Certain” matters. Among its exceptions are commands used as `if` conditions, commands tested with `!`, most non-final parts of `&&` or `||` lists, and non-final pipeline commands, subject to pipeline status rules. Here `&&` means “run the next command only if the preceding command succeeds”; `||` outside `[[ ... ]]` means “run the next command only if the preceding command fails.”

Functions make this less obvious. Save this as `errexit-demo.sh`:

```bash
set -e
step() {
  false
  printf 'still running\n'
}
if step; then
  printf 'the condition saw success\n'
fi
```

Running `bash errexit-demo.sh` produces:

```text
still running
the condition saw success
```

The function call is the condition of `if`. In that context, `-e` is ignored within this function call too. The failed `false` does not stop it; the successful `printf` becomes its final status. As a result, the condition sees success. A function that only worked safely because of automatic stopping can behave differently when its caller starts testing it.

That is why `report_file` checks the essential count explicitly and returns failure explicitly. This is important even without `set -e`. Similarly, writing `if ! command; then ...` can be useful, but `!` reverses the status: inspecting `$?` in that branch gives the reversed result, not the original failure code. Use an unnegated `if command; then ... else ... fi` when the original failure code is needed.

Bash also has context-dependent behavior for `-e` inside command substitutions. Do not infer that a complex group of commands inside `$(...)` must stop at its first failure. Our substitution contains just the one counting command, and its result is tested directly.

## Check scripts without trusting them blindly

Before running a changed script, ask Bash to check its syntax without executing its commands:

```bash
bash -n count-lines.sh
```

`-n` means read the commands but do not execute them. The finished script produced no output and status `0` for this check. A missing quote or missing `fi` can produce a diagnostic instead. For example, checking a file containing an unclosed single quote produced an “unexpected EOF while looking for matching” diagnostic: EOF means the end of the file arrived before the closing quote.

A syntax check cannot know that you meant a different filename, that your count label is misleading, or that an unchecked command can fail. Successful syntax is only the first check. Run the whole script against small files you own, including a name with spaces, a missing path, a directory, no arguments, and a mixture of good and bad inputs. Inspect the statuses as well as the visible text. Keep destructive operations out of a script while you are still learning its control flow.

All examples so far use `bash script.sh`, which needs permission to read the script but does not require its executable permission. If you want direct execution, first inspect the file and confirm that you are changing the practice copy, then:

```bash
chmod u+x hello.sh
./hello.sh Ada
```

`chmod` changes permissions. `u+x` adds execute permission for the file's owner without replacing the other permission bits. `./hello.sh` names the script in the current directory instead of asking Bash to search `PATH` for it. Its shebang now selects the interpreter. In the practice test this printed `Hello, Ada!`. Filesystems mounted to prohibit direct execution can still reject that invocation; using `bash hello.sh Ada` is sufficient for this chapter.

Relative input paths are resolved from the directory where the script is running, not automatically from the directory holding the script file. If you run a script by a longer path while standing elsewhere, `'My Notes.txt'` still means a file in your current directory. Use a suitable full input path when that is what you intend. Do not add a silent directory change just to hide this distinction.

Finally, quotation preserves values; it does not validate their meaning. Avoid `eval` on supplied text: it asks the shell to interpret that text as commands. Do not turn this report into a deletion script by adding a broad wildcard or an unchecked path. Read-only reporting gives you a useful result while keeping the reasoning visible: validate the input, attempt the operation, explain failure, and return a truthful status.

## Further reading

- [Bash manual](https://www.gnu.org/software/bash/manual/): shell parameters, quoting, functions, conditional constructs, redirections, and the `set` builtin.
- [BashFAQ: set -e](https://mywiki.wooledge.org/BashFAQ/105): examples showing why automatic error stopping needs care.
- [ShellCheck wiki](https://www.shellcheck.net/wiki/): explanations of common shell-script mistakes. Static analysis can find additional problems, but it does not replace executing safe test cases.
