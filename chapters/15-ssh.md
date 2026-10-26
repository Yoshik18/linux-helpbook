# 15. Connect to another machine with SSH

[Contents](../README.md) | [Previous: shell scripts](14-shell-scripts.md) | [Next: archives](16-archives.md)

Secure Shell (SSH) provides encrypted remote login and command execution. It is commonly used for server administration, but the exact access rules depend on the server's configuration and the account you are authorized to use.

## Connect by host name

```bash
ssh user@example.com
```

`ssh` is the client program, `user` is the account name, and `example.com` is the server name. Replace both with values supplied by the system owner. The client resolves the name and attempts to connect to the server's SSH service, commonly on TCP port 22. A successful connection may open an interactive shell; it does not grant permission to access data beyond that account's authorization.

On first connection, SSH may ask you to verify the server's host-key fingerprint. Confirm it through a trusted channel with the server owner. Accepting an unverified key can expose the connection to impersonation. Do not disable host-key checking to bypass a warning.

## Use a key carefully

SSH public-key authentication uses a key pair. The private key stays with the user and must be protected; the public key is installed on the server by an authorized process. `ssh-keygen` can create keys, but creating or replacing a key affects access and should follow your organization's policy. Never share the private key or upload it to a repository.

`ssh -v` prints diagnostic detail about connection setup. It can expose usernames, hostnames and paths, so review output before sharing. Verbose logs help identify whether the failure is name resolution, network reachability, host-key verification or authentication. They do not justify weakening security checks.

## Copy files

`scp` copies files over SSH:

```bash
scp report.txt user@example.com:/home/user/
```

This reads `report.txt` from the current directory and writes it to the remote destination. Confirm the local file and remote target before running it. A copy can overwrite an existing remote file with the same name. For complex synchronization, `rsync` offers additional behavior that must be understood before use, especially deletion options.

## Common confusion

- A network timeout differs from a host-key warning and an authentication failure.
- The server may use a non-default port or restrict allowed users.
- The server fingerprint must be verified through a trusted source.
- SSH encryption does not make an authorized remote command harmless.
- Never share a private key, password or unredacted verbose log.

## Further reading

- [OpenSSH manual pages](https://www.openssh.com/manual.html)
- [OpenSSH: ssh(1)](https://man.openbsd.org/ssh)
- [OpenSSH: ssh-keygen(1)](https://man.openbsd.org/ssh-keygen)
