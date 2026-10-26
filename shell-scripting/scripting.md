# Bash scripting: from command to reliable script

A shell script is a text file that Bash reads as commands. Bash parses syntax,
expands variables and patterns, sets up redirection/pipelines, then runs builtins
and external programs. Understanding that order explains several common bugs:
`"$file"` is passed as one argument, while unquoted `$file` may split into many.
This guide assumes Bash. Arrays and `mapfile` require Bash 4 or later.

Start with the [Linux learning path](../fundamentals/README.md) if paths, quoting,
pipes or exit statuses are unfamiliar. Use a disposable directory for file-writing
examples.

## Make a script and run it

```bash
mkdir -p "$HOME/bash-practice"
cd "$HOME/bash-practice"
printf '%s\n' '#!/usr/bin/env bash' 'printf "Hello, %s\\n" "$USER"' > hello.sh
bash -n hello.sh
bash hello.sh
```

`printf` writes the two lines to `hello.sh`; the first is a *shebang*, telling
the system which interpreter to use when executing the file directly. `bash -n`
parses the script without running its commands. `bash hello.sh` explicitly runs
it with Bash, so execute permission is not needed. This example writes only under
your home directory; choose another disposable location if preferred.

To run the script by its path, first make it executable:

```bash
chmod u+x hello.sh
./hello.sh
```

`chmod u+x` adds execute permission for the owner. `./` tells Bash to look in the
current directory; current directories are normally not in `PATH`. Direct
execution also needs a valid shebang and a filesystem that permits execution.

## Variables and quoting

Bash variables have no declared string/integer type by default. Assignment has no
spaces around `=`; expansion uses `$name` or `${name}`.

```bash
name='Ada Lovelace'
printf 'Hello, %s\n' "$name"
```

Single quotes preserve literal characters. Double quotes allow `$name`, command
substitution and some backslash escapes while keeping the result one argument.
`printf`'s format string `%s\n` prints the value and a newline. Prefer `printf`
over `echo` when exact output matters.

```bash
file="$HOME/notes with spaces.txt"
printf 'One argument: <%s>\n' "$file"
printf 'Home: %s\n' "$HOME"
printf 'Today: %s\n' "$(date +%F)"
```

`$(...)` runs a command and substitutes its standard output; Bash removes trailing
newlines from that output. Quote the substitution to keep the result one
argument. Quoting does not make arbitrary command output a safe filename or a
validated input.

```bash
printf 'one\ntwo\n' > names.txt
for file in *.txt; do
    printf 'Matched path: %s\n' "$file"
done
```

Bash expands `*.txt` before starting the loop. Each match becomes a separate
word. If no files match, default behavior leaves the literal `*.txt`; scripts
that need other behavior should choose and document `nullglob`/`failglob`. Keep
each expanded filename quoted inside the loop.

## Standard streams, pipelines and status

Commands read standard input (0), write normal output to standard output (1), and
write diagnostics to standard error (2). These are separate streams until you
redirect them.

```bash
printf '%s\n' 'started' 'ERROR timeout' > app.log
printf '%s\n' 'still running' >> app.log
grep -n 'ERROR' app.log > matches.txt
grep -n 'missing' app.log 2> search-errors.txt
```

`>` creates or truncates a file before running the command; `>>` appends.
`grep -n` prints matching line numbers. A no-match search returns status 1, which
is not the same as an I/O error (usually status 2). Capture `$?` immediately if
you need it; the next command replaces it.

```bash
if grep -q 'ERROR' app.log; then
    printf '%s\n' 'at least one error'
else
    status=$?
    if (( status == 1 )); then
        printf '%s\n' 'no matches'
    else
        printf 'grep failed with status %s\n' "$status" >&2
        exit "$status"
    fi
fi
```

`-q` suppresses matching lines; the status communicates match/no-match/error.
The `if` tests the command's status directly, so expected “no match” is handled
without pretending every nonzero status has the same meaning.

```bash
grep 'ERROR' app.log | sort | uniq -c
```

