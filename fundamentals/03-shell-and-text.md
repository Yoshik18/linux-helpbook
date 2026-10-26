# 3. Run shell commands and process text

A shell is both a command launcher and a small language. Before a program runs, the shell recognizes operators such as `|` and `>`, expands variables and wildcards, and builds its argument list. Understanding that order prevents common mistakes: quote a path with spaces, and quote a search pattern when another program—not the shell—should interpret it.

## Arguments, quotes, and filename patterns

```bash
file="$LINUX_LAB/notes/file with spaces.txt"
printf 'path: %s\n' "$file"
cat "$file"
printf '%s\n' "$LINUX_LAB"/logs/*.log
```

An assignment stores text in `file`; `"$file"` expands to one argument even with spaces. Without quotes, spaces split words and wildcard characters may expand. In the last command, the quoted directory prefix stays literal while `*.log` expands to matching filenames. A quoted `'*'` would be passed literally. If there are no matches, Bash normally leaves an unmatched pattern unchanged; shell options can alter this behavior.

## Standard streams and pipelines

A process normally reads standard input (fd 0), writes normal results to standard output (fd 1), and writes diagnostics to standard error (fd 2). Redirection connects those streams to files; a pipe connects one process's output to another's input.

```bash
grep '^ERROR ' "$LINUX_LAB/logs/app.log" > "$LINUX_LAB/errors.txt"
grep ERROR "$LINUX_LAB/missing.log" 2> "$LINUX_LAB/read-errors.txt"
grep '^ERROR ' "$LINUX_LAB/logs/app.log" | wc -l
```

`>` creates or truncates the destination before the command runs; it captures stdout, not stderr. `2>` redirects diagnostics. `|` sends the left command's stdout to the right command's stdin. The final pipeline counts matching lines. Never redirect a transformation to its own input path: truncation can happen before the reader opens it.

## Exit status is evidence

```bash
grep -n 'ERROR' "$LINUX_LAB/logs/app.log"
printf 'grep status=%s\n' "$?"
grep 'NO_SUCH_TEXT' "$LINUX_LAB/logs/app.log"
printf 'no-match status=%s\n' "$?"
```

`grep -n` prints matching line numbers and text. GNU grep uses status 0 for a match, 1 for no match, and usually 2 for an error. `$?` is the immediately preceding command's status, so print it before running another command. In a pipeline, Bash normally reports the last command's status; `set -o pipefail` makes a failing earlier stage count too. See [pipeline practice](13-practice-labs.md). Deliberate failures can interrupt scripts using `set -e`.

## Search and count repeated lines

```bash
grep -n -i -C 1 'db refused' "$LINUX_LAB/logs/app.log"
grep -v '^INFO' "$LINUX_LAB/logs/app.log"
grep '^ERROR ' "$LINUX_LAB/logs/app.log" | sort | uniq -c | sort -nr
```

`-i` ignores case; `-C 1` prints one context line on each side; `-v` selects nonmatching lines. The pattern is a regular expression (`^` anchors at line start); `-F` selects literal-string matching. The pipeline selects error lines, sorts identical records together, counts adjacent duplicates, then sorts numerically in reverse order. Expect `ERROR api timeout` twice and `ERROR db refused` once. `uniq -c` alone does not combine duplicates separated by other lines.

## Select fields from structured-looking text

```bash
awk '$4 >= 500 {print $1, $3, $4}' "$LINUX_LAB/logs/access.log"
awk '$4 >= 500 {count++} END {print count+0}' "$LINUX_LAB/logs/access.log"
cut -d, -f1,3 "$LINUX_LAB/data/report.csv"
awk -F, 'NR > 1 && $2 == "prod" {total += $3} END {print total+0}' "$LINUX_LAB/data/report.csv"
```

The fixture's access records are whitespace-separated: client, method, path, status, duration. Awk's `$4` is status; the first query prints client, path, status for codes at least 500, and the next counts them (expect 2). `cut -d, -f1,3` uses comma delimiter and selects fields one and three. `awk -F,` sets the field separator; `NR > 1` skips the header and the condition selects `prod` rows. The fixture total is 165. These simple comma splits are not a full CSV parser for quoted fields containing commas or newlines.

## Preview a text transformation

```bash
sed 's/environment=staging/environment=production/' "$LINUX_LAB/config/app.conf"
sed 's/environment=staging/environment=production/' "$LINUX_LAB/config/app.conf" > "$LINUX_LAB/config/app.preview"
diff -u "$LINUX_LAB/config/app.conf" "$LINUX_LAB/config/app.preview"
```

`sed 's/old/new/'` substitutes the first match on each input line and prints the result; it does not edit the source. The second command saves that output separately. `diff -u` shows changed lines with context. Status 1 means files differ; status 0 means identical. Review output before replacing any original file.

**Try it:** Save only error lines to a separate fixture file and count them. Check output and status rather than assuming a quiet command succeeded.

```bash
grep '^ERROR ' "$LINUX_LAB/logs/app.log" > "$LINUX_LAB/error-only.log"
wc -l "$LINUX_LAB/error-only.log"
printf 'grep status=%s\n' "$?"
```

[Manual: grep](https://man7.org/linux/man-pages/man1/grep.1.html) · [awk](https://man7.org/linux/man-pages/man1/awk.1p.html) · [Bash quoting and pipelines](https://man7.org/linux/man-pages/man1/bash.1.html) · [Shell scripting](../shell-scripting/scripting.md) · [Previous](02-filesystem-and-paths.md) · [Index](README.md) · [Next](04-users-and-access.md)
