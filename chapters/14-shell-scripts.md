# 14. Small shell scripts

[Contents](../README.md) | [Previous: security](13-security.md) | [Next: ssh](15-ssh.md)

A shell script is a text file containing commands that the shell reads in sequence. Scripts are useful for repeatable tasks, but putting commands in a file does not make them safe. Understand each command, quote values, check failures and test on disposable data before using a script on important files.

## A minimal Bash script

```bash
#!/usr/bin/env bash
set -u

name=${1:-world}
printf 'Hello, %s\n' "$name"
```

The first line is a shebang: when executed directly, it asks the system to run the file with Bash found through `env`. `set -u` makes Bash report use of unset variables. `${1:-world}` uses the first positional argument or the fallback `world`. Quoting `"$name"` preserves it as one argument. `printf` writes the result.

Save this as `hello.sh`, then run it through Bash without changing permissions:

```bash
bash hello.sh 'Ada Lovelace'
```

This reads the script and prints a greeting. Passing a name containing a space shows why quotes matter. Alternatively, after confirming the path and setting its executable bit, you can run `./hello.sh`. That modifies the script's permissions; running `bash hello.sh` does not require that change.

## Check command failures

A script can stop when an essential command fails. Bash's `set -e` can help in simple scripts but has exceptions in conditionals, pipelines and functions. It is not a complete error-handling strategy. For important steps, test the condition explicitly and print an actionable error.

```bash
if ! test -r "$1"; then
  printf 'cannot read input file\n' >&2
  exit 1
fi
```

This fragment expects an argument. `test -r` checks whether the current process can read the path; `!` reverses the condition. `>&2` sends the diagnostic to standard error. `exit 1` returns a failure status. In a complete script, validate that `$1` exists before using it, for example with `${1:?usage: script FILE}`. Quoting prevents word splitting but does not validate that a path is safe or appropriate.

## Arguments and pipelines

Use `"$@"` when forwarding all positional arguments while preserving their boundaries. Do not use `$*` for this purpose. For a pipeline where an earlier stage's failure matters, Bash supports `set -o pipefail`; without it, a pipeline's status normally comes from its last command.

Scripts should avoid `eval` on data, broad globs for destructive operations, and assumptions that the current directory is a particular path. Use explicit paths, validate inputs, and print the target before a consequential change.

## Loop over arguments and use a function

This complete script reports a line count for each readable regular file supplied as an argument:

```bash
#!/usr/bin/env bash
set -u

report_file() {
  local path=$1
  if [[ ! -f "$path" || ! -r "$path" ]]; then
    printf 'not a readable regular file: %s\n' "$path" >&2
    return 1
  fi
  printf '%s: ' "$path"
  wc -l < "$path"
}

if (( $# == 0 )); then
  printf 'usage: bash count-lines.sh FILE...\n' >&2
  exit 2
fi

status=0
for path in "$@"; do
  if ! report_file "$path"; then
    status=1
  fi
done
exit "$status"
```

Save it as `count-lines.sh`. `$#` is the argument count; `(( ... ))` evaluates an arithmetic condition in Bash. `for ... in "$@"` processes each original argument without splitting names containing spaces. A function groups commands, and `local` limits `path` to that function. Bash's `[[ ... ]]` tests whether the path is a regular file (`-f`) and readable (`-r`); `||` means either condition is enough to reject it. `return` leaves the function, whereas `exit` ends the script.

For example, `bash count-lines.sh 'My Notes.txt' other.txt` reads those two files, not three words. `<` gives `wc` the file as input, and `-l` counts newline characters, so a final unterminated line is not counted. An unreadable or missing input prints a diagnostic, records a failure and allows the loop to continue. The final exit status is `1` if any input failed and `0` otherwise; no arguments produces `2`. The check is not atomic: a file can change between testing and reading, so `wc` can still fail. Its failure becomes the function's status and is recorded by the caller.

## Test without risk

Test a script with a temporary copy of input data that you own. Start with read-only behavior or a disposable directory, inspect the exact target paths, and test error cases. Do not test cleanup scripts against a real home directory, production data or a shared system. A syntax check can catch malformed Bash but cannot prove the script does what you intend.

## Common confusion

- `set -e` does not replace explicit error handling.
- `"$@"` preserves separate arguments; unquoted expansions can split or expand wildcards.
- A syntax check does not prove correctness or safety.
- The current working directory may differ when a script is launched from another location.
- Executable permission is needed for direct execution, not for `bash script.sh`.

## Further reading

- [Bash manual](https://www.gnu.org/software/bash/manual/)
- [BashFAQ: set -e](https://mywiki.wooledge.org/BashFAQ/105)
- [ShellCheck wiki](https://www.shellcheck.net/wiki/)
