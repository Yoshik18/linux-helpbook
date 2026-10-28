# 7. CPU, memory and load

[Contents](../README.md) | [Previous: processes](06-processes.md) | [Next: storage](08-storage.md)

A report that normally finishes quickly is taking several minutes. The terminal still responds, and the program has not exited. Is the machine busy calculating, waiting for storage, or struggling to keep its working data in memory?

Those are different problems. Adding memory does not make a calculation use more processors. A program waiting for a file will not necessarily use much processor time. Before changing anything, we need to tell doing work apart from waiting to do it.

This chapter follows that slow report through a small set of read-only checks. The report and its displayed measurements are a **schematic example**, not an incident reproduced on a real server. The commands can inspect your own machine, but its numbers will differ. You do not need to create a heavy workload to learn how to read them.

## On this page

- [What the processor can do at once](#what-the-processor-can-do-at-once)
- [Why load is not a percentage](#why-load-is-not-a-percentage)
- [Start the investigation with two small checks](#start-the-investigation-with-two-small-checks)
- [Memory that is free and memory that is available](#memory-that-is-free-and-memory-that-is-available)
- [What swap does and does not tell you](#what-swap-does-and-does-not-tell-you)
- [Watch a short stretch of time with vmstat](#watch-a-short-stretch-of-time-with-vmstat)
- [Read the report example across several measurements](#read-the-report-example-across-several-measurements)
- [Find the program behind the numbers](#find-the-program-behind-the-numbers)
- [Where these measurements stop helping](#where-these-measurements-stop-helping)
- [Further reading](#further-reading)

## What the processor can do at once

A processor carries out instructions: compare values, add numbers, move data, and decide which instruction comes next. It is also called a **CPU**, short for central processing unit. A busy application needs both time on a CPU and access to the data it is working with.

A modern processor usually contains several **cores**, which can carry out work alongside one another. Some cores present more than one execution slot to the operating system. Linux calls those slots logical CPUs. Two logical CPUs on one physical core share some hardware, so they do not necessarily do as much work as two separate cores.

For an initial investigation, think in terms of the logical CPUs Linux can schedule work onto. Four logical CPUs offer four places for work to run at once. They do not promise that every program runs four times faster. A program must have work it can divide up to use all four.

A running program is a process. A process can contain several independently scheduled parts called **threads**. One application might have eight threads doing calculations, while another has just one. This is why counting application names is not enough to know how much processor work is waiting.

At any moment, a thread might be:

- **Running:** using a logical CPU now.
- **Ready to run:** able to continue, but waiting for a CPU to give it a turn.
- **Waiting for something else:** unable to continue until an event happens, such as a read finishing or another part of the application releasing a lock.

Linux often groups running and ready-to-run work under the word **runnable**. Work can be runnable without currently running.

CPU utilization measures how CPU time was spent during an interval. If all four logical CPUs were busy throughout an interval, an aggregate display can show close to 100% busy. If only one was busy and three were idle, the aggregate can show roughly 25% busy. The single working thread may still be using all the CPU time it can get. Low overall utilization does not prove that every application has spare capacity.

## Why load is not a percentage

Suppose four threads are calculating on four logical CPUs. Four more threads become ready. The CPUs are still fully busy, but now some work also has to wait. A busy-time percentage cannot show how long that queue has become: the CPUs cannot become more than fully busy.

Linux provides another measure, **load average**, to describe the amount of active or waiting work over time. It includes runnable tasks and tasks in a particular kind of wait called **uninterruptible sleep**. That wait is often associated with storage input or output, though storage is not its only possible cause. Input/output, usually shortened to **I/O**, means moving data to or from something such as a storage device.

Not every sleeping program contributes to load. A shell waiting for you to type, for example, normally does not. Nor does every network wait or application-lock wait belong to the uninterruptible category. “Waiting” is a useful everyday description, but Linux distinguishes several kinds of waiting.

A load average has no percent sign. A value of 6 means roughly six contributing tasks on average, not 6% or 600% CPU use. If those tasks are all runnable, six represents more demand than four logical CPUs can run at once. The same load would leave plenty of processor capacity on a much larger machine. If several tasks are blocked on I/O instead, a load of six can coexist with mostly idle CPUs.

That is the central distinction:

- CPU utilization asks, “How was the processors' time spent?”
- Load average asks, “How much runnable or uninterruptibly waiting work has there been?”

You need both questions because a queue can grow for reasons other than busy processors.

## Start the investigation with two small checks

First, ask how long the machine has been running and what its recent load averages are:

```bash
uptime
```

This command reads system information; it does not restart or change anything. A schematic result for the slow-report machine is:

```text
 14:20:00 up 6 days,  3:12,  1 user,  load average: 6.20, 3.10, 1.20
```

The first field is the current clock time. `up 6 days, 3:12` means the machine has been running for six days, three hours and twelve minutes since its last boot. The user count concerns login sessions, not the number of applications.

The three load values represent approximately the last one, five and fifteen minutes. These are smoothed averages, not three instantaneous task counts or three separate measurements of CPU percentage. Here the shortest-window value is highest. That is consistent with demand increasing recently, but it does not say which resource caused the increase. The averages also take time to fall after a busy period ends.

Next, ask how many processing units are available to the command you are running:

```bash
nproc
```

For our schematic machine:

```text
4
```

`nproc` needs no option here. Its result is a useful starting point for comparing runnable demand with CPU capacity. It is not a count of physical processor packages, and it need not equal the machine's advertised core count.

Programs may be limited to particular CPUs. Containers and service managers can also impose resource limits; a **control group** is one Linux mechanism used to group processes and enforce such limits. What `nproc` reports depends on the implementation, version and constraints it recognizes. Meanwhile, `uptime`, `free` and other tools in a container can expose broader host information. Do not assume all these tools describe the same boundary just because you ran them in the same terminal.

For now, our example assumes an ordinary machine with four available logical CPUs and no separate container limit. Load 6.20 gives us a reason to examine waiting work. It does not yet give us a diagnosis.

## Memory that is free and memory that is available

The processor needs somewhere to keep the instructions and data it is using. The fast working area is **RAM**, or random-access memory. Unlike saved files, its contents normally disappear when the machine loses power.

Linux does not leave all otherwise-unused RAM empty. If it has recently read a file, it can keep a copy of that file's contents in RAM. A second read may then avoid slower storage access. Such retained copies are a **cache**. Linux also uses memory for bookkeeping about files and other system objects.

This leads to a common misleading observation: a machine can have very little completely unused RAM while still having room to start another application. Some memory holds useful cached data that Linux can give up when an application needs space.

Inspect memory with:

```bash
free -h
```

`free` prints a memory summary. The `-h` option asks for human-readable sizes rather than long counts. `Mi` means mebibytes and `Gi` means gibibytes, units based on powers of 1024. The command only reads information.

Here is a schematic result for our report machine, using a recent procps layout:

```text
               total        used        free      shared  buff/cache   available
Mem:           8.0Gi       2.0Gi       300Mi        64Mi       5.8Gi       6.0Gi
Swap:          2.0Gi          0B       2.0Gi
```

Start with `Mem:` and read these fields in this order:

1. **`total`** is the usable physical memory reported by the kernel, the central part of Linux that manages hardware and processes. It can be less than the amount printed on a hardware specification because some memory is reserved.
2. **`free`** is memory currently unused. Here that is only `300Mi`.
3. **`available`** estimates how much memory could be provided to new applications without needing to move memory contents into swap. Here it is about `6.0Gi`, much more than `free`.
4. **`buff/cache`** groups memory used for buffers and caches. Much of it may be reclaimable, which means Linux can repurpose it. Not all of it can necessarily be reclaimed immediately.

The `used` calculation has changed between procps versions. In recent versions it is based on `total` minus `available`; older versions can calculate it differently. Do not build your understanding around a memorized sum of every displayed column. Human-readable rounding also prevents exact arithmetic from always matching.

The `shared` field is mostly memory used by memory-backed filesystems such as `tmpfs`. It is not simply “all memory shared between processes,” and it is not an extra amount to add to the other columns.

In the example, the small `free` value does not demonstrate a shortage. The much larger `available` estimate suggests Linux has substantial room to satisfy new demand. Cached file data is helping the machine, not automatically wasting memory.

That does not make the estimate a guarantee. Applications can demand memory suddenly, and a process can have a limit below the system total. Compare repeated readings with the symptoms rather than deciding from one number. Do not clear caches to make the `free` column look better: doing so can remove useful data and make subsequent reads slower.

## What swap does and does not tell you

Linux can move some memory contents that are not currently needed from RAM into a separate backing area. That area is called **swap**. It may be a file or a dedicated part of a storage device. Moving data there can leave more RAM for active work; using that data again may require bringing it back.

Swap is not more RAM with the same speed. Accessing ordinary disk-backed swap usually takes much longer than accessing RAM. Some systems use compressed memory for swap, so the exact cost and storage path vary.

The `Swap:` line in `free -h` reports how much swap exists, how much is occupied, and how much remains unused. In the example it is configured but empty. A machine without configured swap can show zero in all three fields; that alone is not an error.

An occupied swap area is not proof of a current problem. Linux may have moved rarely used data out earlier and left it there. The question is not just “Is something in swap?” but “Is data moving in and out now, and does that coincide with the delay?”

If an application keeps needing data that is being moved out of RAM, repeated movement can become a large part of its work. That is a possible sign of **memory pressure**: workloads are competing for insufficient readily usable memory. Low and falling `available`, continuing swap transfers, and worsening response time together support that explanation more strongly than any one reading does.

Even without swap, memory pressure can cause slowdowns while Linux reclaims caches and other reclaimable memory. A lack of swap transfers does not rule it out. Under severe pressure, allocations may fail or Linux may terminate a process to recover memory. Changing swap configuration is not a first diagnostic step on a shared machine.

## Watch a short stretch of time with vmstat

Our two snapshots leave questions open. Was the report briefly busy or continuously waiting? Is swap merely occupied, or actively moving data? We need measurements across time.

The command `vmstat` prints several kinds of activity together, including processor use, memory, and waiting processes. Despite its name, it is not limited to memory. On systems with the procps version installed, run:

```bash
vmstat 1 5
```

The first number, `1`, requests one second between reports. The second, `5`, limits the output to five reports, after which the command exits. The first report normally appears immediately, so this is not five full one-second intervals: there are four subsequent intervals. Without the final count, sampling would continue until interrupted.

Here is a complete **schematic** five-report example. It uses a common column layout; your version may add columns, including `gu` for time running virtual-machine guest code.

```text
procs -----------memory---------- ---swap-- -----io---- -system-- ------cpu-----
 r  b   swpd   free   buff   cache   si   so    bi    bo   in   cs us sy id wa st
 1  0      0 307200 131072 5955584    0    0    20    10  300  600 10  3 87  0  0
 7  0      0 306000 131072 5955584    0    0     0     0 1400 2800 90  8  2  0  0
 8  0      0 305000 131072 5955584    0    0     0     8 1500 3000 91  8  1  0  0
 6  0      0 306000 131072 5955584    0    0     0     0 1300 2600 89  9  2  0  0
 7  0      0 306000 131072 5955584    0    0     0     4 1450 2900 90  8  2  0  0
```

There is one crucial timing distinction. In the **first data row**, CPU percentages and activity rates summarize time since boot. In later rows, those fields describe the interval since the previous report. Process counts and memory amounts are current snapshots even in the first row. The first row is therefore not simply “what happened during the first second.”

In this example, do not conclude that CPU use jumped from 10% to 90% in one second. The 10% `us` value describes a much longer history. Read the later four rows to discuss the current short sample.

### First read the work and CPU columns

The leftmost columns describe work that can run or is blocked:

- `r` counts runnable work, including work already running as well as work waiting for CPU time. It is not just the length of the waiting queue.
- `b` counts processes blocked waiting for I/O. It is not a count of every sleeping application or every kind of application wait.

The CPU columns are percentages of aggregate CPU time:

- `us` is time running application code, called user time. “User” here does not mean someone is typing.
- `sy` is time running kernel code, such as carrying out an application's request to the operating system.
- `id` is idle time.
- `wa` is time accounted as waiting for I/O while the CPU is otherwise idle.
- `st` is time taken away from a virtual machine because its underlying host was using the processor elsewhere, called steal time.

Read labels rather than assuming all versions have the same number of columns. Rounding and additional categories can affect totals.

`wa` is not the percentage of a disk's capacity in use, and it is not the time a particular read took. On machines doing many things at once, it is especially easy to overinterpret. A low `wa` value does not prove that every storage request is fast.

### Then read amounts separately from rates

`swpd` is an amount of swap occupied now. `free`, `buff` and `cache` are memory amounts. The usual default for these fields is KiB, or kibibytes. Unlike `free -h`, this plain `vmstat` invocation does not automatically attach convenient size suffixes.

`si` and `so` are rates: memory swapped in and swapped out per second. Their units follow the memory unit setting; with the usual default they are KiB per second. A steady `swpd` value with `si` and `so` both zero means something different from continuous transfers.

`bi` and `bo` report block-device input and output rates, not just swap. File reads and writes can appear here too. Consult your installed manual for units, especially when comparing older implementations. The current procps manual documents these as KiB per second.

`in` counts interrupts per second, events that need processor attention. `cs` counts context switches per second, times Linux changes which task is running. These are useful for more detailed investigation, but neither has a universal “bad” threshold. You do not need to diagnose them to understand our report example.

### A small input mistake

The report count must be a number, not a word. This deliberately incorrect command was tested:

```bash
vmstat 1 five
```

The tested procps version reported this error and exited with status 1, meaning failure:

```text
vmstat: failed to parse argument: 'five'
```

That is a command-input error, not evidence that the machine is overloaded. Correct the argument to the digit `5`:

```bash
vmstat 1 5
```

If a tool instead reports that the command was not found, the program may be absent from a minimal installation. Use the system's approved software-installation process rather than treating a missing utility as a performance symptom.

## Read the report example across several measurements

We now have a connected set of observations for the schematic report machine:

- Four logical CPUs are available.
- The one-minute load is above four and higher than the longer-window averages.
- `free -h` estimates substantial memory available, despite little completely unused RAM.
- The interval rows in `vmstat` show six to eight runnable tasks, almost no idle CPU time, no blocked tasks at the sampled moments, and no swap transfers.

Together, these support a specific next question: which work is competing for CPU time? They do not suggest clearing caches or changing swap. They also do not prove that the report is the source of the load. Another application could be occupying the processors while the report waits its turn.

The process and memory fields are snapshots, so short events can occur between samples. Four intervals are enough to illustrate a pattern, not enough to establish an hour-long trend. If the symptom lasts longer, take another bounded sample while it is happening and compare with a quieter period under a similar workload.

### What if the same load came from blocked work?

Keep the four-CPU machine and a load average near six, but suppose later samples instead look like this. These are **selected schematic columns**, not the full output of another command:

```text
r  b  us sy id wa
1  5   8  4 58 30
1  4   7  3 65 25
2  5  10  5 50 35
```

Here the CPUs have substantial idle time, few tasks are runnable, and several are blocked. The high load no longer points mainly toward a shortage of processor time. Investigate the waiting work and storage path next, using the next chapter. Busy or slow storage is a possibility, not a conclusion: these numbers do not identify a device or explain why requests are delayed.

### What if memory became the limiting resource?

Now consider a different later observation: repeated `free -h` readings show `available` falling, the report gets slower, and the following selected **schematic** `vmstat` fields appear:

```text
swpd    si    so
524288  4096  8192
532480  6144 12288
540672  8192 16384
```

Swap is occupied and transfers continue in both directions. With falling available memory and the matching slowdown, this is stronger evidence of memory pressure than the swap amount alone. Find which processes or workload changes are increasing memory demand before choosing a remedy.

If instead `swpd` remained nonzero while `si` and `so` stayed at zero and the machine responded normally, the occupied swap would not by itself justify an intervention. An amount describes what is there; a rate describes what is happening.

## Find the program behind the numbers

System totals do not identify the application responsible. To connect them to processes, open the changing display introduced in the previous chapter:

```bash
top
```

`top` normally takes over the terminal and refreshes its display. Press `q` to leave it. Its initial layout and sorting can depend on saved settings and the installed version. Read the headings rather than assuming the first process is always the one you need.

The header combines load, CPU and memory information. The process rows let you relate activity to a process ID and command. Compare repeated refreshes while the report is slow rather than trusting one row at one instant.

A process's CPU percentage can use a different scale from the aggregate CPU header. In a common `top` mode, one fully occupied logical CPU corresponds to about 100% for a process. A multithreaded process can then exceed 100%. Do not compare that directly with the whole-machine percentage without checking the display mode.

Memory columns need similar care. Resident memory is memory currently held in RAM for a process. Some of it can be shared with other processes, so adding every process's resident amount can count the same memory more than once. A large virtual-memory figure describes address space, not necessarily RAM actually occupied. A growing resident amount across repeated observations is worth investigating, but one large value does not establish a leak.

For our CPU-heavy schematic case, look for persistently busy processes and check whether they belong to the expected report workload. A program using CPU to do useful calculations is not automatically malfunctioning. Do not terminate an unfamiliar process simply because it is near the top of a display.

## Where these measurements stop helping

A slow application can wait for a remote server, a database query, an application lock, or a request in its own internal queue while the local machine has plenty of CPU and available memory. Normal-looking system totals do not prove that the application is healthy. They tell you to widen the investigation rather than force a CPU or RAM explanation.

Likewise, a short busy period can be entirely expected. Compare measurements with what the machine was asked to do and when the symptom began. “The report took longer while another calculation was running” is more useful than “the load looked high.”

On a virtual machine, persistent steal time may point outside the guest. In a container, check its assigned limits before trusting host-wide capacity figures. More advanced Linux facilities, such as Pressure Stall Information, can measure time workloads lose waiting for CPU, memory or I/O resources; the kernel documentation below explains their scope.

All commands in the main investigation read information. They create no workload to stress the system and require no system cleanup. Their readings describe your current environment; the report scenarios above are illustrations of how to reason about those readings, not values your machine should match.

Do not create stress loads on a shared machine to try to reproduce the examples. The useful habit is to connect an existing symptom to repeated observations, identify the likely kind of waiting, and only then consider an approved change.

## Further reading

- [Linux man-pages: proc(5)](https://man7.org/linux/man-pages/man5/proc.5.html)
- [Linux man-pages: proc_loadavg(5)](https://man7.org/linux/man-pages/man5/proc_loadavg.5.html)
- [GNU Coreutils: nproc](https://www.gnu.org/software/coreutils/manual/html_node/nproc-invocation.html)
- [procps-ng: free](https://man7.org/linux/man-pages/man1/free.1.html)
- [Linux kernel documentation: PSI](https://docs.kernel.org/accounting/psi.html)
- [procps-ng: vmstat(8)](https://man7.org/linux/man-pages/man8/vmstat.8.html)
- [procps-ng: top(1)](https://man7.org/linux/man-pages/man1/top.1.html)
