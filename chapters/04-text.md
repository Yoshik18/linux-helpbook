# 4. Reading and searching text

[Contents](../README.md) | [Previous: files and paths](03-files-and-paths.md) | [Next: permissions](05-permissions.md)

Linux configuration and logs are often plain text. A useful first move is to inspect a small, relevant part of a file, then search for a specific value. Avoid dumping a huge log into the terminal before deciding what question you are asking.

## Read a file

```bash
cat /etc/os-release
```

`cat` writes the file's contents to standard output. It is convenient for short files. For a long file, use a pager if one is installed:

```bash
less /var/log/syslog
```

The path `/var/log/syslog` is used by some distributions; others use different log files or route messages to the system journal. `less` displays text one screen at a time. Press `q` to exit; use `/word` to search within the displayed file. If the path is absent, that alone does not imply logging is broken.

To inspect just the start or end of a file, `head` and `tail` are often more useful:

```bash
head -n 20 /etc/passwd
tail -n 20 /etc/passwd
```

`-n 20` requests twenty lines. `/etc/passwd` contains account metadata, not passwords, but it can disclose local usernames and service accounts. Do not paste system files into a public issue without checking for sensitive information.

## Search for text

`grep` prints lines that match a pattern:

```bash
grep '^PRETTY_NAME=' /etc/os-release
```

The single quotes pass the pattern literally to grep and protect it from shell expansions. In Bash, `^` alone is not special, but quoting patterns is a useful habit because other pattern characters can be. In a basic regular expression, `^` matches the start of a line. This command searches the distribution file for the human-readable name field. If there is no match, grep usually returns status `1`; that means no line matched, not necessarily that the file could not be read. Other nonzero statuses can signal an error.

To search several files recursively, GNU grep supports:

```bash
grep -rni -- 'error' /var/log
```

`-r` searches recursively without following symbolic links discovered inside the tree, `-n` prints line numbers, and `-i` ignores letter case. `--` separates options from the search pattern. Recursive log search may return permission errors or many matches. Start with the specific file or time range relevant to your investigation. Do not infer a root cause from the word `error` alone.

Use fixed-string matching when punctuation should be literal:

```bash
grep -F -- 'failed to start' /var/log/syslog
```

`-F` disables regular-expression interpretation. The example log path varies by distribution. The pattern still needs to occur exactly as written; no match is not the same as a read error.

## Count and transform lines

`wc` counts lines, words and bytes. With `-l`, it prints only the line count:

```bash
wc -l /etc/passwd
```

The count describes the file at the time it was read. It does not tell you how many users can log in, because service and locked accounts may also appear.

`sort` orders lines; `uniq` removes adjacent duplicate lines. To count repeated values, sort first:

```bash
cut -d: -f7 /etc/passwd | sort | uniq -c
```

`cut -d:` splits each line on `:` and `-f7` selects field seven, the login shell field in this file format. `sort` groups equal shell paths together; `uniq -c` prints each distinct adjacent value with its occurrence count. The counts describe local account records, not active login sessions. The pipe (`|`) connects the first command's standard output to the next command's standard input. The shell starts all commands in the pipeline. This is a read-only example, but it exposes local account configuration; review output before sharing it.

## Select columns and transform a stream

`awk` handles records and fields. This example selects two fields from the colon-separated account file:

```bash
awk -F: '{print $1, $7}' /etc/passwd
```

`-F:` sets the field separator to a colon. The single-quoted program prints fields one and seven, separated by a space, for each record. Here `$1` and `$7` belong to awk, not to the shell: the quotes prevent shell expansion. The result pairs each local account name with its configured shell; it does not identify which accounts are allowed to log in.

`sed` can transform text without modifying the source file:

```bash
printf 'status=old\n' | sed 's/old/new/'
```

The `s/pattern/replacement/` instruction replaces the first match on each line and prints the result, `status=new`. The pattern is a regular expression. This command transforms an input stream only. In-place editing options such as `sed -i` change files and vary between implementations; inspect output and keep a recoverable copy before using them on important data.

## Follow a growing log

`tail -f application.log` first prints the final lines of an existing log, then waits for more data. Use a log you are allowed to read, and press Ctrl+C to stop following it. On GNU tail, `-f` follows the open file descriptor; `tail -F application.log` follows the name and retries, which helps when rotation replaces the file. Neither command reconstructs records that were never written or have already been removed.

## Common confusion

- `grep` status `1` commonly means no match; a larger error status can mean the file could not be read.
- `head` and `tail` show only part of a file. Absence from that excerpt is not proof a message never occurred.
- Recursive grep can print permission errors and still find some matches.
- Regular expressions give punctuation special meaning; use `grep -F` for literal text.
- A pipeline can hide an earlier command's failure unless you inspect each status or configure shell pipeline behavior.

## Further reading

- [GNU grep manual](https://www.gnu.org/software/grep/manual/)
- [GNU Coreutils: Output of parts of files](https://www.gnu.org/software/coreutils/manual/html_node/Output-of-parts-of-files.html)
- [GNU Coreutils: wc invocation](https://www.gnu.org/software/coreutils/manual/html_node/wc-invocation.html)
- [GNU awk manual](https://www.gnu.org/software/gawk/manual/)
- [GNU sed manual](https://www.gnu.org/software/sed/manual/)
