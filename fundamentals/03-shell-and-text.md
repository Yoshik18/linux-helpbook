# 3. Search logs and build useful pipelines

Use the [practice files](01-how-linux-works.md). The log formats below are small,
fictional fixtures, not a parser for arbitrary application logs or CSV.

## Find an error and keep its line number

```bash
grep -n 'ERROR' "$LINUX_LAB/logs/app.log"
grep -in 'error' "$LINUX_LAB/logs/app.log"
grep -n -C 1 'db refused' "$LINUX_LAB/logs/app.log"
grep -v '^INFO' "$LINUX_LAB/logs/app.log"
```

`-n` prints line numbers, `-i` ignores case, `-C 1` includes one context line on
either side and `-v` excludes matches. Expect ERROR lines 2, 4 and 5. Use `-F`
for literal text containing characters you do not want interpreted as a regex.

## Count repeated errors

```bash
grep '^ERROR ' "$LINUX_LAB/logs/app.log" | sort | uniq -c | sort -nr
```

Read left to right: select errors, group equal lines, count adjacent duplicates,
then sort counts numerically in reverse order. Expect `ERROR api timeout` twice
and `ERROR db refused` once. `uniq` alone does not combine separated duplicates.

## Select fields and filter by a value

```bash
awk '$4 >= 500 {print $1, $3, $4}' "$LINUX_LAB/logs/access.log"
awk '$4 >= 500 {count++} END {print count+0}' "$LINUX_LAB/logs/access.log"
cut -d, -f1,3 "$LINUX_LAB/data/report.csv"
awk -F, 'NR > 1 && $2 == "prod" {total += $3} END {print total+0}' "$LINUX_LAB/data/report.csv"
```

The access fixture is whitespace-separated: client, method, path, status,
duration. There are two 500 responses. `-F,` changes awk's field separator; `NR
> 1` skips the CSV header. The production request total is `165`. These tools
are not a full CSV parser when quoted fields can contain commas or newlines.

## Preview a text change before overwriting anything

```bash
sed 's/environment=staging/environment=production/' "$LINUX_LAB/config/app.conf"
sed 's/environment=staging/environment=production/' "$LINUX_LAB/config/app.conf" > "$LINUX_LAB/config/app.preview"
diff -u "$LINUX_LAB/config/app.conf" "$LINUX_LAB/config/app.preview"
```

`sed` prints a transformed copy by default. `diff -u` shows the changed line;
status 1 means files differ, not that diff failed. Do not redirect a filter's
output to its own input file: the shell may truncate the input before reading it.

## Quote paths, and separate results from diagnostics

```bash
file="$LINUX_LAB/notes/file with spaces.txt"
cat "$file"
grep ERROR "$LINUX_LAB/logs/app.log" > "$LINUX_LAB/errors.txt"
grep ERROR "$LINUX_LAB/missing.log" 2> "$LINUX_LAB/read-errors.txt"
printf 'grep exit status: %s\n' "$?"
cat "$LINUX_LAB/read-errors.txt"
```

Quoted `"$file"` stays one argument. `>` captures stdout; `2>` captures stderr.
GNU grep returns 0 for a match, 1 for no match and usually 2 for an error. Capture
`$?` before another command changes it. Run deliberate-failure examples outside
blanket `set -e` handling. [Practice lab 1](13-practice-labs.md) compares pipeline
statuses with and without `pipefail`.

## Practice

Print the two most frequent client IPs in the access fixture. Extract only the
ERROR lines, without changing the original log.

<details>
<summary>One answer</summary>

```bash
awk '{print $1}' "$LINUX_LAB/logs/access.log" | sort | uniq -c | sort -k1,1nr -k2,2 | head -n 2
grep '^ERROR ' "$LINUX_LAB/logs/app.log" > "$LINUX_LAB/error-only.log"
```

The top clients are documentation addresses `192.0.2.10` and `192.0.2.11`, each
with two requests. They are invented fixture data, not real traffic.

</details>

[Manual: grep](https://man7.org/linux/man-pages/man1/grep.1.html)
· [awk](https://man7.org/linux/man-pages/man1/awk.1p.html)
· [Bash pipelines and quoting](https://man7.org/linux/man-pages/man1/bash.1.html)
· [More Bash examples](../shell-scripting/scripting.md)
· [Previous](02-filesystem-and-paths.md) · [Index](README.md) · [Next](04-users-and-access.md)
