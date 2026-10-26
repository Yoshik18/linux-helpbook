# 3. Shell and text

[Previous: filesystem and paths](02-filesystem-and-paths.md) · [Index](README.md) · [Next: users and access](04-users-and-access.md)

The shell turns command text into arguments, connections, and processes. Learning what it changes before a program starts prevents errors that look like broken tools but are really argument or redirection mistakes. Examples here use Bash, not arbitrary `sh` implementations.

## Arguments are not just visible words

Single quotes preserve literal text. Double quotes permit parameter expansion such as `$name` and command substitution such as `$(command)`, while preventing ordinary word splitting and filename expansion on the result. [Bash manual](https://man7.org/linux/man-pages/man1/bash.1.html) Prefer `printf '%s\n' "$name"` when printing a variable: the fixed format string separates data from formatting instructions.

Unquoted variable expansions in ordinary command arguments can split into several words and then expand wildcard characters into matching filenames. Quoting `"$file"` keeps a filename containing spaces as one argument. Conversely, `*.log` deliberately asks the shell to expand matching filenames; `'*.log'` passes a literal asterisk pattern to the program. [Bash manual](https://man7.org/linux/man-pages/man1/bash.1.html) Shell globs and `grep` regular expressions are different languages. A quoted regex reaches `grep` unchanged and is then interpreted there.

Command substitution captures standard output and strips trailing newlines. [Bash manual](https://man7.org/linux/man-pages/man1/bash.1.html) It is useful for a small value, not a general mechanism for storing arbitrary binary data. Do not build command strings from input and execute them with `eval`; keep values as arguments.

## Streams and status answer different questions

Programs conventionally receive standard input on descriptor 0, write results to standard output on 1, and diagnostics to standard error on 2. A pipe, `a | b`, connects `a`'s standard output to `b`'s standard input; it does not include standard error by default. [Bash manual](https://man7.org/linux/man-pages/man1/bash.1.html) The programs can run concurrently, and the kernel can make a writer wait if the pipe fills.

The shell sets up redirections: `< file` supplies input, `> file` creates or truncates output, `>> file` appends, and `2> file` captures diagnostics. [Bash manual](https://man7.org/linux/man-pages/man1/bash.1.html) Never redirect output back to the same input file when filtering: truncation can happen before the program reads it. Use a distinct output path.

An **exit status** is separate from printed output. Zero conventionally means success; nonzero meanings depend on the program. Bash's `$?` holds the most recent command or pipeline status, so capture it before another command overwrites it. Normally a pipeline reports the last command's status. Bash's `pipefail` option instead reports the rightmost nonzero status, or zero if all succeed. [Bash manual](https://man7.org/linux/man-pages/man1/bash.1.html) It exposes failures; it does not explain whether a nonzero status was expected.

## Lab: filter a known fixture

Prerequisites: Bash, GNU `grep`, `cut`, `sort`, and `wc`; an existing writable scratch parent. Run the complete block. `set +e` is local to the subshell so intentional failures remain observable even if your calling shell uses `errexit`. No real logs or environment dumps are used.

```bash
(
    set +e
    lab=$(mktemp -d "${TMPDIR:-/tmp}/linux-text.XXXXXX") || exit 1
    printf '%s\n' 'INFO api ready' 'ERROR worker timeout' \
        'ERROR api refused' 'INFO worker ready' > "$lab/events.txt"
    grep '^ERROR ' "$lab/events.txt" | cut -d ' ' -f 2 | sort
    grep -F 'ERROR' "$lab/events.txt" | wc -l

    for pattern in '^ERROR' '^DEBUG' '['; do
        if grep "$pattern" "$lab/events.txt" > "$lab/matches.txt" 2> "$lab/diagnostic.txt"; then
            status=0
        else
            status=$?
        fi
        printf 'pattern=%s status=%s\n' "$pattern" "$status"
    done
    cat "$lab/diagnostic.txt"

    set +o pipefail
    false | wc -l
    printf 'default pipeline status=%s\n' "$?"
    set -o pipefail
    false | wc -l
    printf 'pipefail pipeline status=%s\n' "$?"

    export HELPBOOK_MODE='practice only'
    bash -c 'printf "child value=<%s>\n" "$HELPBOOK_MODE"'
    printf 'Retained lab: %s\n' "$lab"
)
```

Expect sorted service names `api` and `worker`, then a count of two. The three patterns return 0 (match), 1 (no match), and 2 (invalid regex). GNU `grep` documents these statuses; with `-q`, a match can yield zero even if an error was detected, so this lab intentionally avoids `-q`. [grep(1)](https://man7.org/linux/man-pages/man1/grep.1.html) Diagnostic wording can vary.

Both `false | wc -l` pipelines print zero lines counted, but their statuses differ: 0 without `pipefail`, 1 with it. The child shell prints the exported practice value. Exported variables form part of a child's environment; ordinary unexported shell variables do not automatically do so. [Bash manual](https://man7.org/linux/man-pages/man1/bash.1.html) A child's changes do not update its parent's variables.

**Validation:** this lab block has not been run. It is a small text fixture, not a parser for arbitrary filenames, structured logs, or binary data. Continue with the existing [shell scripting guide](../shell-scripting/scripting.md) for functions and control flow.

## Check your understanding

1. Why can `grep` return 1 without reporting an error?
2. Why can a pipeline succeed when its first command fails?
3. What changes when you quote `"$file"`, and what does quoting not do to a regex interpreted by `grep`?