A pipe connects standard output from each command to the next command's standard
input. Here grep selects lines, sort places identical lines together, and `uniq
-c` counts adjacent repeats. Without additional handling, a pipeline's status is
the status of its last command. Bash's `set -o pipefail` instead makes the
pipeline nonzero if a command fails; decide whether that is the right policy for
your script. See [pipeline status exercise](../fundamentals/13-practice-labs.md).

## Arguments are already separate values

Use `"$@"` to pass all script arguments onward without splitting them. Avoid
unquoted `$@` and `$*` for argument forwarding.

```bash
#!/usr/bin/env bash
printf 'Received %d arguments\n' "$#"
for path in "$@"; do
    printf 'Path argument: <%s>\n' "$path"
done
```

Save the complete block as `show-args.sh`. Run it with `bash show-args.sh "file with spaces" second.txt`; it should report two arguments and print each path on one line. `bash FILE` does not require execute permission. To run `./show-args.sh` directly instead, first use `chmod u+x show-args.sh`. `$#` is the argument count, `$1` the first, and `$0` the script name.

Parse short options with `getopts`:

```bash
#!/usr/bin/env bash
usage() {
    printf 'Usage: %s [-v] -f FILE\n' "$0" >&2
}

verbose=false
input=''
while getopts ':f:vh' option; do
    case $option in
        f) input=$OPTARG ;;
        v) verbose=true ;;
        h) usage; exit 0 ;;
        :) printf 'Option -%s needs an argument\n' "$OPTARG" >&2; usage; exit 2 ;;
        \?) printf 'Unknown option: -%s\n' "$OPTARG" >&2; usage; exit 2 ;;
    esac
done
shift "$((OPTIND - 1))"

if [[ -z $input ]]; then
    usage
    exit 2
fi
printf 'Input path: %s\n' "$input"
printf 'Verbose: %s\n' "$verbose"
```

The leading `:` in `':f:vh'` makes `getopts` report a missing argument with
`:`; `f:` means `-f` requires a value, while `v` and `h` do not. `OPTARG` holds
the option value; `OPTIND` marks how many arguments were consumed. `shift` removes
those parsed options so remaining positional arguments begin at `$1`. `getopts`
handles short options, not arbitrary long-option syntax.

## Use arrays for a list of paths

A Bash array stores each value separately. This is safer than building a
space-separated string and trying to recover its boundaries later.

```bash
files=("$HOME"/*.conf)
printf 'Found %s paths\n' "${#files[@]}"
for file in "${files[@]}"; do
    [[ -e $file ]] || continue
    printf 'Config: %s\n' "$file"
done
```

`"${files[@]}"` expands to one word per array element. The `-e` test skips the
literal unmatched glob under Bash's default settings. Arrays are Bash syntax, not
portable POSIX `sh` syntax.

## Conditions and loops

Use `[[ ... ]]` for Bash string/file tests, and `(( ... ))` for integer arithmetic.
Spacing matters around `[[` and `]]`.

```bash
if [[ -r $input ]]; then
    printf '%s\n' 'Readable file'
else
    printf 'Cannot read: %s\n' "$input" >&2
fi

count=0
while (( count < 3 )); do
    printf 'Attempt %d\n' "$((count + 1))"
    ((count += 1))
done
```

`-r` tests whether the current process can read the path, not whether another
service user can. Arithmetic commands return a status based on the arithmetic
value, so a post-increment from zero can return status 1. Here `((count += 1))`
returns nonzero only if the new count is zero, which it is not. Under `set -e`,
this status behavior matters.

## Functions and scope

Functions group commands and receive arguments in `$1`, `$2`, and so on. `local`
limits a variable to a function's dynamic scope in Bash; nested functions can see
it. It does not create a completely isolated lexical scope.

```bash
log() {
    local level=$1
    shift
    printf '[%s] %s\n' "$level" "$*"
}

log INFO 'service started'
```

`shift` removes the first function argument. `"$*"` joins the remaining arguments
into one message with the first character of `IFS` between them. If the exact
argument boundaries matter, use `"$@"` instead.

A function's `return` value is an exit status from 0 to 255, not a general-purpose
string result. Print data to stdout or assign a variable when a caller needs a
larger result.

