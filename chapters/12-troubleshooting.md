# 12. Troubleshooting without guessing

[Contents](../README.md) | [Previous: packages](11-packages.md) | [Next: security](13-security.md)

A report command works when you run it from its folder. Run the same script from somewhere else, and it says that its input file does not exist. Yet you can still see that file. Should you reinstall the program? Change the file's permissions? Restart something?

None of those changes follows from what we know so far. We first need to find out which file the command tried to open, and from where.

This chapter follows that small failure from the first error to a checked correction. The files are deliberately created for the example. There is no claim that an actual company service failed this way. The point is to practice separating what happened from what might explain it, using a failure that is safe to repeat.

## On this page

- [Make a small report that can fail safely](#make-a-small-report-that-can-fail-safely)
- [Catch the failure without losing its evidence](#catch-the-failure-without-losing-its-evidence)
- [Ask smaller questions](#ask-smaller-questions)
- [Compare a working case with the failing case](#compare-a-working-case-with-the-failing-case)
- [Reproduce, change one thing, and check again](#reproduce-change-one-thing-and-check-again)
- [Decide what the correction does and does not prove](#decide-what-the-correction-does-and-does-not-prove)
- [Carry the same reasoning to a service or website](#carry-the-same-reasoning-to-a-service-or-website)
- [Know when to stop and ask for help](#know-when-to-stop-and-ask-for-help)
- [Remove the example files](#remove-the-example-files)
- [Further reading](#further-reading)

## Make a small report that can fail safely

Use an ordinary account, not an administrator account. Everything we create belongs in one new directory. Do not substitute a real report job, customer data, or a scheduled task: rerunning a real job might send messages, charge money, or overwrite records.

The examples use Bash and common GNU commands. To start a Bash session without its usual personal startup files, run:

```bash
bash --noprofile --norc
```

`bash` starts another command-reading shell. `--noprofile` skips Bash's login startup files; `--norc` skips its interactive startup file. This makes personal aliases and startup commands less likely to change the example. It is not a security sandbox and does not erase inherited settings. Keep using this same terminal so the variables and current directory remain available.

First, create a directory with a fresh name:

```bash
case_dir=$(mktemp -d "$HOME/troubleshooting.XXXXXX")
printf '%s\n' "$case_dir"
```

`mktemp` creates a new file or directory with an unpredictable name. `-d` asks for a directory. The six `X` characters are replaced with generated characters, so an existing folder is not silently reused. `$HOME` supplies your home directory. You do not need to type your username into the command.

`$(...)` means “run the enclosed command and use its output here.” `case_dir=` saves that path in a shell variable named `case_dir`; there are no spaces around `=`. Later, `$case_dir` retrieves the saved value. The double quotes keep an expanded path together even if it contains spaces.

`printf` prints according to a format. Here `%s` means a string and `\n` means a newline. The single quotes protect the format from shell interpretation. The printed result will be the full path to your new folder. Its final characters will differ on each run. If creation fails, stop here rather than continuing with an empty or unexpected path.

Now make two folders and two tiny text files:

```bash
mkdir "$case_dir/data" "$case_dir/launcher"
printf '%s\n' 'Daily report: 3 orders' > "$case_dir/data/orders.txt"
printf '%s\n' 'cat data/orders.txt' > "$case_dir/report.sh"
```

`mkdir` creates the two named directories. `data` will hold the input; `launcher` will be an empty folder from which we start the report.

The `>` symbol sends a command's normal output into a file rather than to the terminal. It creates a missing file, but **replaces the contents of an existing file**. That is why these commands target only our newly created directory. They should normally print nothing.

The first `printf` writes the report's input text. The second writes one line of shell commands into `report.sh`:

```text
cat data/orders.txt
```

`cat` reads a file and prints its contents. Our “report” only prints its input, which keeps the failure easy to inspect. We will ask Bash to read `report.sh`, so the file does not need executable permission. No permission changes are part of this example.

The arrangement is now:

```text
new example directory/
    report.sh
    data/
        orders.txt
    launcher/
```

This is a diagram, not output from a directory-listing command.

## Catch the failure without losing its evidence

Start the report from the empty `launcher` folder. Before doing that, we need two ways to record what happened: a time and an exit status.

A command can print ordinary results and error messages separately. The ordinary results use **standard output**; error messages conventionally use **standard error**. The shell identifies standard error as stream number `2`. In `2> filename`, the `2` must touch the `>`: together they redirect error messages into that file. Normal output still goes to the terminal.

When a command finishes, it also returns a small number called its **exit status**. Zero normally means success; a nonzero value means some other outcome, whose exact meaning depends on the command. Bash makes the most recent status available as `$?`. Save it immediately. Even a successful command that prints a timestamp replaces it.

`date -u` prints the time using Coordinated Universal Time (UTC), a shared time reference, rather than the machine's local timezone. The argument starting with `+` selects its layout: `%Y-%m-%d` is year-month-day, `%H:%M:%S` is hour:minute:second, and the literal `T` and `Z` make the boundary and UTC designation visible.

Run these commands in order. If `cd` reports an error, stop instead of running the remaining lines from the wrong place.

```bash
cd "$case_dir/launcher"
date -u '+%Y-%m-%dT%H:%M:%SZ'
bash "$case_dir/report.sh" 2> "$case_dir/failure.log"
result=$?
printf 'report exit status: %s\n' "$result"
date -u '+%Y-%m-%dT%H:%M:%SZ'
cat "$case_dir/failure.log"
```

`cd` changes the shell's current directory. `bash "$case_dir/report.sh"` asks Bash to read and execute the file at that full path. `result=$?` saves its exit status before another command can replace it. The final `cat` reads the error log we just created.

This is actual output from the disposable example during testing. Your timestamps will differ, and error wording can depend on the system's language settings:

```text
2026-10-28T05:08:32Z
report exit status: 1
2026-10-28T05:08:32Z
cat: data/orders.txt: No such file or directory
```

There are several separate facts here:

- No report text appeared.
- The report invocation returned `1`, not `0`.
- The message names `cat` and `data/orders.txt`.
- The two timestamps place this attempt within one second at the displayed precision. They do not measure its exact duration.

The log's last line was displayed after the second timestamp because we read the log then. It does not mean the error happened after the command finished. Logs can be written earlier than they are viewed.

A useful first problem statement is: “From the example's launcher directory, Bash can start the report, but its attempt to read `data/orders.txt` fails with ‘No such file or directory’ and status 1.” That is more useful than “Linux lost my file.”

Our log contains one run's error message, not a complete recording of the terminal session. We recorded the time and status separately. On real work, keep the exact command, its output, its status, its time and timezone, and where you ran it. Preserve those notes before retrying anything that overwrites a log. Here, `2>` would replace `failure.log` if we used that same redirection again.

## Ask smaller questions

The message is evidence about one attempted file read. It does not prove the input has been deleted everywhere, nor does it prove a permissions problem.

A **hypothesis** is a possible explanation with a consequence we can check. “The input was deleted” predicts that reading the intended input directly should also fail. “The script is looking from the wrong directory” predicts that the intended file could still be readable by its full path.

Check where we are, then try reading that intended file:

```bash
pwd
cat "$case_dir/data/orders.txt"
```

`pwd` prints the current working directory: the folder from which relative file names are interpreted. Its output in your run should be the generated example path ending in `/launcher`. The second command gave this actual result in testing:

```text
Daily report: 3 orders
```

That is a useful discovery. For this user, at this moment, the file at the full path exists and can be read. Reinstalling `cat` or granting everybody access would not explain why that direct read already works.

Do not stretch the conclusion. We have not shown that another account could read the file, that it was present yesterday, or that a program inside a different container sees it. We have answered a small question about this attempt.

Next, read the script rather than changing it:

```bash
cat "$case_dir/report.sh"
```

Actual result:

```text
cat data/orders.txt
```

The script asks for `data/orders.txt`, not the full path we just read successfully. It does not begin with `/`, so it is a **relative path**: its starting point is the process's current directory.

Our starting folder is `launcher`. From there, the requested path means “look for a `data` folder inside `launcher`, then for `orders.txt` inside that.” We created no such folder. The real `data` folder is alongside `launcher`, one level above it.

Bash found the script because we gave Bash its full path. That does not make the script's own relative paths start from its containing folder. Unless a program changes directory itself, it normally starts with the directory inherited from the program that launched it. Finding the script and finding the script's input are two different steps.

This distinction often explains why “it works in my terminal” is not enough information. A terminal, a scheduler, and a service manager may start the same command from different directories, under different accounts, with different settings. Those are possible differences to check, not reasons to assume a scheduler is broken.

## Compare a working case with the failing case

We now have a **known-good comparison**: the same input is readable through its full path. “Known-good” does not mean a whole machine is perfect. It means a specific action produced the expected result under recorded conditions.

Our comparison kept the account, machine, input contents, and reading program the same. It changed how the input was located. That makes a path explanation more persuasive than a theory about a broken disk. A comparison against an unrelated report on another server would change too many things to be as useful.

Think of the report as a short chain of steps, or **layers**:

1. The shell must find and start Bash.
2. Bash must find and read `report.sh`.
3. Bash must run the command inside the script.
4. That command must find and read its input.
5. Its output must reach the place where we expect to see the report.

The error came from `cat`, which is inside the script. We have evidence that execution reached the input-reading step. Starting again with package installation would ignore that evidence. Equally, finding a readable script alone would not prove that its input exists.

This is how layers help: not as a long list to run blindly, but as a way to ask which part has been reached and which next part is still uncertain. Check the part closest to the evidence before expanding the search.

## Reproduce, change one thing, and check again

We have a strong explanation, but we should test its prediction. Because this report only reads a disposable file, running it again has no business effect. That safety property matters more than the convenience of reproduction.

While still in `launcher`, run the same report again, this time leaving its error visible rather than replacing the saved log:

```bash
bash "$case_dir/report.sh"
result=$?
printf 'report exit status: %s\n' "$result"
```

The observed error was again:

```text
cat: data/orders.txt: No such file or directory
```

The status line was:

```text
report exit status: 1
```

These come from different output streams; the display order can vary when another tool captures them. The important comparison is the same failing read and status, not the order in which a viewer displays the streams.

Now change just the starting directory. Leave the script, account, input, and invocation unchanged. Record the corrected attempt in a separate error log so the first failure remains available:

```bash
cd "$case_dir"
pwd
date -u '+%Y-%m-%dT%H:%M:%SZ'
bash "$case_dir/report.sh" 2> "$case_dir/success.log"
result=$?
printf 'report exit status: %s\n' "$result"
date -u '+%Y-%m-%dT%H:%M:%SZ'
cat "$case_dir/success.log"
```

Check that `cd` succeeded before continuing. `pwd` should now print the generated example path without `/launcher` at the end. After that path line, the observed output in testing was:

```text
2026-10-28T05:08:32Z
Daily report: 3 orders
report exit status: 0
2026-10-28T05:08:32Z
```

Reading `success.log` printed nothing: that file was empty. Notice all three checks together. The intended report appeared, the invocation returned zero, and no error message was captured. An empty error log alone would not establish that the report had the correct contents. A zero status alone would not establish that it printed a useful report.

We can now explain both outcomes with the same mechanism. From `launcher`, `data/orders.txt` names the wrong location. From the example's main directory, it names the input we created. Changing only the working directory produced the predicted change in result.

## Decide what the correction does and does not prove

For this fixture, the narrow correction is to launch the report from its required directory. We did not need to edit input data, reinstall software, become an administrator, or make the input writable.

That establishes the cause of this constructed failure. It does not establish the cause of some unrelated real report outage. If you encounter a similar message on a real system, repeat the reasoning against that system's evidence rather than importing this answer.

A lasting correction depends on who owns the report and how it is meant to run. A job configuration might need an explicit working directory. A script might instead need a configured full input path. Those are design decisions with different effects: changing directory also changes how every other relative path in the program is interpreted. Do not paste a new directory into a live service definition just because it repaired this small example.

There is another limit to the status evidence. Our script contains one command, so Bash's script status reflects that command. In a longer script, the status normally reflects the last command executed. A later successful “finished” message can hide an earlier failed read unless the script handles failures deliberately. Chapter [14](14-shell-scripts.md) develops that issue. Always check the promised result as well as the final status.

If an incident is urgent, distinguish **restoring service** from **explaining the failure**. An approved restart might restore a service while leaving the cause unknown. Record it as a recovery action, not proof that the service “needed a restart.” A restart can clear useful evidence and interrupt people. Save relevant observations first when the situation and the owner's procedures allow it.

## Carry the same reasoning to a service or website

A browser saying “this site cannot be reached” is a much broader starting symptom than our file error. There are more steps between the action and the result, but the reasoning is the same: identify the attempted action, find the earliest failing step, and compare a closely matched working case.

For a real request, first record the requested hostname, protocol, port, time and timezone, and where the client was running. Record whether it failed once or repeatedly. A timeout, a name lookup failure, and an HTTP error response are different observations. Do not flatten them into “the network is down.”

The following checks are a conditional walkthrough for an authorized investigation, not a second reproduced outage. They were not exercised against a live network or service for this chapter. Use the actual approved target and the system's supported tools; do not probe arbitrary hosts.

### Start with what the local machine knows

An interface is a machine's network attachment, such as a Wi-Fi connection. An address identifies it on a network. A route tells the system which way to send traffic. These commands inspect local information without changing it:

```bash
ip address show
ip route show
ip -6 route show
```

`ip` is commonly supplied by the iproute2 package. `address show` lists interfaces and their addresses; `route show` lists IPv4 routes; `-6` selects IPv6 routes. An interface being up or a route existing does not prove packets reach the server. Compare the output with what that machine is supposed to have. Do not guess the expected address from someone else's screenshot.

A hostname must also be translated into an address. On systems with `getent`, this checks the system's configured host lookup mechanism:

```bash
getent ahosts example.com
```

`getent` queries system information sources; `ahosts` requests host address information. `example.com` is a documentation domain here: replace it with the approved hostname when investigating. Results can include repeated addresses for different socket types. A returned address is evidence that this lookup produced a result, not that a connection to the application succeeded. The result can come from configured sources other than DNS, such as a local hosts file.

### Ask the application a bounded question

If sending a request is authorized and a suitable HTTP client is installed, a limited request can separate connection problems from application responses:

```bash
curl --connect-timeout 5 --max-time 10 --head https://example.com/
```

`curl` sends the request. `--connect-timeout 5` limits its connection phase to five seconds; `--max-time 10` limits the whole operation to ten seconds. `--head` asks for response headers using HTTP's HEAD method instead of downloading a normal response body. The address selects HTTPS and its default port, 443. This is a network action, not merely a local inspection.

Do not run that command mechanically on production. Even a request can create access-log entries or trigger application work. HEAD is not supported identically by every application, so compare it with the request that actually fails. Do not disable certificate checks to turn a failed secure connection into an apparently successful test.

If an HTTP response arrives, some server answered at the application layer. That still does not prove the requested operation works. Without an option such as `--fail`, curl can return status zero for a successfully transferred HTTP error response. Read the HTTP status and the response, not just `$?`. Conversely, a timeout does not by itself tell you which router, firewall, or server caused the delay.

For a fair comparison, keep the hostname, protocol, port, address family, and request type consistent. Comparing IPv4 from one machine with IPv6 from another may investigate a different path without making that difference obvious.

### Look on the server only if it is yours to inspect

On the machine expected to run the service, `ss` can inspect listening TCP sockets, which are local endpoints waiting for connections:

```bash
ss -ltn
```

`-l` selects listening sockets, `-t` selects TCP, and `-n` shows numeric addresses and ports rather than translating them to names. A listener on a port shows that something is waiting there. It does not prove that it is the intended program, that it can read its data, or that remote clients can reach it. A listener bound only to the local loopback address is not the same as one accepting remote connections.

For a systemd-managed service, Chapter [10](10-services.md) explains service status and journal inspection. The journal is a collection of recorded system and service messages. Ask for the correct service and a small time window around the failed attempt rather than dumping every message on the machine. Other systems may use different logging tools.

Match a log entry to the attempt using time, service identity, and, when available, a request identifier. Check timezone differences. A nearby error is a lead, not proof of causation. No matching entry can mean the request never arrived, but it can also mean you chose the wrong log, lack access, or the application does not record that event.

Here is the connection to our report: a service can be running and accepting connections while its application cannot find an input file. “The service is active” is like “Bash started the script.” It confirms one step, not the entire chain.

## Know when to stop and ask for help

Our safe experiment had a clear owner, tiny disposable inputs, no external effects, and a correction we could reverse. A real investigation may have none of those properties.

Stop before a proposed test if it could overwrite data, resend a job, interrupt users, change access controls, or produce costs without approval. Stop if the next step requires privileges you do not have. A permission error is a boundary to understand, not an invitation to retry everything as root.

Do not deliberately reproduce suspected disk damage by writing more data. Do not reproduce a suspected attack against a real service. If data loss or a security incident is possible, preserve evidence according to the owner's procedure and involve the responsible team. Avoid broad “repairs” such as recursively loosening permissions, flushing firewall rules, killing every process with a matching name, or restarting unrelated services.

Before an authorized change, be able to name the exact target, the expected result, who approved it, who might be affected, how to undo it, and how you will check success. If you cannot answer those questions, gather read-only evidence or escalate rather than experimenting on other people's work.

A useful handoff is not a raw log dump. For our fixture, it would say:

> The report failed from the launcher directory with status 1 and an error opening the relative path `data/orders.txt`. Reading the intended input by its full path worked under the same account. Repeating the original invocation reproduced the failure. Changing only the starting directory to the report's main directory produced the expected report, status 0, and an empty error log. No live scheduler or service was investigated.

For a real incident, add the exact commands, time window, affected users or scope, relevant sanitized output, changes already made, and the questions that remain unanswered. Keep original evidence in an approved private location. Remove credentials, tokens, customer data, and unnecessary machine identifiers from copies you share. Logs can contain secrets even when the command used to read them is harmless.

## Remove the example files

Once you have finished comparing the two runs, remove only the files created here. `rm` removes the named files; `--` marks the end of options. `rmdir` removes directories only when they are empty, which makes unexpected extra files a reason to stop rather than delete more broadly.

Keep the same shell and check that `$case_dir` still names the generated example folder before running this block. `cd "$HOME"` moves out of the folder we are removing.

```bash
cd "$HOME"
rm -- "$case_dir/data/orders.txt" "$case_dir/report.sh" "$case_dir/failure.log" "$case_dir/success.log"
rmdir -- "$case_dir/data" "$case_dir/launcher"
rmdir -- "$case_dir"
```

Successful cleanup normally prints nothing. If a name is missing or a directory is not empty, read the error and inspect the target. Do not replace these narrow commands with a recursive deletion of a broader path. The disposable demonstration, including cleanup, was executed in a fresh scratch directory; no production service, account, network configuration, or installed package was changed.

## Further reading

- [Google SRE Book: effective troubleshooting](https://sre.google/sre-book/effective-troubleshooting/) explains how observations, possible explanations, and tests fit together in larger systems.
- [GNU Bash manual](https://www.gnu.org/software/bash/manual/bash.html) documents command execution, inherited working directories, redirection, and exit status.
- [Linux man-pages: proc(5)](https://man7.org/linux/man-pages/man5/proc.5.html) describes Linux's process and system information files for deeper inspection.
- [curl manual](https://curl.se/docs/manpage.html) documents time limits, response handling, and the meaning of curl's options.
