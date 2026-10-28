# 2. The shell and commands

[Contents](../README.md) | [Previous: system](01-system.md) | [Next: files and paths](03-files-and-paths.md)

Suppose you want to keep a short list of jobs, find the unfinished ones, and save those in a second file. You could open an editor and do the work by hand. You can also describe the work in a few lines of text and let the computer repeat it. This chapter builds that small example, one part at a time.

The important part is not memorizing punctuation. It is learning who reads it. In a line such as `cat "job notes.txt"`, one program works out where the command starts and how the filename is grouped. Another program reads the file. Understanding that division explains many errors that otherwise seem arbitrary.

## In this chapter

- [The window and the program reading your commands](#the-window-and-the-program-reading-your-commands)
- [A separate place for the example](#a-separate-place-for-the-example)
- [What a command receives](#what-a-command-receives)
- [Keep a value together with quotes](#keep-a-value-together-with-quotes)
- [Save a value in a variable](#save-a-value-in-a-variable)
- [Let the shell find matching filenames](#let-the-shell-find-matching-filenames)
- [Send text to a file](#send-text-to-a-file)
- [Build a pipe one step at a time](#build-a-pipe-one-step-at-a-time)
- [Keep results and errors separate](#keep-results-and-errors-separate)
- [Find out whether a command succeeded](#find-out-whether-a-command-succeeded)
- [How the shell finds a command](#how-the-shell-finds-a-command)
- [Variables passed to other programs](#variables-passed-to-other-programs)
- [Leave the example directory safely](#leave-the-example-directory-safely)
- [Further reading](#further-reading)

## The window and the program reading your commands

A **terminal** is the window or text screen that lets you type commands and see their output. The **shell** is the program that reads those commands and arranges the work. Bash is one common shell, and the examples here use Bash with the usual GNU command-line programs.

When the shell is ready, it displays a **prompt**. This might contain your username, a directory name, and a final `$`. The examples below omit the prompt: type only the text inside each command block, then press Enter. Blocks labeled as output are what you read, not additional commands to type.

An ordinary command runs and then returns you to the prompt. A command that is waiting for input may not do that immediately. Ctrl+C usually interrupts the foreground command, the one currently using the terminal. It does not undo files that command has already changed.

If you normally use a different shell, you can start a Bash session without loading personal Bash startup files:

```bash
bash --noprofile --norc
```

`--noprofile` and `--norc` tell Bash to skip those startup files. They do not erase the environment inherited from your existing shell or turn Bash into a security sandbox. At the end, `exit` leaves this extra session. You do not need to start another Bash if you are already using it.

## A separate place for the example

We will create small files, so use a new directory rather than experimenting among existing documents:

```bash
work=$(mktemp -d "$HOME/shell-notes.XXXXXX")
cd "$work"
pwd
```

`mktemp` creates a new name that is not already in use. Its `-d` option asks for a directory rather than a file. The six `X` characters are replaced with a generated ending. `$HOME` supplies your home directory, so this creates a new directory there without needing administrator access.

The outer `$(...)` runs the command inside it and uses its printed result as a value. This is called **command substitution**. Here, Bash stores the new directory's path in a variable called `work`. The assignment does not print that value. If `mktemp` reports an error, stop and address that error rather than continuing with an unset or empty destination.

`cd` changes the directory in which this shell is working. `pwd` prints that directory. The output will resemble this schematic path, with your own home directory and generated ending:

```text
/home/yourname/shell-notes.A1b2C3
```

This is the **working directory**. Names without a leading `/`, such as `jobs.txt`, are interpreted relative to it. A path starting with `/` starts at the top of the filesystem instead. The next chapter explores paths in more detail.

If a file seems to have disappeared, run `pwd` before creating a replacement. Often you have simply moved to another directory. `cd -` returns to the previous working directory and prints its path. It switches between the last two locations; it is not a list of every directory you have visited.

## What a command receives

Start with a command that prints a few words:

```bash
printf '%s\n' pack read rest
```

Output:

```text
pack
read
rest
```

`printf` is the command name. The remaining pieces are values passed to it, called **arguments**. This command receives four arguments: the format `%s\n`, then `pack`, `read`, and `rest`.

The first argument tells `printf` how to display the others. `%s` means “put a text value here”; `\n` means “start a new line.” When there are more values, `printf` reuses this format. That is why three words become three lines. The single quote marks keep the format together and preserve the backslash for `printf` to interpret. The quote marks themselves are not passed to the command.

Notice that a command can give special meaning to one of its arguments. Bash does not interpret `%s` as a print instruction: `printf` does. Later, we will meet symbols such as `>` that Bash handles itself before the program runs.

Many programs also take arguments that choose a behavior. These are called **options**. For example:

```bash
ls -lah .
```

`ls` lists names in a directory. Here `.` means the current directory. `-lah` combines three short options: `-l` asks for a detailed listing, `-a` includes names starting with a dot, and `-h` makes sizes easier to read in the detailed listing. The output depends on your files and system, so there is no fixed listing to compare against.

These meanings belong to `ls`, not to the minus sign in general. Another command's `-h` might request help, or it might mean something else. To read the options accepted by GNU `ls`, use:

```bash
ls --help
```

The two leading minus signs introduce a long option here. Many external programs support `--help`, but not all do. For a command built into Bash, use Bash's own help, for example `help cd`. If manual pages are installed, `man ls` opens the longer reference for `ls`; press `q` to leave its usual viewer. A small installation may have no `man` command or no manual pages.

## Keep a value together with quotes

Return to `printf` and compare these two commands:

```bash
printf '<%s>\n' pack bag
printf '<%s>\n' 'pack bag'
```

Output:

```text
<pack>
<bag>
<pack bag>
```

The angle brackets are ordinary printed characters. They make the boundaries visible. In the first command, spaces separate `pack` and `bag` into two arguments. In the second, quotes group `pack bag` into one argument, including its space. That difference matters for filenames: `job notes.txt` is one name, not two files called `job` and `notes.txt`.

Single quotes keep their contents literal. Double quotes also keep spaces together, but allow values such as `$HOME` to be substituted. We will make this difference visible using our own variable rather than printing personal system information.

Quotes do not become part of the stored text unless you specifically include quote characters inside them. They are instructions to the shell about how to prepare arguments. This is why `cat "job notes.txt"` asks for a filename containing a space, not a filename containing quote marks.

## Save a value in a variable

A variable gives a short name to a value you want to use again:

```bash
note='job notes.txt'
printf '<%s>\n' "$note"
printf '<%s>\n' '$note'
printf '<%s>\n' $note
```

Output in the clean example session:

```text
<job notes.txt>
<$note>
<job>
<notes.txt>
```

The first line, `note='job notes.txt'`, is an assignment. There are no spaces around `=`. It stores the text `job notes.txt`; it does not create a file.

In `"$note"`, Bash replaces `$note` with its value and keeps that value as one argument. In `'$note'`, the single quotes prevent replacement, so the printed text is literally `$note`. In the unquoted `$note`, Bash replaces the value and then, with its normal settings, splits it at spaces. That leaves two arguments for `printf`.

This replacement is called **expansion**. The word describes what Bash does before starting a command, not something the command does later. By the time `printf` runs, it has received either one filename, a literal dollar-sign expression, or two separate words.

Leave out the spaces around `=` deliberately. This incorrect version does something different:

```bash
note = 'job notes.txt'
```

Instead of assigning a value, Bash tries to run a command named `note`, passing `=` and `job notes.txt` as arguments. In a clean session without such a command, it reports `note: command not found`. Correct it by writing `note='job notes.txt'`. The exact error prefix can vary by shell and setup.

Use double quotes around variable references that represent one path or one value: `"$note"`, not `$note`. Besides spaces, an unquoted value can contain filename patterns that Bash expands. A value that is empty can disappear entirely when unquoted; quoted, it remains one empty argument. These are changes to what the command receives, not just differences in presentation.

Quotes preserve boundaries. They do not make every use of a value safe. In particular, do not feed untrusted text to `eval`, which asks the shell to interpret text as commands again. None of the work here needs it.

## Let the shell find matching filenames

We do not yet have a notes file. First, look at the difference between text and a filename pattern:

```bash
printf '%s\n' '*.txt'
```

Output:

```text
*.txt
```

The single quotes keep the asterisk literal. Without quotes, Bash treats `*.txt` as a request to find names ending in `.txt` in the working directory. This is a **wildcard pattern**. The `*` can stand for any number of characters, including none.

In ordinary Bash settings, a pattern that finds no matching names stays unchanged. In this new, still-empty directory:

```bash
ls -- *.txt
```

`ls` reports that it cannot access `*.txt`. The error does not mean the asterisk is broken. Bash found no matches and passed the text `*.txt` to `ls`, which tried to find a file with that literal name. Shell options can change unmatched-pattern behavior; this chapter uses the default behavior.

The `--` tells `ls` that option processing is finished. Arguments after it are names, even if a name begins with `-`. Many, but not all, commands support this convention. Quoting groups a filename; `--` solves a different problem, namely a program mistaking a filename for an option.

We will repeat the wildcard command after creating files so you can see what changes. Patterns normally exclude names beginning with a dot unless the pattern explicitly includes that initial dot or the shell is configured differently. Always inspect wildcard matches before using a command that would remove or overwrite them.

## Send text to a file

Write two entries to our notes file:

```bash
printf '%s\n' 'todo pack bag' 'done read chapter' > "$note"
cat "$note"
```

Output from `cat`:

```text
todo pack bag
done read chapter
```

`cat` reads the named file and prints its contents. The earlier `printf` produced the same sort of text it produced on screen before. What changed was the destination.

Bash handles `>`: it opens the file named by `"$note"` and sends the command's normal output there. This is **redirection**. `printf` is not given `>` or the filename as additional arguments. It receives its format and two text values, then writes its output to the destination Bash prepared.

If the file does not exist, `>` creates it. If it already exists, `>` empties it before the command runs. That makes `>` useful for replacing a generated result, but unsuitable for adding one more note to existing notes.

Use two greater-than signs to add text at the end:

```bash
printf '%s\n' 'todo buy bread' >> "$note"
cat "$note"
```

Output:

```text
todo pack bag
done read chapter
todo buy bread
```

`>>` appends instead of replacing. It also creates the target if it does not exist. No output from either writing command appears on screen because the output went into the file. Reading it back with `cat` confirms the actual contents rather than assuming silence meant success.

To count its lines:

```bash
wc -l "$note"
wc -l < "$note"
```

The first command reports a count of `3` along with the filename `job notes.txt`. The second reports just the count `3`; surrounding spaces may vary.

`wc` counts parts of text, and its `-l` option counts newline characters. Our `printf` ended each entry with a newline, so the count equals the number of entries. A final piece of text without a newline would not add to that count.

In the first command, the filename is an argument and `wc` opens it. In the second, `<` tells Bash to open the file for reading and connect it to the command's usual input. `wc` receives `-l` but no filename, so it reads that input and has no filename to include in its report. The file is the same; the route to the command is different.

Do not write `cat "$note" > "$note"` to copy the file onto itself. Bash would empty the output file before `cat` could read the original contents. A redirection is prepared before the command runs, even if that command later fails.

## Build a pipe one step at a time

The notes file has three entries. Begin by reading all three:

```bash
cat "$note"
```

Now put a vertical bar after that command and give its output to a search command:

```bash
cat "$note" | grep -F 'todo'
```

Output:

```text
todo pack bag
todo buy bread
```

`grep` selects lines containing a match. Its `-F` option treats `todo` as ordinary text rather than as a special search pattern. Here any line containing those four characters is selected, not only a line beginning with them.

The `|` is called a **pipe**. Bash connects the first command's normal output to the second command's normal input. `cat` does not display its lines on the terminal in this version; `grep` receives them instead. `grep` then prints the selected lines to the terminal. No intermediate file is needed.

Add a third stage only after the first two make sense:

```bash
cat "$note" | grep -F 'todo' | wc -l
```

Output is the count `2`, possibly with surrounding spaces. `cat` supplies three lines, `grep` passes on two, and `wc -l` counts the two newline characters it receives. The last command sees the filtered text, not the original file.

For this particular job, `cat` is optional because `grep` can open a file itself:

```bash
grep -F 'todo' "$note" | wc -l
```

This also reports `2`. The longer version made each connection visible; the shorter version avoids a separate program merely to read the file.

Save the selected lines rather than their count:

```bash
grep -F 'todo' "$note" > todo.txt
cat todo.txt
```

Output:

```text
todo pack bag
todo buy bread
```

We now have two `.txt` files. Repeat the filename-pattern example:

```bash
printf '<%s>\n' *.txt
```

Output in this directory:

```text
<job notes.txt>
<todo.txt>
```

Bash finds the two names before starting `printf`. The space inside the matched filename does not split that match into two arguments. Compare this with the earlier unquoted `$note`: splitting a variable value and finding matching filenames are different steps. The simplest reliable habit is still to quote a variable containing a path.

## Keep results and errors separate

Commands have two usual output routes. One carries requested results; the other carries explanations of problems. Both normally appear in the terminal, so until now they may have looked like one thing.

The result route is called **standard output**. The problem-reporting route is called **standard error**. The usual route for incoming text is **standard input**. These are connections a program uses, not necessarily files on disk: Bash can connect them to a terminal, a file, or another program.

Ask `cat` to read one existing file and one missing file:

```bash
cat "$note" missing.txt > combined.txt
```

You will still see a diagnostic resembling:

```text
cat: missing.txt: No such file or directory
```

The three lines from the existing file went into `combined.txt`. The complaint did not, because `>` redirects standard output, not standard error. You can read `combined.txt` with `cat combined.txt` to see that it contains the notes but not the complaint.

Send the two routes to separate files:

```bash
cat "$note" missing.txt > combined.txt 2> errors.txt
cat errors.txt
```

Now the complaint is in `errors.txt`. The `2` identifies standard error; the `>` immediately after it sends that connection to a file. Leave `2>` together. Writing `2 > errors.txt` would instead pass `2` as an argument and redirect standard output.

The connection numbers are called **file descriptors**: `0` for standard input, `1` for standard output, and `2` for standard error. The plain `>` you used earlier means `1>`.

A pipe also carries standard output only, unless you explicitly arrange otherwise. For example:

```bash
cat "$note" missing.txt | wc -l
```

The count is still `3`, and the missing-file complaint still appears on the terminal. Its position relative to the count may vary because the commands run together. A sensible-looking count does not prove that every input file was read successfully.

Sometimes you want one file containing both results and complaints:

```bash
cat "$note" missing.txt > combined.txt 2>&1
```

Read this from left to right. First, `>` connects standard output to `combined.txt`. Next, `2>&1` makes standard error use the destination standard output has at that moment. The ampersand here says to use an existing numbered connection, not a file named `1`.

Order matters. This different command leaves the complaint on the terminal:

```bash
cat "$note" missing.txt 2>&1 > combined.txt
```

At the first step, standard output still goes to the terminal, so standard error is connected there too. The second step changes only standard output to the file. It does not move standard error again. Think of `2>&1` as copying the current destination, not permanently tying the two numbers together.

Keep errors visible while investigating a problem. Redirecting them away can hide the reason a command returned incomplete results.

## Find out whether a command succeeded

Printed text is one kind of result. Programs also return a small number when they finish, called an **exit status**. Zero conventionally means success; a nonzero number means some other outcome, whose exact meaning depends on the command.

Try a search that finds no matching lines:

```bash
grep -F 'cancelled' "$note"
printf 'status=%s\n' "$?"
```

Output:

```text
status=1
```

`grep` prints nothing because none of our entries contains `cancelled`. Its status is `1`, meaning no match. For `grep`, `0` means a match was found and `2` indicates an error. A nonzero status is therefore not always a broken program or system.

`$?` supplies the previous command's status. Bash substitutes it before starting `printf`. After `printf` finishes, `$?` describes `printf`, not the earlier search. If you need the earlier status later, save it immediately:

```bash
grep -F 'cancelled' "$note"
search_status=$?
printf 'search status=%s\n' "$search_status"
```

This prints `search status=1`. The assignment captures the old value; an unrelated command between the search and that assignment would lose it.

Pipelines need more care. By default, Bash reports the last command's status:

```bash
cat missing.txt | wc -l
printf 'pipeline status=%s\n' "$?"
```

You see a missing-file complaint, a count of `0`, and `pipeline status=0`. `cat` failed, but `wc` successfully counted the empty input. This is not evidence that the file was empty: the file was never opened.

Bash has a setting for noticing such failures:

```bash
set -o pipefail
cat missing.txt | wc -l
printf 'pipeline status=%s\n' "$?"
set +o pipefail
```

With this setting, the same missing-file example reports a nonzero pipeline status. On the GNU tools used for these examples it is `1`. `set -o pipefail` enables the setting; `set +o pipefail` disables it again. More precisely, with `pipefail` enabled the status comes from the rightmost pipeline command that returned nonzero, or is zero if all succeeded.

This setting changes how Bash reports the result; it does not stop `wc` from running or repair missing input. It can also make a no-match result from `grep` make the whole pipeline nonzero. Understand each stage before treating every nonzero pipeline result as the same kind of failure.

## How the shell finds a command

Until now we have treated the command name as the first word on the line. But how does Bash know what `cat`, `cd`, or `printf` means?

Some commands are part of Bash itself. These are **builtins**. Others are separate program files. Ask Bash about the names:

```bash
type cd
type printf
type cat
```

In a Bash session without custom replacements, the first two are reported as shell builtins. `cat` is normally reported with the path to a separate executable, such as `/usr/bin/cat`. The exact path varies. An **executable** is a file the system can run as a program.

`cd` must affect the shell itself: it changes the working directory that later commands inherit. A separate program cannot change the working directory of the shell that started it.

Personal setup can add shortcuts called aliases or reusable command groups called functions. These can take precedence over a program with the same name. That is one reason `type` is useful when a familiar command behaves unexpectedly.

For another lookup form, use:

```bash
command -v bash
```

This asks how the current shell would resolve the name `bash`. It normally prints a path. `command -v` is also available in many shells other than Bash. For a builtin, alias, or function, its answer need not be an executable file path. No output with a nonzero status means the name was not found through that lookup, not proof that no such file exists anywhere on the computer.

For a separate program named without a slash, Bash searches a configured list of directories, called `PATH`, normally checking them in order. For example, if `/usr/bin` is on that list, it can find `/usr/bin/cat` when you type `cat`. Bash may remember successful lookups rather than search afresh each time. A name with a slash, such as `/usr/bin/cat` or `./helper`, specifies a path instead of asking for that search.

You can inspect your own search list with:

```bash
printf '%s\n' "$PATH"
```

Its output is machine-specific: colons separate directory entries. Do not replace it with a guessed list from a tutorial. In particular, putting an untrusted writable directory first could cause its program to run instead of the system program you expected. There is no need to change `PATH` for this chapter.

## Variables passed to other programs

Our `note` variable has been useful within this shell. A program started by the shell does not automatically receive every shell variable. Values deliberately passed on to new programs form the shell's **environment**.

A second Bash can demonstrate this without depending on a particular editor or application. First remove any old value of a demonstration name, then assign a new one:

```bash
unset NOTE_LABEL
NOTE_LABEL='weekend jobs'
bash --noprofile --norc -c 'printf "child sees: <%s>\n" "$NOTE_LABEL"'
```

Output:

```text
child sees: <>
```

`unset` removes the named variable, including an inherited exported value if there was one. The assignment creates a variable in our current shell. The new Bash does not receive it, so in its normal settings its unset `$NOTE_LABEL` expands to empty text.

`-c` tells the new Bash to run the command text in the following argument. The outer single quotes are important: the parent shell passes that text literally. The child Bash then interprets the double quotes and `$NOTE_LABEL`. Without that separation, we might accidentally print a value supplied by the parent and learn nothing about what the child received.

Now make the variable available to subsequently started programs:

```bash
export NOTE_LABEL
bash --noprofile --norc -c 'printf "child sees: <%s>\n" "$NOTE_LABEL"'
unset NOTE_LABEL
```

Output:

```text
child sees: <weekend jobs>
```

`export` marks the variable for inclusion in the environment of new programs. It does not send a live update to programs already running. Each child receives its own starting values; changes in that child do not change the parent shell's variables. The final `unset` removes the demonstration value from our shell.

A practical use is `export EDITOR=nano`, if Nano is the editor you actually use. Programs that consult `EDITOR` can then choose it when they next need an editor. This assignment neither installs Nano nor opens it, and not every application uses this setting. It also does not change an unrelated terminal's environment. Avoid putting secrets in demonstrations or dumping your whole environment when asking for help.

## Leave the example directory safely

The working directory now contains the original notes, selected notes, and the files used to demonstrate output and errors. If you want to keep them, simply leave the directory in place.

If you want to remove this example's files, first check that you are still in the generated `shell-notes` directory and list its contents:

```bash
pwd
ls -a
```

`ls -a` includes names beginning with a dot. Only continue if this is your example directory and the following names are the files you created here:

```bash
rm -- 'job notes.txt' todo.txt combined.txt errors.txt
cd ..
rmdir -- "$work"
unset note work
```

`rm` removes the four explicitly named files. The quoted name remains one argument. This is not a wildcard removal: it does not select extra files that happen to end in `.txt`. Ordinary command-line removal does not send files to a desktop trash folder.

`cd ..` moves to the parent directory. `rmdir` removes the now-empty example directory named by `work`; it refuses to remove a directory that still contains files. If it refuses, inspect the remaining contents rather than changing this into a recursive removal. `unset note work` clears our two variables. If you started an extra Bash at the beginning, `exit` returns to the shell underneath it.

The same few distinctions explain the whole example: the shell prepares arguments; commands act on the arguments they receive; quotes keep values together; input and output connections decide where text travels; and the status reports an outcome separately from the printed text. When a longer command is confusing, shorten it until you can see each of those parts again.

## Further reading

- [Bash manual](https://www.gnu.org/software/bash/manual/)
- [Bash reference manual: quoting](https://www.gnu.org/software/bash/manual/html_node/Quoting.html)
- [Bash reference manual: shell expansions](https://www.gnu.org/software/bash/manual/html_node/Shell-Expansions.html)
- [Bash reference manual: redirections](https://www.gnu.org/software/bash/manual/html_node/Redirections.html)
- [GNU coreutils manual](https://www.gnu.org/software/coreutils/manual/)
