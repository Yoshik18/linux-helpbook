# 6. Processes and signals

[Contents](../README.md) | [Previous: permissions](05-permissions.md) | [Next: resources](07-resources.md)

You start a command, but the terminal does not give you another prompt. Is the command busy, waiting for something, or stuck? You open another terminal and find several commands with the same name. Which one belongs to the work you just started?

Linux gives each running process an identity. Learning to read that identity lets you investigate before interrupting anything. In this chapter, we will start a harmless waiting command, find it, pause it, continue it, and finally end it. The same questions apply to larger programs, but the consequences of interrupting a real application can be much greater.

## In this chapter

- [A program is not the same thing as a process](#a-program-is-not-the-same-thing-as-a-process)
- [Start a waiting process without losing the prompt](#start-a-waiting-process-without-losing-the-prompt)
- [Read the process you just started](#read-the-process-you-just-started)
- [What a process state tells you](#what-a-process-state-tells-you)
- [Move between foreground and background](#move-between-foreground-and-background)
- [Ask your own process to finish](#ask-your-own-process-to-finish)
- [Why KILL is different](#why-kill-is-different)
- [Find candidates without guessing at a target](#find-candidates-without-guessing-at-a-target)
- [Further reading](#further-reading)

## A program is not the same thing as a process

A program is a set of instructions that the machine can run. Many programs are stored as executable files: for example, the `sleep` command is a program that waits for a specified amount of time. A file on disk does not consume processor time merely because it exists.

When you run that program, Linux creates the working machinery needed to carry out its instructions: memory, information about open files, an identity, and a current position in the instructions. That running instance is a **process**. A process can be alive even when it is waiting and has no work for the processor to do.

You can start the same program twice. The two processes use the same program instructions, but they have separate identities and can finish at different times. Ending one does not delete the program or automatically end the other.

Your shell is also a process. It reads what you type and starts other commands for you. A process that starts another process is its **parent**; the newly created process is its **child**. This relationship describes how processes are connected, not a promise that their lifetimes will be identical. A child can finish before its parent, and in some circumstances it can outlive its original parent.

Linux assigns a number called a **process ID**, usually shortened to **PID**, to identify a process. Its parent's number is the **parent process ID**, or **PPID**. A PID is not a permanent name: after a process ends, Linux can eventually reuse its number for an unrelated process. This matters whenever you use a number to send a signal.

Before exploring that, try the smallest waiting command in an interactive Bash terminal:

```bash
sleep 2
```

The number `2` means two seconds. There is normally no output. The prompt disappears while the shell waits for `sleep` to finish, then returns. Nothing was broken during the silence. The command was doing exactly what you requested.

A command that occupies the terminal this way is in the **foreground**. Until it finishes or you interrupt or suspend it, the shell is not accepting another command at its normal prompt. This is different from the terminal application itself freezing.

## Start a waiting process without losing the prompt

Use one Bash terminal for the connected example below. A new terminal with no existing background work makes the job numbers easier to follow. We will affect only the `sleep` processes we start ourselves. No administrator access is needed.

This time, let the waiting command run for five minutes, but ask the shell to return the prompt immediately:

```bash
sleep 300 &
```

The `&` belongs to the shell, not to `sleep`. It tells Bash to start this command in the **background**, allowing you to enter another command while it continues. The waiting process still exists. Background does not mean finished, hidden, or disconnected from the terminal.

Illustrative output, with numbers that will differ on your machine:

```text
[1] 24680
```

The two numbers identify different things:

- `[1]` is Bash's job number for this work in this shell.
- `24680` is the PID of this simple background command.

A **job** is work the shell tracks as a unit. Our job contains one process. A pipeline can contain several processes while still being one shell job, so job number and PID should not be treated as interchangeable.

Save the PID without copying a number from the screen:

```bash
pause_pid=$!
```

`pause_pid` is a variable name we chose. There are no spaces around `=`. The special shell value `$!` is the PID of the most recently started background job. Save it immediately after starting our command, before starting any other background work. For our one-command job, it is the PID we want.

You can display the saved value:

```bash
printf '%s\n' "$pause_pid"
```

`printf` prints formatted text. The format `'%s\n'` means print the supplied value as text, then start a new line. `"$pause_pid"` asks Bash to insert the variable's value as one argument. You should see the same PID that appeared beside the job number. The quotes are a useful habit whenever a variable is passed to a command.

If five minutes pass while you are reading, the process will finish naturally. That is not a failure. Start `sleep 300 &` again and save `$!` again before continuing. Do not carry an old PID forward and assume it still identifies your work.

## Read the process you just started

The `ps` command reports information about processes. Rather than begin with the whole machine, ask for our one process:

```bash
ps -p "$pause_pid" -o pid,ppid,user,stat,etime,args
```

`-p` selects the PID supplied next. `-o` chooses the output columns; the comma-separated words are field names, not shell commands. The spelling here is for the procps-ng version of `ps` commonly supplied on Linux.

Illustrative output:

```text
    PID    PPID USER     STAT     ELAPSED COMMAND
  24680   24600 student  S          00:12 sleep 300
```

Read across the row:

- **PID** is this process's number, matching the value you saved.
- **PPID** is its parent's number. Here the parent is the Bash shell that started it.
- **USER** is the account whose permissions the process is using, reported here as its effective user. Expect your own account for this example.
- **STAT** describes the process's current state. `S` means it is waiting in a way that can be interrupted. For `sleep`, waiting is the purpose of the program.
- **ELAPSED** is how long the process has existed. `00:12` means twelve seconds, not twelve seconds of processor work.
- **COMMAND** comes from the `args` field. It shows the command and its arguments, helping us distinguish `sleep 300` from some other waiting command.

To check the parent relationship, print this shell's own PID:

```bash
printf '%s\n' "$$"
```

`$$` is Bash's PID in this interactive shell. Its value should match the `PPID` in our `sleep` row. The two processes are separate: the shell is reading your next command while its child waits.

If `ps` prints only a heading and no process row, it did not find a visible process with that PID at that moment. Perhaps the five minutes ended. Do not respond by sending signals to nearby numbers. Recreate the example and capture its new PID.

Linux also offers a more detailed view through `/proc`. This is a special directory whose contents are supplied by the running kernel, rather than ordinary documents stored permanently on disk. Inspect our process's status with:

```bash
cat "/proc/$pause_pid/status"
```

`cat` prints the named file. Bash inserts the saved PID into the path, so it reads our process's `status` entry. Look near the beginning for `Name`, `State`, `Pid`, and `PPid`; they describe the same identity and state that `ps` presented more compactly. You do not need to understand every memory or signal field yet.

An error saying the file does not exist can simply mean the process ended before `cat` opened the entry. A process list is not a reservation that keeps a process alive.

## What a process state tells you

A process does not continuously use the processor from the moment it starts until the moment it ends. It can spend most of its life waiting for a timer, keyboard input, disk activity, or a reply from another program. The kernel tracks which processes are ready to work and gives them opportunities to run. This sharing of processor time is called **scheduling**.

The first letter in `ps`'s `STAT` field is useful for understanding what is happening:

| Letter | Meaning | What to infer, and what not to infer |
| --- | --- | --- |
| `R` | Running, or ready to run when processor time is available | It has work it can do. One snapshot does not tell you how much processor time it has used. |
| `S` | Interruptible sleep | It is waiting for something. This is normal for many healthy programs, including our `sleep`. |
| `D` | Uninterruptible sleep | It is waiting in a kernel operation, often involving input or output. Investigate the resource it is waiting for rather than repeatedly sending signals. |
| `T` | Stopped by a job-control signal | Its execution has been suspended. It still exists and can be continued. |
| `Z` | Zombie | It has finished, but its parent has not yet collected its exit information. It is not still doing application work. |

Other state codes exist. You may also see extra characters after the first letter. For example, `+` marks membership in the terminal's **foreground process group**, the set of processes the terminal treats as its current foreground work. This matters for a pipeline: a keyboard interrupt can reach the group rather than only one command. Extra markers are not additional independent states and are not, by themselves, error flags.

The word “sleep” in a process state is broader than the command named `sleep`. A web server waiting for a request may also show `S`. Likewise, Bash can call a background job “Running” while `ps` shows `S`: Bash means the job is active rather than stopped or finished, not that it is using a processor at that exact instant.

A zombie does not need a stronger termination signal. Its application execution has already ended. Normally the parent collects the exit information promptly. Persistent zombies call for investigation of the parent and how it manages children, not attempts to kill the already-finished child.

## Move between foreground and background

Our waiting command is currently in the background. Ask Bash what jobs it is tracking:

```bash
jobs -l
```

`jobs` is part of Bash. The `-l` option includes process IDs. Illustrative output:

```text
[1]+ 24680 Running                 sleep 300 &
```

The `+` marks the current job, the one Bash would normally select if you used `fg` without an explicit job number. It does not mean elevated permissions or high priority.

`jobs` knows about this shell's jobs, not all processes owned by your account. Opening a second terminal starts another shell with a different job list. A process may therefore appear in `ps` but not in that second shell's `jobs` output.

Bring our job into the foreground:

```bash
fg %1
```

`fg` means foreground. `%1` selects job 1 from this shell's job list; it is not PID 1. If your job number differs, use the number shown by your own `jobs -l`. Bash prints the command and waits for it. The prompt disappears again because `sleep` is now the foreground job.

While it is still waiting, hold **Ctrl** and press **Z** once. Do not type the characters `Ctrl+Z` as a command. With normal interactive terminal settings, this asks the foreground work to suspend. Bash should return a prompt and report that `sleep` is stopped.

Now inspect both views:

```bash
jobs -l
ps -p "$pause_pid" -o pid,ppid,user,stat,etime,args
```

`jobs` should report `Stopped`, and `ps` should show `T`. The PID remains the same. The process has not finished or been started again; it has paused. A stopped process can still hold memory and open files, so suspending work is not a substitute for ending it.

Resume it in the background:

```bash
bg %1
```

`bg` continues the selected stopped job without making it the foreground job. The prompt remains available. A subsequent `jobs -l` should report `Running` again, although `ps` will normally show our waiting process as `S`.

To end this first waiting process through the terminal, bring it forward once more:

```bash
fg %1
```

This time press **Ctrl+C**. Under normal settings, the terminal sends an interrupt signal, named `INT`, to the foreground process group. Our simple `sleep` exits, and the prompt returns. Pressing Ctrl+C at an idle prompt is not a way to select and end arbitrary background work.

Check the job list:

```bash
jobs
```

With no other jobs, it should be empty. If you now try `fg %1` again, Bash reports an error such as:

```text
bash: fg: %1: no such job
```

That error means the shell no longer has that job to foreground. It does not mean `fg` is missing. The correction is to check `jobs` first and use an existing job number. If you want another waiting process, start a new one rather than trying to revive an exited process.

These controls require an interactive shell with job control and normal terminal settings. They are not instructions to paste into a script. A full-screen application may handle Ctrl+C differently, and a background command that tries to read the terminal may be stopped until you bring it forward. Background work can also still print into your terminal.

Finally, `&` is not a promise that work will survive closing the terminal or logging out. Long-running services need deliberate management, covered in [Boot, services and logs](10-services.md).

## Ask your own process to finish

Ctrl+C is convenient for foreground work. To address a particular process from the prompt, Linux provides **signals**: named notifications that can request actions such as interrupting, stopping, continuing, or terminating a process.

The command named `kill` sends signals. Its name is misleading because not every signal ends a process. Bash provides its own `kill` command, which is the one normally used in these examples.

Start another waiting process and save its new identity:

```bash
sleep 300 &
pause_pid=$!
```

The old process is gone; its saved PID was not reusable knowledge. Before acting on the new one, inspect it again:

```bash
ps -p "$pause_pid" -o pid,ppid,user,stat,etime,args
```

For this example, look for your account, the expected shell parent, a recent elapsed time, and `sleep 300`. If the row is absent or does not describe your waiting command, stop here and investigate. A name alone is not enough to establish identity.

Once it is confirmed, request termination:

```bash
kill -TERM "$pause_pid"
```

`-TERM` selects the termination signal, also called `SIGTERM`. If no signal is specified, `kill` normally sends TERM, but naming it makes the intent visible.

TERM gives an application an opportunity to follow its own shutdown procedure. A program might finish writing a file or release a resource before exiting. It can also choose to ignore or handle the signal without exiting. Our `sleep` has no elaborate shutdown work and normally ends immediately.

Successful `kill` commonly prints nothing. Bash may separately print a notification saying `Terminated`. Neither the lack of output nor a successful signal request alone proves the application's shutdown is complete.

For this particular child of our shell, ask Bash to wait for its completion and report the result:

```bash
wait "$pause_pid"
printf '%s\n' "$?"
```

`wait` waits for this shell's child to finish, or reports its already-known result. It is not a general way to wait for an unrelated system process. If a child has not exited, `wait` can itself keep waiting.

`$?` is the previous command's exit status, the small numeric result the shell records when a command finishes. Read it immediately; another command would replace it. In the tested Bash example, termination by TERM made `wait` return `143`. This is a shell convention for termination by a signal, not the PID and not evidence that sending TERM failed.

Confirm the result with the same inspection command:

```bash
ps -p "$pause_pid" -o pid,ppid,user,stat,etime,args
```

Normally, after `wait` has collected this child's result, only the heading remains. The process has ended and is no longer listed. `jobs` should also have no remaining job from this example. That is the cleanup: there are no example files to remove and no waiting process left running.

If a process disappears between inspection and signaling, `kill` may report `No such process`. That is a reason to refresh your understanding, not to retry old numbers or add administrator privileges. An `Operation not permitted` error means you lack permission to send that signal to the target. It does not justify using `sudo` against a process you have not been authorized to manage.

## Why KILL is different

Sometimes a program does not finish after TERM. It may be performing legitimate shutdown work, ignoring the request, or stuck waiting for something else. Allow an appropriate shutdown period and inspect it again. Five seconds may be ample for a toy command and wholly inadequate for a large database.

A stronger signal, `KILL`, forces termination without allowing the application to catch or ignore it. This also prevents its normal cleanup. Unsaved work may be lost, and application-managed files or related work may be left incomplete. The kernel still releases the process's own resources as it exits; that is not the same as the application finishing a transaction or saving a document.

The syntax for an escalation against the **same still-existing, freshly confirmed process that you own** is:

```bash
kill -KILL "$pause_pid"
```

This is a conditional example, not the next step after the successful TERM sequence above. That sequence should already have removed our process. Do not run KILL on the stale value just because it appears next on the page. The KILL command was tested separately against another newly created disposable `sleep`, not against a real service or an unresponsive production application.

KILL is not a universal immediate fix. A process in an uninterruptible kernel wait, often shown as `D`, may not disappear until that operation allows it to finish exiting. More signals do not repair a failed disk or release a resource held elsewhere. Nor does signaling a parent necessarily end all of its children. Large applications need an understanding of their own process structure.

For a managed service, use the service manager's supported shutdown procedure when authorized, rather than picking a child from `ps`. A supervisor may start a replacement as soon as a process dies. A new PID afterward can mean an automatic restart, not that the old process survived KILL.

## Find candidates without guessing at a target

Our saved `$!` gave us a useful starting point because we created the process. On an unfamiliar system, you may know only a program name. Process searches can narrow the list, but they do not authorize a state change.

While your own waiting process is alive, you can find direct children of this shell named exactly `sleep`:

```bash
pgrep -P "$$" -a -x sleep
```

`pgrep` searches process records. Here, `-P` restricts matches to processes whose parent is this shell, `-a` prints command arguments along with the PID, and `-x` requires the whole process name to match `sleep`. These procps-ng options make a more focused search than a loose name fragment. The result should include the current `sleep 300` if it is still alive. If you already finished the example, no match is expected.

With no matches, `pgrep` normally prints nothing and returns status 1. That is a meaningful search result, not necessarily a broken command. Even with an exact name, several results are possible if you started several instances. Process names and command lines also are not proof of trustworthiness; they are clues to combine with owner, parent, start time, and knowledge of the workload. Some implementations limit the process-name field they search, so check their manual before depending on long names.

For a wider read-only view, use:

```bash
ps -eo pid,ppid,user,stat,comm --sort=pid
```

`-e` selects all processes visible in your environment. `-o` again selects columns. Here `comm` shows the command name rather than the full arguments selected by `args`. `--sort=pid` orders rows by PID. More rows give you context, not permission to stop anything. Containers and access restrictions can also limit what you can see; “all” does not necessarily mean every process on the physical host.

`ps` is a snapshot. To watch changing activity, `top` provides an updating display:

```bash
top
```

Press `q` to quit `top` and return to the prompt. Merely opening this display and quitting is inspection; avoid its process-control commands while learning. Fields and keys vary by implementation. A high processor percentage is not enough to identify a fault: consider how long it lasts, whether the work is expected, and whether users are affected. The [next chapter](07-resources.md) explains that resource view.

The safest habit is to separate discovery from action. First find candidates. Then establish which process belongs to which work and whether you are responsible for it. Only then choose an appropriate way to stop it, and check the result. Avoid broad name-based termination commands: an innocent-looking name may belong to several unrelated tasks.

## Further reading

- [GNU Bash manual: job-control basics](https://www.gnu.org/software/bash/manual/html_node/Job-Control-Basics.html)
- [GNU Bash manual: job-control builtins](https://www.gnu.org/software/bash/manual/html_node/Job-Control-Builtins.html)
- [procps-ng: ps(1)](https://man7.org/linux/man-pages/man1/ps.1.html)
- [Linux man-pages: proc(5)](https://man7.org/linux/man-pages/man5/proc.5.html)
- [Linux man-pages: signal(7)](https://man7.org/linux/man-pages/man7/signal.7.html)
- [procps-ng project and manuals](https://gitlab.com/procps-ng/procps)
