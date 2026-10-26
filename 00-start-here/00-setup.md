# Choose a safe practice environment

A Linux command can change the machine where you run it. Use a disposable [virtual machine](../glossary.md#virtual-machine) that you control, with no personal files, work credentials or production access. For the first lesson, you only need an existing Linux environment and a [terminal](../glossary.md#terminal); its commands inspect information without changing settings.

## Tested baseline

The first lesson's commands were executed on 2026-10-26 in an isolated hosted Debian sandbox. Its virtualization detector reported KVM. That identifies the reported virtualization context; it does not establish that the sandbox has all the features of a normally installed Debian server.

| Component | Observed version |
|---|---|
| Debian | 13.7, trixie |
| Bash | 5.2.37 |
| GNU coreutils | 9.7 |
| Running Linux kernel | 6.1.158+ |
| Reported machine architecture | x86_64 |

These are the exact tested versions, not instructions to install arbitrary newer releases or a claim that the provider's image is immutable. No image, package download or installer is used in this first increment. Each future lab must pin its own provisioning dependencies before it can be called reproducible.

Your system's reported release and architecture may differ. Do not upgrade, downgrade or replace a kernel merely to match sample output.

## What you need before the first lesson

1. Open a terminal inside the disposable Linux environment, not a terminal on a different host.
2. Use an ordinary account rather than an administrative session. The first lesson needs no administrator permissions.
3. Make sure you can discard the environment without losing useful data. Do not attach work disks, copy credentials into it or expose services publicly.
4. Read [how to use the course](01-how-to-use-this-repo.md), then follow the first lesson listed in [ROADMAP.md](../ROADMAP.md).

## Provisioning is outside the verified scope

> UNVERIFIED: Creating and deleting a fresh learner VM has not been tested for this course. The verified environment was an already provisioned hosted sandbox. Do not treat this page as an end-to-end installation or VM lifecycle lab.

If you do not already have a suitable environment, use the official Debian installation guide with a virtualization application you understand, or ask for a tested setup guide for your host platform. Stop if you cannot identify the target disk. Do not install over an existing disk that contains data you need.

This first increment has no cloud provisioning steps and no required paid resources. Do not create a cloud server just to follow it. Future cloud labs require a dated cost estimate, a sandbox account with budget alerts, and verified teardown as their last step.

## Environment limits

The current sandbox has not established a working systemd service manager. Service management, package changes, mounts, boot recovery and privileged networking operations are not covered by the first lesson's evidence. A [container](../glossary.md#container) is useful for many command-line exercises, but must not be presented as a full server booting its own kernel.

The first lesson is read-only: it creates no files or resources, so no lesson cleanup is needed. If you independently provision a VM, its lifecycle remains your responsibility; this course has not verified that teardown route.

## Further reading

- [Debian 13 installation guide for amd64](https://www.debian.org/releases/trixie/amd64/)
- [Debian installer information](https://www.debian.org/releases/trixie/debian-installer/)
- [Linux kernel KVM documentation](https://docs.kernel.org/virt/kvm/index.html)
