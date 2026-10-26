# 13. Security basics

[Contents](../README.md) | [Previous: troubleshooting](12-troubleshooting.md) | [Next: shell scripts](14-shell-scripts.md)

Linux security is a set of controls, not a single setting or command. Identity, file permissions, process isolation, network exposure, software updates and audit evidence work together. A configuration that is appropriate for one machine can be wrong for another, especially when services and organizational policies differ.

## Use least privilege

Run day-to-day work as an ordinary account. Use administrative privileges only for a specific, understood action. Before `sudo`, read the full command and confirm every path and argument. A typo with elevated access can damage files that the ordinary account could not change.

Inspect identity and group membership with `id`. Inspect a file's owner and mode with `ls -l`. These are useful first checks, but access may also depend on ACLs, namespaces, mount flags and mandatory access controls such as SELinux or AppArmor.

## Keep software sources trustworthy

Install updates through the distribution's supported package manager and configured repositories. Verify repository instructions with the vendor or organization responsible for the machine. Adding a repository or key changes the software trust boundary. Do not run copied installation commands that download and execute code as root without reviewing their source and effect.

## Reduce exposed services

A listening socket is a possible network entry point, not by itself a vulnerability. Identify the owning service and whether it needs to listen on that address and port. Firewalls, reverse proxies and network controls affect exposure, but they do not replace application authentication or patching. Do not alter firewall rules on a live system without the service owner's change plan and a recovery path.

## Protect secrets

Do not place passwords, access tokens or private keys in shell history, public repositories, screenshots or support logs. Restrict secret-file permissions and use an approved secret manager where available. If a secret is exposed, treat it as compromised and rotate it through the responsible service's process; deleting the visible copy alone may not remove it from history or backups.

## Understand security limits

A successful `uname`, package inventory or permission listing does not establish that a system is secure. Security depends on current configuration, patch state, reachable services, threat model and operational practices. Use the organization's approved baseline and incident process rather than improvising hardening commands from an unrelated distribution guide.

## Common mistakes

- Treating `sudo` as a general fix for permission errors.
- Disabling a security control to make an application start without understanding why it denied access.
- Assuming a closed port means an application is safe, or an open port means it is vulnerable.
- Pasting secrets into a terminal command that will be saved in shell history.
- Claiming a machine is secure based on a few point-in-time checks.

## Further reading

- [Linux man-pages: capabilities(7)](https://man7.org/linux/man-pages/man7/capabilities.7.html)
- [SELinux project documentation](https://selinuxproject.org/page/Main_Page)
- [AppArmor documentation](https://apparmor.net/)
- [NIST: Guide to General Server Security](https://csrc.nist.gov/pubs/sp/800/123/final)
