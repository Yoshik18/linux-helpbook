# 15. Connect to another machine with SSH

[Contents](../README.md) | [Previous: shell scripts](14-shell-scripts.md) | [Next: archives](16-archives.md)

A report is on another Linux machine, and its owner has given you an account to retrieve it. You do not need to sit at that machine's keyboard. You can open a terminal on your own computer, connect to the other machine, and work there through the network.

The program commonly used for this is **SSH**, short for Secure Shell. It encrypts the connection, but it does not decide whether a command is sensible or whether you are allowed to read a particular file. Those questions still depend on the account, its permissions, and the owner's rules.

This chapter follows that report example. The remote steps are a conditional walkthrough, not a record of a tested connection. Run them only for a machine you are authorized to use, with details supplied by its owner. `reports.example.com`, `learner`, port `2222`, and the remote paths below are documentation placeholders. They do not describe an available server. Without an authorized destination, you can still read the walkthrough and try the local key and configuration examples.

## In this chapter

- [Which machine receives your commands?](#which-machine-receives-your-commands)
- [Get the destination details first](#get-the-destination-details-first)
- [Check the server before trusting it](#check-the-server-before-trusting-it)
- [Work remotely, then return locally](#work-remotely-then-return-locally)
- [Understand the two halves of a login key](#understand-the-two-halves-of-a-login-key)
- [Create a separate key without replacing another](#create-a-separate-key-without-replacing-another)
- [Authorize the public key and select the private key](#authorize-the-public-key-and-select-the-private-key)
- [Let an agent remember an unlocked key](#let-an-agent-remember-an-unlocked-key)
- [Keep connection settings in a small file](#keep-connection-settings-in-a-small-file)
- [Copy the report in the right direction](#copy-the-report-in-the-right-direction)
- [Find the stage that failed](#find-the-stage-that-failed)
- [Remove the practice key when finished](#remove-the-practice-key-when-finished)
- [Further reading](#further-reading)

## Which machine receives your commands?

Before connecting, your terminal runs a command-reading program, usually a shell, on your own computer. We will call this the **local** machine. A command such as `pwd` reports a directory on that machine.

After an interactive SSH login succeeds, the same terminal displays a shell running on the other computer. That is the **remote** machine. Typing `pwd` there reports a remote directory. Typing `rm` there removes remote files, subject to your remote account's permissions. Your local files do not automatically appear on the remote machine.

The terminal window has not moved. The place where its input is being used has changed:

```text
Before login: keyboard → local shell → local files
During login: keyboard → SSH connection → remote shell → remote files
After logout: keyboard → local shell → local files
```

A prompt may change after login, but prompts can be customized. Treat a familiar-looking prompt as a reminder, not proof of where you are. If you have several terminals open, keep one clearly identified for the remote session. Do not start another SSH session from inside it unless you intentionally want a connection from that remote machine.

## Get the destination details first

You need more than “the server.” Ask its owner for:

- The machine's network name or address, called its **host name** or IP address.
- The account name you are permitted to use on that machine.
- The SSH **port**, a number identifying the network service to contact. The usual SSH port is `22`, but the owner may choose another.
- The approved login method: perhaps a password, a public key, or an organization-managed method with an additional approval step.
- The expected server host-key fingerprint and a trusted way to confirm it.
- Any required VPN or other access arrangement, plus the report's exact location.

A local account and a remote account can have different names. Your local account might be `sam` while the authorized remote account is `learner`. An administrator's name is not an invitation to log in as that administrator, and you do not need to begin with `root`.

First, check that the client program exists locally:

```bash
ssh -V
```

The capital `-V` asks for the installed version and exits without connecting. A typical result begins with `OpenSSH_`; the rest depends on your installation. The version may appear on the terminal's error-output stream even when the command succeeds. If the shell reports `ssh: command not found`, the client is missing. Use your distribution's supported installation instructions if installation is authorized. Installing a client is different from enabling an SSH server, which accepts incoming connections.

For our documentation destination, the basic command would be:

```bash
ssh -p 2222 learner@reports.example.com
```

Here `ssh` is the local client. Lowercase `-p 2222` selects the supplied port. The `@` separates the remote user, `learner`, from the machine name, `reports.example.com`. It is part of SSH's destination notation, not an email address in this command.

If the actual owner supplies port `22`, you can normally omit `-p 22`. If you omit `learner@`, SSH normally starts with your local username unless a configuration setting supplies another. Writing the user explicitly avoids a common source of failed logins.

Do not run the placeholder command hoping to discover a usable account. Replace its values only after obtaining authorized connection details.

## Check the server before trusting it

SSH has two different identity questions to answer:

1. **Is this the machine I meant to reach?** Your client checks the server's host key.
2. **Am I allowed into this account?** The server checks your login credentials.

Your password or personal login key answers the second question, not the first. A machine that asks convincingly for your password is not necessarily the right machine.

A server has its own keys, called **host keys**. SSH can show a shortened representation of a host public key, called a **fingerprint**, so that you can compare it with a trusted reference. For a first connection, a prompt might look like this schematic example:

```text
The authenticity of host '[reports.example.com]:2222 (...)' can't be established.
ED25519 key fingerprint is SHA256:<server-fingerprint>.
Are you sure you want to continue connecting (yes/no/[fingerprint])?
```

`<server-fingerprint>` is explanatory text, not a real fingerprint. The actual display will contain a long value. `ED25519` identifies the kind of key. The square brackets and `:2222` identify a host using a non-default port.

Before answering, compare the **entire fingerprint**, and the key type it belongs to, with the value obtained from the owner through an independently trusted route. That might be an authenticated management page you already trust or a verified conversation with the administrator. Merely asking the same unverified connection for its fingerprint provides no independent check. A key collected with `ssh-keyscan` also needs verification; collecting a key does not establish who owns it.

If the reference matches, accept using the prompt's supported response, commonly `yes`. If it does not match, or you cannot obtain a trusted reference, answer `no` and resolve the uncertainty with the owner. Do not enter a password first and investigate afterward.

After acceptance, the client normally records the host's public key in your local `~/.ssh/known_hosts`. Here `~` means your local home directory, and `.ssh` is a directory used for SSH files. Future connections can compare the server against that saved record. Some organizations preinstall trusted host keys or use host certificates, so a first connection may not ask this question at all.

A later warning such as `REMOTE HOST IDENTIFICATION HAS CHANGED!` is different from an unknown first-time host. A legitimate rebuild can change a host key, but so can connecting to the wrong machine or an impersonation attempt. Stop and ask the owner to confirm the change and new fingerprint. Do not delete the saved entry, turn off host-key checking, or redirect the known-hosts file to nowhere just to silence the warning. Once the change is independently confirmed, follow the approved procedure to update the specific record.

## Work remotely, then return locally

After host verification, the server decides how you must authenticate. If password login is permitted, it may ask for the remote account's password. Terminal password entry normally shows no characters, not even dots. Type it only at the expected prompt after verifying the host, not as part of a shell command. A key-based account may require key setup before any login can succeed; the next sections explain that route.

If login succeeds and the account permits an interactive shell, start with read-only checks:

```bash
whoami
pwd
```

`whoami` prints the account running the command. `pwd` prints the current directory. In our hypothetical session, the results could be:

```text
learner
/home/learner
```

These are illustrative, not observed remote results. A different home directory is not itself an error. Compare the account and location with what the owner told you. Both commands are now running remotely; they have not changed your local account or local working directory.

To inspect the agreed report location, you might then use:

```bash
ls -l /home/learner/reports/report.txt
```

`ls` lists file information; `-l` requests the longer form including permissions, owner, size, and name. This absolute path begins at the remote filesystem's root. The command checks the file's presence and permissions without copying it. A missing-file error means this remote path was not found; it does not say anything about a similarly named file on your laptop.

When finished, end the remote shell:

```bash
exit
```

`exit` closes this shell. In a normal single SSH session, SSH then returns you to your original local shell, often with a connection-closed message. Run `pwd` again if you need to reorient yourself. The directory you were using locally before connecting should still be your local working directory.

SSH also supports a single remote command without an interactive login shell:

```bash
ssh -p 2222 learner@reports.example.com 'pwd'
```

The single quotes make `pwd` one literal argument for the local shell to pass to SSH. SSH requests that command on the remote side and normally closes the session afterward. For more complicated commands, both local and remote shell interpretation matter. Begin with simple read-only commands rather than pasting a pipeline whose execution location you do not understand.

## Understand the two halves of a login key

Instead of proving your identity with an account password, you can use a related pair of files:

- The **public key** is the part you give to the owner through the approved setup process. The server can use it to check a proof made by the matching private key.
- The **private key** is the part you keep protected on your own machine. SSH uses it to make that proof without sending the private key itself to the server.

The files are related, but they are not interchangeable. Sending a private key to an administrator is not a normal public-key setup step. Do not paste one into chat, upload it to a repository, or copy it to the remote server to make login work. An attacker who obtains a usable private key may be able to impersonate you wherever its public key is accepted.

A **passphrase** protects a private-key file by encrypting it while stored. You enter it locally to unlock the key for use. It is not the remote account password, and it is not the server's host fingerprint. A strong passphrase helps if the file is stolen, but does not make a compromised computer safe.

Before creating a key for real access, check the owner's policy. You might be expected to use an existing managed key, a hardware-backed key, or a certificate rather than a new personal file.

## Create a separate key without replacing another

The following local example makes a separate directory and explicitly names the new key. It does not use or replace default keys in `~/.ssh`. Choose a parent directory you control, outside any repository or shared folder, and check that `ssh-practice` does not already exist.

```bash
mkdir -m 700 ssh-practice
```

`mkdir` creates a directory. `-m 700` gives its owner read, write, and directory-entry access, and gives no access to the group or others. Success normally prints nothing. If it says the directory already exists, stop and choose a different unused name; do not assume an existing directory is disposable.

Only after that command succeeds, enter the new directory:

```bash
cd ssh-practice
```

`cd` changes your local shell's working directory. Keep this directory as your local working directory for the key, configuration, and copy examples below.

If new Ed25519 keys are allowed by the owner's policy, create one here:

```bash
ssh-keygen -t ed25519 -f ./practice_ed25519 -C 'handbook-practice'
```

`ssh-keygen` creates and manages SSH keys. `-t ed25519` chooses the key type. `-f ./practice_ed25519` chooses the private-key filename in the current directory; the public-key filename will be `practice_ed25519.pub`. `-C` attaches a descriptive comment. The quoted comment is one argument, not a password and not an access rule.

The program asks for a passphrase twice. For a key intended for real access, use a strong, unique passphrase and the organization's storage and recovery guidance. Type it into the prompt, not into a command-line option that could enter shell history. If the program unexpectedly asks to overwrite a file, decline and investigate rather than replacing an existing key.

Successful generation reports the two saved file paths and a fingerprint for your new **user** key. This fingerprint is not the **server's** fingerprint from the earlier connection check.

To inspect that public-key fingerprint again:

```bash
ssh-keygen -l -f ./practice_ed25519.pub
```

Here lowercase `-l` means list a fingerprint, rather than create a key. The result includes the key size, fingerprint, comment, and key type. To view the public key for an approved enrollment process:

```bash
cat ./practice_ed25519.pub
```

`cat` writes the named file's contents to the terminal. The `.pub` suffix matters. Its output is one long public-key line, commonly beginning `ssh-ed25519`. Provide the complete line through the approved route; the descriptive comment alone is not the key. Do not remove `.pub` from this command: that would display the private-key file instead.

## Authorize the public key and select the private key

Creating a key does not grant access anywhere. The server must be configured to recognize the public key for the intended account.

On many OpenSSH servers, an account's accepted public keys are stored in that remote account's `~/.ssh/authorized_keys`. For `learner`, the `~` in that explanation means **learner's remote home**, not your local home. The administrator may instead manage keys centrally. Ask them which process applies.

Give the public key to the owner for enrollment, or use their approved self-service process. Do not replace an existing `authorized_keys` file: it can contain keys needed by other authorized access. Tools such as `ssh-copy-id` can install a public key when you already have an approved login route, but they are not a way around a failed first authentication. No server-side installation command is needed for the local example here.

Once this public key has been authorized, a connection from the directory containing the pair could use:

```bash
ssh -p 2222 -i ./practice_ed25519 -o IdentitiesOnly=yes learner@reports.example.com
```

`-i` selects the private-key file. `-o` passes a named SSH setting; `IdentitiesOnly=yes` limits which identities SSH offers to the configured or explicitly selected identities, rather than trying every identity held by an agent. The connection still verifies the server's host key and still follows the server's account and authentication policy. Key authentication may also be combined with another factor.

A prompt like `Enter passphrase for key ...` is asking locally to unlock the selected key. A prompt like `learner@... password:` is asking for an account password. If you expected only key authentication, a password prompt may mean the key was not accepted or another method is required. Stop and check rather than entering unrelated passwords.

### Permissions protect different files for different reasons

OpenSSH may refuse a private key that other users can read. If the newly created example key's permissions have been changed, restore owner-only access locally:

```bash
chmod 600 ./practice_ed25519
```

`chmod` changes permissions on this named file. `600` allows the owner to read and write and allows nobody else access through the ordinary group/other permission bits. It does not change the owner. Do not run broad recursive permission changes to fix a single key.

The usual owner-controlled `.ssh` directory has mode `700`; private keys and `authorized_keys` commonly have mode `600`. Public keys are not secrets and can commonly have mode `644`, meaning owner read/write and everyone else read access. The server also checks ownership and whether important account paths can be modified by others. Shared or centrally managed arrangements may differ. Have the administrator inspect remote ownership and permissions rather than trying `chmod 777`, which makes access less safe and can make SSH reject it.

Keep the roles separate: `known_hosts` remembers **servers you trust** on the client; `authorized_keys` lists **user keys accepted for an account** on the server. Editing one cannot repair the other's identity check.

## Let an agent remember an unlocked key

Repeatedly typing a key passphrase can be inconvenient. A local helper called an **SSH agent** can hold an unlocked identity and make authentication proofs when SSH asks. Your desktop login may already provide one.

If an agent is available and using it is permitted, add only the intended key:

```bash
ssh-add -t 1h ./practice_ed25519
```

`ssh-add` talks to your local agent. `-t 1h` requests a one-hour lifetime for the loaded identity. It may ask for the key's passphrase. Loading the identity does not enroll the public key on a server and does not prove that a remote connection will succeed.

To see which key fingerprints the agent holds:

```bash
ssh-add -l
```

Lowercase `-l` lists fingerprints, not private-key contents. “The agent has no identities” means an agent answered but has no loaded identities. “Could not open a connection to your authentication agent” means this terminal cannot reach an agent. In that case, you can still use `ssh -i` and enter the passphrase when needed; consult your desktop or organization's instructions before starting additional agents.

To remove just this identity from the agent before its lifetime expires:

```bash
ssh-add -d ./practice_ed25519.pub
```

`-d` removes the matching identity from the agent. It does not delete the key files or revoke the public key on a server. Revoking access requires removing or disabling the server's authorization through its approved process.

Avoid enabling agent forwarding, such as `ssh -A`, merely for convenience. Forwarding lets the remote environment request authentication operations from your local agent. A compromised remote machine can misuse that access while it is available, even without receiving the private-key file.

## Keep connection settings in a small file

Long connection commands become easier to read if you give their settings a local nickname. Rather than modifying an existing `~/.ssh/config`, create a new file named `ssh-example.conf` in the local practice directory using your text editor. Put this documentation example in it, replacing destination details only for authorized use:

```text
Host report-box
    HostName reports.example.com
    User learner
    Port 2222
    IdentityFile ./practice_ed25519
    IdentitiesOnly yes
    ForwardAgent no
```

`Host report-box` introduces settings for that nickname. `HostName` gives the actual destination name, `User` the remote account, and `Port` the SSH port. `IdentityFile` selects the private-key path, and `IdentitiesOnly` has the same purpose as in the earlier command. `ForwardAgent no` explicitly leaves agent forwarding off. Indentation makes the section readable; this is SSH configuration, not shell commands.

The `./practice_ed25519` path is relative to the directory where you run SSH, not automatically to the configuration file's directory. That is why these examples stay in the practice directory. A lasting configuration should use the intended key's absolute path or an appropriate `~/.ssh/...` path, following local policy.

For this simple file, inspect the settings without making a remote connection:

```bash
ssh -G -F ./ssh-example.conf report-box
```

`-F` selects this configuration file instead of the normal client configuration files. Capital `-G` prints the evaluated settings and exits rather than logging in. Expect a long list of settings, including values such as these selected, illustrative lines:

```text
user learner
hostname reports.example.com
port 2222
identitiesonly yes
identityfile ./practice_ed25519
```

This confirms how SSH interprets the settings, not whether the destination exists or accepts the key. Use `-G` with configuration you understand: more advanced configurations can contain commands that execute during evaluation, such as `Match exec`.

When the destination and key are authorized, the shorter connection command is:

```bash
ssh -F ./ssh-example.conf report-box
```

For routine use, OpenSSH normally reads `~/.ssh/config`, but do not overwrite an existing file to adopt this example. Its sections may already control other connections. For most individual settings the first matching value wins, so section order also matters. The explicit example file keeps this chapter's settings separate.

## Copy the report in the right direction

After confirming the remote report path and leaving the remote shell with `exit`, run the copy from your **local** terminal. The `scp` program copies files over an SSH connection and uses the same host verification and login checks. Current OpenSSH uses the SFTP file-transfer protocol for `scp` by default; older installations may behave differently.

First, check where the local copy will land:

```bash
pwd
ls -l ./report-from-server.txt
```

The first command identifies the local directory. The second checks the proposed local filename. If it reports “No such file or directory,” that name was not found at that moment. If it exists, choose another name or deliberately arrange a backup before copying. `scp` can overwrite an existing destination without asking, and checking beforehand is not a guarantee against a file appearing later in a shared directory.

Using the separate settings file, download the agreed report:

```bash
scp -F ./ssh-example.conf report-box:/home/learner/reports/report.txt ./report-from-server.txt
```

`scp` takes the source first and destination last. The colon after `report-box` marks the source as remote. `/home/learner/reports/report.txt` is its path on that machine. `./report-from-server.txt` has no remote prefix, so it is a path on your local machine. `-F` selects the same settings file, including the port and key. You may see a progress indicator or authentication prompts; an error is not a completed transfer.

After a successful copy, inspect the local result:

```bash
ls -l ./report-from-server.txt
```

The listing should now describe the local file. Its presence alone does not establish that it is the report you expected. Check the name, size, and contents as appropriate for the file and your authorization. If a transfer was interrupted, treat any partial destination as incomplete.

Without the configuration file, the equivalent download command would use capital `-P` for the port:

```bash
scp -P 2222 -i ./practice_ed25519 -o IdentitiesOnly=yes learner@reports.example.com:/home/learner/reports/report.txt ./report-from-server.txt
```

This is an alternative to the previous download, not another required copy. SSH login uses lowercase `-p`; `scp` uses capital `-P`. For `scp`, lowercase `-p` preserves file times and mode bits instead of selecting a port.

Copying in the other direction writes to the remote machine. Only if the owner has approved an upload path, and you have checked that overwriting the named destination is intended, an upload might be:

```bash
scp -F ./ssh-example.conf ./report-from-server.txt report-box:/home/learner/incoming/report-review.txt
```

Now the local file comes first and the remote destination last. The remote directory must already exist and be writable by the remote account. A successful login does not grant write access everywhere. Do not reverse source and destination to “see what happens.”

Start with one explicitly named file. Adding `-r` copies directories recursively and can include more than you intended, including content reached through symbolic links. `rsync` offers more sophisticated synchronization, but its deletion options can remove destination files. Neither encryption nor a familiar tool makes an unchecked copy direction safe.

## Find the stage that failed

Troubleshooting is easier when you ask how far the connection got. Changing a password cannot repair a misspelled host name, and loosening file permissions cannot repair a network timeout.

### The destination name could not be found

A message such as `Could not resolve hostname` means the client could not turn the supplied name into a usable address. Check spelling, the owner's exact name, and any required VPN or network connection. In the configuration example, `report-box` works only when SSH reads the file that defines it. If you accidentally run `ssh report-box`, the correction is to include `-F ./ssh-example.conf`, not to create a different remote account.

### The connection timed out or was refused

A timeout means the attempt did not complete in time. A wrong address, network policy, missing VPN, or unavailable server can cause it. “Connection refused” usually means an endpoint actively rejected the connection, often because no service is listening on that port or a network rule rejects it. Confirm the supplied port and access route with the owner. Neither message establishes that your password is wrong. Do not open firewall ports or restart services on someone else's machine as a guessing step.

### The host key is unknown or changed

Follow the fingerprint process above. An unknown host needs a trusted reference. A changed host needs an explanation and independent confirmation. Do not bypass either check to reach the login prompt.

### The server denied authentication

`Permission denied (publickey)` generally means the server did not accept the available public-key authentication. Check the remote user, selected key, and whether the matching public key was actually enrolled for that account. If a key is accepted for one user, it is not automatically accepted for every user on that server.

A warning about an “UNPROTECTED PRIVATE KEY FILE” points instead to local private-key permissions. Correct the specific local file, as described above. “Too many authentication failures” can occur when the client offers several agent keys before the intended one; selecting the intended key with `-i` and `IdentitiesOnly=yes` can address that cause. Server-side policy or ownership problems need the administrator's inspection.

For additional detail, add lowercase `-v` to the connection command:

```bash
ssh -v -F ./ssh-example.conf report-box
```

`-v` prints diagnostic messages about connection setup and authentication. Look for which stage completed and which key was offered or accepted. Verbose output can reveal account names, addresses, paths, fingerprints, and other configuration details. Review and redact it before sharing, and never share a private key, passphrase, password, or unreviewed full log.

### Login works, but copying fails

A file-transfer “Permission denied” after successful authentication may refer to the source file or destination directory, not to login. Recheck the exact remote path and the local destination. A message about a failed SFTP subsystem can mean file transfer is disabled or configured differently on the server. Ask the owner which transfer method is supported rather than blindly forcing an older protocol.

The useful stopping point is a specific question: “Is this the correct port?”, “Has this public key been enrolled for this account?”, or “Can this account read that report?” That gives the owner something concrete to check without weakening identity verification.

## Remove the practice key when finished

If this pair was only for practice, first remove it from the agent with the earlier `ssh-add -d ./practice_ed25519.pub` command, if you loaded it. If you enrolled its public key on a real server, arrange removal of that authorization through the owner's approved process too. Deleting a local key does not revoke copies or server-side authorization.

Stay in your local `ssh-practice` directory and check `pwd` before removing anything. Once you are sure these are the disposable files you created:

```bash
rm -- ./practice_ed25519 ./practice_ed25519.pub
```

`rm` removes these two specific files. `--` ends its options. This does not securely erase storage or backups, and there is no built-in undo. Keep a key that is still needed for real access rather than following cleanup blindly.

If you also created the example settings file and no longer need it, remove it separately:

```bash
rm -- ./ssh-example.conf
```

Any downloaded report is your data, not automatically disposable. Decide whether to keep it. To remove the practice directory, leave it with `cd ..` and use `rmdir ssh-practice`. `rmdir` refuses if a report or any other file remains. Inspect those files rather than switching to recursive deletion. The named key and settings-file removals were checked on disposable local fixtures; no server authorization was changed.

## Further reading

- [OpenSSH manual pages](https://www.openssh.com/manual.html)
- [OpenSSH: ssh(1)](https://man.openbsd.org/ssh)
- [OpenSSH: ssh-keygen(1)](https://man.openbsd.org/ssh-keygen)
- [OpenSSH: ssh_config(5)](https://man.openbsd.org/ssh_config)
- [OpenSSH: ssh-add(1)](https://man.openbsd.org/ssh-add)
- [OpenSSH: scp(1)](https://man.openbsd.org/scp)
