# 4. Reading and searching text

[Contents](../README.md) | [Previous: files and paths](03-files-and-paths.md) | [Next: permissions](05-permissions.md)

Suppose an application has stopped answering some requests. Its log contains a mixture of ordinary messages, warnings, and failures. Reading everything from beginning to end might work for a tiny file, but not for a day of activity. You need to narrow the question: which lines describe failures, which part of the application produced them, and how often does each part appear?

Linux has small commands for each of these jobs. One reads lines, another keeps matching lines, another selects a piece of each line. You can see each intermediate result before connecting the commands. That is more useful than memorizing a long command whose answer you cannot check.

This chapter uses one invented log throughout. The displayed noninteractive results were checked with the fixture shown here, using Bash and the installed Linux text utilities. Real logs will have different formats and contents. No command here needs administrator privileges.

## In this chapter

- [Make a small file you can understand completely](#make-a-small-file-you-can-understand-completely)
- [Read all of it, or just an end](#read-all-of-it-or-just-an-end)
- [Find lines containing specific text](#find-lines-containing-specific-text)
- [Choose between literal text and a pattern](#choose-between-literal-text-and-a-pattern)
- [Understand an empty result and a real error](#understand-an-empty-result-and-a-real-error)
- [Pass one command's result to another](#pass-one-commands-result-to-another)
- [Select fields, then count repeated values](#select-fields-then-count-repeated-values)
- [Select and compare fields with awk](#select-and-compare-fields-with-awk)
- [Preview an edit without changing the original](#preview-an-edit-without-changing-the-original)
- [Watch a file as new lines arrive](#watch-a-file-as-new-lines-arrive)
- [Remove the practice files](#remove-the-practice-files)
- [Further reading](#further-reading)

## Make a small file you can understand completely

A plain-text file stores readable characters, rather than a word processor's page layout. In this example, each line describes one event. A real application chooses its own format; there is no single universal Linux log layout.

Start in a directory where you keep your own practice files. Make a new directory for this example:

```bash
mkdir log-notes && cd log-notes && pwd
```

`mkdir` creates `log-notes`. The shell's `&&` means to run the next command only if the previous one succeeds. This matters: if the directory already exists, stop and choose another unused name rather than assuming it is safe to overwrite its contents. `cd` changes your current directory, and `pwd` prints that directory's full path. That path depends on where you started; it should end in `/log-notes`.

Now create the log:

```bash
cat > application.log <<'EOF'
09:00|INFO|web|request accepted
09:01|ERROR|cache.v1|connection refused
09:02|WARN|worker|queue growing
09:03|ERROR|cacheXv1|retry failed
09:04|INFO|web|request accepted
09:05|ERROR|cache.v1|retry failed
09:06|INFO|worker|job finished
09:07|ERROR|web|upstream timeout
EOF
```

Here `cat` copies the text you supply. The `>` tells the shell to put its output in `application.log` instead of on the screen. It creates the file if necessary and **empties an existing file of that name before writing**, which is why we started in a new directory.

The `<<'EOF'` part tells the shell to supply the following lines as input, stopping at a line containing just `EOF`. This is called a *here-document*. The closing `EOF` must start at the beginning of its line. Quoting the opening `'EOF'` keeps the shell from interpreting dollar signs or other substitutions inside the supplied text. You can paste the whole block; Bash may display a continuation prompt while waiting for the closing marker. A successful creation prints nothing.

Each log line has four pieces, separated by the vertical bar character, `|`:

```text
time|level|component|message
```

That is a description of the format, not another line to add. The level is the application's label for how important an event is. `INFO` marks ordinary information, `WARN` a warning, and `ERROR` a failure. The component names identify parts of this fictional application. In particular, `cache.v1` and `cacheXv1` are deliberately different names. We will use that difference to see how searches work.

The message is readable text and can contain spaces. Counting spaces would therefore not be a reliable way to find the component. Remember the actual separator chosen by the file's format.

## Read all of it, or just an end

For a short file, print the entire contents:

```bash
cat application.log
```

```text
09:00|INFO|web|request accepted
09:01|ERROR|cache.v1|connection refused
09:02|WARN|worker|queue growing
09:03|ERROR|cacheXv1|retry failed
09:04|INFO|web|request accepted
09:05|ERROR|cache.v1|retry failed
09:06|INFO|worker|job finished
09:07|ERROR|web|upstream timeout
```

Unlike the creation command, this invocation gives `cat` a filename to read and does not redirect its output. It does not change the file. What you see is eight lines in their original order. The apparent columns are not formatting supplied by `cat`; the bars are characters in the file itself.

For a large file, avoid filling the terminal with thousands of lines. `head` prints the beginning:

```bash
head -n 3 application.log
```

```text
09:00|INFO|web|request accepted
09:01|ERROR|cache.v1|connection refused
09:02|WARN|worker|queue growing
```

`-n 3` asks for three lines. `tail` uses the same option to select lines from the end:

```bash
tail -n 2 application.log
```

```text
09:06|INFO|worker|job finished
09:07|ERROR|web|upstream timeout
```

These commands leave the source unchanged. If a file has fewer lines than requested, they print what is available. A missing failure in the final two lines only means it is not in that excerpt, not that it never occurred.

When you need to move around a long file, `less` is useful if installed:

```bash
less application.log
```

It keeps the file on screen rather than printing everything and returning immediately to the shell. Press Space to move forward a screen, `b` to move back, and `q` to quit. Type `/ERROR` and press Enter to search forward, then `n` to move to the next match. The `/` starts a search within `less`; it is not a shell command. These interactive steps were not exercised in this chapter's test environment because `less` was not installed. `head` and `tail` remain available ways to read excerpts.

On a real machine you might inspect `/var/log/syslog`, but that path does not exist on every distribution. Some systems keep messages in a system journal instead; [chapter 10](10-services.md) covers that. Do not treat an absent example filename as evidence that logging is broken. Real logs can also contain usernames, request data, or secrets, so review excerpts before sharing them.

## Find lines containing specific text

`grep` reads text and prints the lines that match a search. Start by asking for lines containing the exact text `ERROR`:

```bash
grep -nF -- 'ERROR' application.log
```

```text
2:09:01|ERROR|cache.v1|connection refused
4:09:03|ERROR|cacheXv1|retry failed
6:09:05|ERROR|cache.v1|retry failed
8:09:07|ERROR|web|upstream timeout
```

The command has several parts:

- `-n` adds the original line number followed by a colon. `2:` means line two of the file, not two errors.
- `-F` asks for fixed-string matching: treat the search as literal text, not a pattern language.
- `--` ends option processing. What follows is the search text, even if it begins with a dash.
- `'ERROR'` is the search text. Bash removes these surrounding quotes before passing it to `grep`. Quoting keeps spaces and shell-special characters together when a search becomes more complicated.
- `application.log` is the file to read.

`grep` prints the whole matching line, not just the matching word. It preserves file order and does not edit or remove any lines in the file. A substring anywhere on the line is enough: this search does not know which piece represents the level. In this fixture, `ERROR` occurs only in the level field, but that is a fact about our data, not an ability supplied by `grep`.

Searches normally distinguish uppercase from lowercase. Adding `-i` ignores that difference:

```bash
grep -iF -- 'error' application.log
```

This prints the same four log lines, without the line-number prefixes because we did not request `-n`. An opposite kind of selection uses `-v`, meaning keep the lines that **do not** match:

```bash
grep -vF -- '|INFO|' application.log
```

This prints the four error lines and the warning line. The bars are part of the literal search, so a message containing the word `INFO` on its own would not be enough to exclude it. Even so, searching for separators is only a shortcut: if a message could contain `|INFO|`, the shortcut could select the wrong records. Later we will compare a particular field instead.

## Choose between literal text and a pattern

Suppose you want messages from `cache.v1`, not `cacheXv1`. With `-F`, the dot means an actual dot:

```bash
grep -F -- 'cache.v1' application.log
```

```text
09:01|ERROR|cache.v1|connection refused
09:05|ERROR|cache.v1|retry failed
```

Now try the same search without `-F`:

```bash
grep -- 'cache.v1' application.log
```

```text
09:01|ERROR|cache.v1|connection refused
09:03|ERROR|cacheXv1|retry failed
09:05|ERROR|cache.v1|retry failed
```

The extra line is not a spelling correction or a fuzzy search. Without `-F`, `grep` interprets the search as a *regular expression*: text in which some characters describe how to match rather than standing for themselves. A dot in a regular expression matches any single character within the line. Both the literal dot in `cache.v1` and the `X` in `cacheXv1` satisfy it.

The quotes do **not** turn a regular expression into a literal search. They protect the argument from Bash; `grep` still applies its own interpretation afterward. For an exact piece of text copied from an error message or identifier, `-F` is often the clearest starting choice.

Patterns become useful when you want a rule rather than a fixed substring. For example:

```bash
grep -- '^09:01' application.log
```

```text
09:01|ERROR|cache.v1|connection refused
```

Here `^` means the start of a line, so a mention of `09:01` later in a message would not match. In this pattern language, `$` means the end of a line, and `[0-9]` matches one digit in the usual C locale. You do not need these when a literal search answers the question.

To keep either error lines or warning lines, use the extended form of the pattern language:

```bash
grep -E -- 'ERROR|WARN' application.log
```

```text
09:01|ERROR|cache.v1|connection refused
09:02|WARN|worker|queue growing
09:03|ERROR|cacheXv1|retry failed
09:05|ERROR|cache.v1|retry failed
09:07|ERROR|web|upstream timeout
```

`-E` enables extended regular expressions. In that mode the `|` inside the quoted search means “or.” It is not looking for a literal bar between `ERROR` and `WARN`. It is also not a shell pipe, because the quotes keep it inside the argument passed to `grep`. Basic and extended regular expressions differ in how some punctuation is written; do not assume a pattern from another tool will work unchanged. The ordinary dot and start-of-line examples above work with either mode.

## Understand an empty result and a real error

Search for a message that is not in the fixture:

```bash
grep -F -- 'DISK_FULL' application.log
printf '%s\n' "$?"
```

```text
1
```

The search itself prints nothing. The second command prints its *exit status*, a small number a command returns separately from its text output. Bash puts the previous command's status in `$?`. Double quotes allow that value to expand while keeping it a single argument. `printf` uses `%s` to print the supplied value as text, and `\n` to end the line.

For `grep`, status `0` means at least one line matched; `1` means no line matched. GNU `grep` uses `2` for an error. Check `$?` immediately: running another command first replaces the value you wanted to examine.

A misspelled filename is a different situation:

```bash
grep -F -- 'ERROR' missing.log
```

```text
grep: missing.log: No such file or directory
```

That diagnostic was written to the error output, and the command returned status `2` in testing. Correct the filename to `application.log` and the search works again. Do not interpret this failure as “there are no errors in the log.” The log was never read.

If you genuinely need to search several files in a directory, GNU `grep` can walk through it:

```bash
grep -rniF -- 'cache.v1' .
```

At this point our directory contains only the original log, so the result is:

```text
./application.log:2:09:01|ERROR|cache.v1|connection refused
./application.log:6:09:05|ERROR|cache.v1|retry failed
```

`-r` descends into subdirectories, `-n` includes line numbers, `-i` ignores letter case, and `-F` still means literal text. The final `.` means the current directory. The added filename tells you where each match came from. GNU `grep -r` does not follow symbolic links it discovers inside the directory tree, though explicitly supplied links are handled differently.

Start with a particular file when possible. Searching an entire real log directory can take time, return unrelated matches, and produce permission errors alongside valid results. Some matches do not prove every file was successfully searched, and the word `ERROR` does not by itself establish the cause of a problem.

## Pass one command's result to another

First count the log's lines:

```bash
wc -l application.log
```

```text
8 application.log
```

`wc` can count lines, words, and bytes. The `-l` option asks only for the line count. The filename appears because we supplied it as an argument. More precisely, `wc -l` counts newline characters: our eight lines each end with one. A final unfinished line without a newline would not add to this count. Bytes are storage units and are not always the same as characters, especially for text containing accented letters or other non-ASCII characters.

Now count only error lines:

```bash
grep -F -- '|ERROR|' application.log | wc -l
```

```text
4
```

The unquoted `|` between the two commands is a *pipe*. It tells Bash to send the first command's normal output to the second command's input. That gives a small chain:

```text
application.log -> grep keeps error lines -> wc counts the received lines
```

Most commands have three separate connections: input to read, normal output for results, and error output for diagnostics. Their conventional names are *standard input*, *standard output*, and *standard error*. A plain pipe connects standard output only. Errors normally still appear in your terminal.

Here `grep` reads the named file and sends four complete lines into the pipe. With no filename argument, `wc` reads the arriving text from its standard input. It does not reread the original log, so it counts four rather than eight. It also has no filename to append to the answer.

Bash starts the commands in a pipeline together; the text can flow as it is produced. It does not have to write an intermediate file. Our count completes once `grep` has finished sending data and closed its end of the pipe.

For this particular job, `grep` has a shortcut:

```bash
grep -cF -- '|ERROR|' application.log
```

```text
4
```

`-c` counts matching lines instead of printing them. It does not count individual occurrences: a line containing the search text twice still contributes one. The longer version teaches the pipe because the same connection works with many other commands.

There is an important failure case:

```bash
grep -F -- 'ERROR' missing.log | wc -l
```

The observed normal output was:

```text
0
```

The observed error output was:

```text
grep: missing.log: No such file or directory
```

`wc` received no lines, so zero is a correct count of what it received. It is **not** a valid count of errors in the intended log. By default Bash reports the last command's status for the pipeline; here `wc` succeeds, making the pipeline status `0` even though `grep` failed.

Bash's `set -o pipefail` changes this rule for later pipelines in that shell. With it enabled, the same example returns status `2`, the rightmost nonzero status in the chain. It does not suppress the misleading-looking zero or repair the missing file. A deliberate no-match from `grep` can also make a pipeline nonzero under this setting. For now, build a chain one stage at a time and read diagnostics as well as answers; [chapter 14](14-shell-scripts.md) develops shell error handling further.

## Select fields, then count repeated values

We now want counts per component, not per severity. Each separator divides a line into pieces called *fields*. In our format the third field is the component. `cut` can take that piece from every line:

```bash
cut -d '|' -f 3 application.log
```

```text
web
cache.v1
worker
cacheXv1
web
cache.v1
worker
web
```

`-d '|'` sets the dividing character, also called the delimiter, to a literal bar. The quotes matter: without them Bash would treat the bar as a pipe. `-f 3` selects field three, counting from one. The spaces within the message do not affect the selection because spaces are not our delimiter.

This file deliberately keeps the format simple: every line has four fields and none of their values contains a bar. `cut` does not understand quoting rules from a spreadsheet or CSV format. If a different file allows separators inside quoted values, use a tool that understands that format instead of treating it as this log.

You might try counting repetitions immediately:

```bash
cut -d '|' -f 3 application.log | uniq -c
```

```text
      1 web
      1 cache.v1
      1 worker
      1 cacheXv1
      1 web
      1 cache.v1
      1 worker
      1 web
```

Why does `web` appear three times with a count of one? `uniq` only combines equal lines that are next to each other. `-c` asks it to prefix each adjacent group with its count. Every repeated component in this input is separated by another name, so no group is larger than one.

First put equal names together with `sort`:

```bash
cut -d '|' -f 3 application.log | LC_ALL=C sort
```

```text
cache.v1
cache.v1
cacheXv1
web
web
web
worker
worker
```

`sort` reads the arriving lines and writes them in order. Here `LC_ALL=C` is a temporary environment setting for this one invocation of `sort`, selecting a predictable byte-based ordering rather than your language's sorting conventions. It does not change your terminal's permanent language setting. This is useful when comparing output that mixes punctuation and upper- and lowercase letters.

Now append the counting stage:

```bash
cut -d '|' -f 3 application.log | LC_ALL=C sort | uniq -c
```

```text
      2 cache.v1
      1 cacheXv1
      3 web
      2 worker
```

Read this from left to right: select component names, put identical names together, then count each group. The leading spaces align the counts; they are not part of the component names. Without `-c`, `uniq` would print one copy of each adjacent group instead. No stage in this chain changes `application.log`.

To put the largest count first, add one more stage:

```bash
cut -d '|' -f 3 application.log | LC_ALL=C sort | uniq -c | sort -nr
```

```text
      3 web
      2 worker
      2 cache.v1
      1 cacheXv1
```

`-n` tells the final `sort` to compare the number at the start numerically. `-r` reverses the order, making it largest first. Without numeric comparison, text such as `10` can be ordered before `2`. Equal counts are ties; do not attach meaning to their order. Other names, locales, or sorting implementations may produce different tie ordering.

These are counts of all log events by component, not counts of failures or active processes. In particular, three `web` events do not mean three failed requests. The meaning of a count depends on the lines you chose to feed into it.

## Select and compare fields with awk

`cut` selects existing fields. When you also need to choose lines based on a particular field, or arrange several fields into a new result, `awk` can do both. Begin with selection only:

```bash
awk -F '|' '{print $1, $3}' application.log
```

```text
09:00 web
09:01 cache.v1
09:02 worker
09:03 cacheXv1
09:04 web
09:05 cache.v1
09:06 worker
09:07 web
```

`awk` reads one line at a time by default. Its `-F '|'` sets the field separator; this is an `awk` option, not `grep`'s fixed-string option. In this single-character separator use, the bar is literal. `$1` means the first field and `$3` the third. The braces enclose the action to perform, and `print $1, $3` prints those fields with a space between them and a newline afterward.

The single quotes around the whole little program are important. They pass `$1` and `$3` to `awk` unchanged. Without those quotes, Bash could try to substitute its own meanings for the dollar expressions before `awk` sees them.

Now ask for only records whose second field is exactly `ERROR`:

```bash
awk -F '|' '$2 == "ERROR" {print $1, $3}' application.log
```

```text
09:01 cache.v1
09:03 cacheXv1
09:05 cache.v1
09:07 web
```

`$2 == "ERROR"` is a comparison: does field two equal the text `ERROR`? `==` tests equality; it is not an instruction to change the field. Only lines for which the comparison is true receive the action in braces. The double quotes around `"ERROR"` belong to the `awk` program and identify a text value. The outer single quotes still belong to Bash.

Unlike the earlier substring search, this condition is about one specified field. A message saying `previous ERROR cleared` on an `INFO` line would not satisfy it. The result also makes a limitation visible: the two differently named cache components remain distinct. Deciding whether those names describe a typo, a configuration problem, or two legitimate components requires information outside these text commands.

## Preview an edit without changing the original

Sometimes you need a transformed copy, perhaps because a report expects the label `ALERT` instead of `ERROR`. `sed` can replace text while leaving the original file untouched:

```bash
sed 's/ERROR/ALERT/' application.log
```

```text
09:00|INFO|web|request accepted
09:01|ALERT|cache.v1|connection refused
09:02|WARN|worker|queue growing
09:03|ALERT|cacheXv1|retry failed
09:04|INFO|web|request accepted
09:05|ALERT|cache.v1|retry failed
09:06|INFO|worker|job finished
09:07|ALERT|web|upstream timeout
```

`sed` reads the file, applies the quoted instruction, and prints each resulting line. In `s/ERROR/ALERT/`, `s` means substitute. The slash characters divide the search pattern from its replacement and mark the end. This replaces the first match **on each line**, not just the first match in the entire file. Adding `g` after the final slash would replace every non-overlapping match on each line.

The search part is a regular expression, not automatically literal. The replacement has its own special characters too: for example, `&` inserts the matched text. Our simple words avoid those complications. Like the first `grep` search, this substitution is not aware of the log's fields. In another file it could change `ERROR` inside a message as well as in the severity field.

To keep the transformed result, redirect it to a different filename:

```bash
sed 's/ERROR/ALERT/' application.log > application-preview.log
head -n 2 application-preview.log
```

```text
09:00|INFO|web|request accepted
09:01|ALERT|cache.v1|connection refused
```

The `sed` command now prints nothing to the terminal because `>` sends its normal output into the preview file. The displayed lines come from `head`. As before, `>` would overwrite an existing preview file. Check the original separately:

```bash
head -n 2 application.log
```

```text
09:00|INFO|web|request accepted
09:01|ERROR|cache.v1|connection refused
```

The original still says `ERROR`. Never redirect this command to its own input filename: the shell would empty that file before `sed` could read it. Writing to a separate file avoids that particular trap and lets you inspect the proposed change. `sed -i` performs in-place editing, but its details differ between implementations. It is not needed here; retain an original or recoverable backup before making important edits.

## Watch a file as new lines arrive

A log is often still being written. To display its current ending and then wait for new data:

```bash
tail -f application.log
```

Without `-n`, `tail` starts with the last ten lines. Our fixture has only eight, so it initially displays all eight. `-f` means follow: instead of exiting after the first read, keep watching for appended data. This command stays in the foreground. It is waiting, not stuck. Press Ctrl+C to stop it and return to the shell.

Our fixture has no running application adding messages, so waiting alone produces no new output. Appending to a copy of this fixture was tested separately; do not expect simulated events to appear by themselves.

Real logging software may rename the current log and open a fresh file of the same name. This is commonly called *log rotation*. On GNU `tail`, plain `-f` follows the already-open file, so it can remain attached to the renamed old file. To follow the name and retry opening it, use:

```bash
tail -F application.log
```

GNU `-F` combines following by name with retrying. When it notices replacement, it can switch to the new file; the switch need not be immediate. Synthetic append and rename/replacement behavior was tested on a fixture, not on a real logging service. Neither mode reconstructs events never written to disk or records already removed. The fact that a line appears in a followed log tells you it was read now, not necessarily that the event occurred at precisely that instant.

## Remove the practice files

Stop any running `tail` with Ctrl+C first. If you are still in the dedicated `log-notes` directory and no longer need these examples:

```bash
rm application-preview.log
rm application.log
cd .. && rmdir log-notes
```

`rm` deletes the named files; it does not put them in a desktop trash folder. The preview file exists only if you ran the redirection example. If it does not exist, `rm` reports that rather than silently assuming it was present.

`cd ..` moves to the parent directory. Only if that succeeds does `rmdir` try to remove `log-notes`. Unlike recursive deletion, `rmdir` refuses to remove a nonempty directory. That refusal is useful if you left another file there: inspect what remains rather than escalating to a broader delete command.

The same habits carry over to real text work: inspect enough input to know its format, make the selection visible, and check what your count or edit actually represents. A command can calculate exactly what you asked while answering a different question from the one you intended.

## Further reading

- [GNU grep manual](https://www.gnu.org/software/grep/manual/), including fixed strings, regular expressions, and exit status.
- [GNU Coreutils: Output of parts of files](https://www.gnu.org/software/coreutils/manual/html_node/Output-of-parts-of-files.html), covering `head` and `tail`.
- [GNU Coreutils: wc invocation](https://www.gnu.org/software/coreutils/manual/html_node/wc-invocation.html).
- [GNU Coreutils: cut invocation](https://www.gnu.org/software/coreutils/manual/html_node/cut-invocation.html).
- [GNU Coreutils: sort invocation](https://www.gnu.org/software/coreutils/manual/html_node/sort-invocation.html).
- [GNU Coreutils: uniq invocation](https://www.gnu.org/software/coreutils/manual/html_node/uniq-invocation.html).
- [GNU awk manual](https://www.gnu.org/software/gawk/manual/). The examples here use basic features also available in common non-GNU `awk` implementations.
- [GNU sed manual](https://www.gnu.org/software/sed/manual/).
- [GNU Bash manual: Pipelines](https://www.gnu.org/software/bash/manual/html_node/Pipelines.html), including pipeline exit status and `pipefail`.