## Read a file line by line

```bash
while IFS= read -r line || [[ -n $line ]]; do
    printf 'Line: %s\n' "$line"
done < names.txt
```

`read` normally uses `IFS` to trim/split input and treats backslashes specially.
Setting `IFS=` preserves leading/trailing whitespace; `-r` disables backslash
interpretation. The final condition processes a last line even if the file lacks
its usual newline. The redirection feeds the loop without a pipeline subshell,
so variables changed in the loop remain available afterward in Bash.

## Failures and shell options

A command's status is a signal from that command, not a universal diagnosis. Handle
expected nonzero results explicitly. `set -u` makes an unset variable an error;
use `${value:-default}` when an empty/unset value should be allowed. `set -o
pipefail` changes how Bash reports a pipeline's status.

`set -e` exits on some unhandled nonzero statuses, but has context-dependent
exceptions in tests, `&&`/`||` lists, pipelines and functions used as conditions.
It is not a substitute for defining what success and failure mean. If you use it,
read the Bash manual and test the script's error paths. This guide does not add a
blanket `set -e` to every example.

```bash
if ! cp -- "$source" "$destination"; then
    printf 'Could not copy %s\n' "$source" >&2
    exit 1
fi
```

`--` ends option parsing for GNU `cp`, useful if a path begins with `-`. Quote
both variables so each remains one argument. `exit 1` reports failure to the
calling shell; choose a documented status convention for larger scripts.

## Temporary files and cleanup

Create a unique temporary file with `mktemp`; never construct a shared predictable
filename in `/tmp`. Keep the path in a variable and quote it at each use.

```bash
#!/usr/bin/env bash
tmp_file=$(mktemp) || exit 1
cleanup() {
    local status=$?
    trap - EXIT
    rm -f -- "$tmp_file" || printf 'Could not remove temporary file\n' >&2
    exit "$status"
}
trap cleanup EXIT

printf '%s\n' 'temporary data' > "$tmp_file"
wc -l < "$tmp_file"
```

The `EXIT` trap runs when the shell exits. It saves the prior status before
cleanup, disables its own trap to avoid recursion, and exits with the saved
status. Cleanup failure is reported but does not mask the original result. A
script handling sensitive data may need stronger cleanup and storage controls;
ordinary deletion does not guarantee secure erasure on modern filesystems.

## Debug before running

```bash
bash -n script.sh
bash -x script.sh
```

`bash -n` checks Bash syntax without running the commands. `bash -x` prints
expanded commands as Bash executes them, which can expose secrets; do not enable
it blindly on credential-handling scripts. [ShellCheck](https://www.shellcheck.net/)
can identify many shell mistakes, but passing it does not prove correctness or safety.

## Small complete example

This script takes a file path, counts lines, and fails clearly when the argument
is missing or unreadable. Save as `line-count.sh` in a practice directory:

```bash
#!/usr/bin/env bash
set -u

if (( $# != 1 )); then
    printf 'Usage: %s FILE\n' "$0" >&2
    exit 2
fi

file=$1
if [[ ! -r $file ]]; then
    printf 'Not readable: %s\n' "$file" >&2
    exit 1
fi

lines=$(wc -l < "$file") || {
    printf 'Could not count lines: %s\n' "$file" >&2
    exit 1
}
printf '%s: %s lines\n' "$file" "$lines"
```

`$#` checks the number of arguments; `$1` is assigned only after that check.
`wc -l < "$file"` counts newline characters and avoids printing the filename as
a second column. A final unterminated line is not counted by `wc -l`, so text files
should normally end with a newline. `$(...)` captures the count for `printf`.
`set -u` catches accidental use of unset variables; explicit checks handle expected
input errors.

## Further reading

- [Bash Reference Manual](https://www.gnu.org/software/bash/manual/bash.html)
- [Bash pitfalls](https://mywiki.wooledge.org/BashPitfalls)
- [ShellCheck](https://www.shellcheck.net/)
- [Linux text and pipeline examples](../fundamentals/03-shell-and-text.md)

[Back to the Linux Helpbook](../README.md)
