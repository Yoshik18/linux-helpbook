# Linux Commands

---

## System Information & Monitoring

| Command         | Description                                   |
|-----------------|-----------------------------------------------|
| `uname -a`      | Display complete system information           |
| `hostname`      | Show system hostname                          |
| `uptime`        | Show system uptime and load average           |
| `whoami`        | Display current username                      |
| `id`            | Show user and group IDs                       |
| `w`             | Show who is logged in and what they're doing  |
| `last`          | Show last logged in users                     |
| `history`       | Display command history                       |
| `env`           | Show environment variables                    |
| `lscpu`         | Display CPU information                       |
| `lsmem`         | Show memory information                       |
| `lsblk`         | List block devices                            |
| `lsusb`         | List USB devices                              |
| `lspci`         | List PCI devices                              |

---

## Basic Navigation & File Operations

| Command                        | Description                                 |
|--------------------------------|---------------------------------------------|
| `pwd`                          | Print working directory                     |
| `ls -la`                       | List all files with detailed info           |
| `ls -lh`                       | List files with human-readable sizes        |
| `ls -lt`                       | List files sorted by modification time      |
| `cd -`                         | Change to previous directory                |
| `cd ../..`                     | Go up two directories                       |
| `mkdir -p path/to/dir`         | Create nested directories                   |
| `rmdir dir`                    | Remove empty directory                      |
| `rm -rf dir/`                  | Remove directory and contents forcefully    |
| `cp -v file1 file2`            | Copy with verbose output                    |
| `mv file1 file2`               | Move/rename files                           |
| `ln -s target linkname`        | Create symbolic link                        |
| `readlink -f linkname`         | Show absolute path of symbolic link         |

---

## File Content Operations

| Command                        | Description                                 |
|--------------------------------|---------------------------------------------|
| `head -n 20 file`              | Show first 20 lines of file                 |
| `tail -f file`                 | Follow file changes in real-time            |
| `tail -n 50 file`              | Show last 50 lines                          |
| `cat -n file`                  | Display file with line numbers              |
| `tac file`                     | Display file in reverse order               |
| `more file`                    | View file page by page                      |
| `less +G file`                 | Open file and go to end                     |
| `wc -l file`                   | Count lines in file                         |
| `wc -w file`                   | Count words in file                         |
| `sort file`                    | Sort file contents                          |
| `sort -r file`                 | Sort in reverse order                       |
| `uniq file`                    | Remove duplicate lines                      |
| `cut -d',' -f1,3 file.csv`     | Extract specific columns from CSV           |

---

## Text Search & Processing

| Command                              | Description                                 |
|--------------------------------------|---------------------------------------------|
| `grep -i "pattern" file`             | Case-insensitive search                     |
| `grep -r "pattern" dir/`             | Recursive search in directory               |
| `grep -n "pattern" file`             | Show line numbers                           |
| `grep -v "pattern" file`             | Invert match (exclude pattern)              |
| `grep -c "pattern" file`             | Count matching lines                        |
| `grep -l "pattern" *.txt`            | List files containing pattern               |
| `awk '{print $1}' file`              | Print first column                          |
| `awk -F',' '{print $2}' file`        | Use comma as field separator                |
| `sed 's/old/new/g' file`             | Replace all occurrences                     |
| `sed -i 's/old/new/g' file`          | Edit file in place                          |
| `tr 'a-z' 'A-Z' < file`              | Convert lowercase to uppercase              |

---

## File Permissions & Ownership

| Command                        | Description                                 |
|--------------------------------|---------------------------------------------|
| `chmod +x script.sh`           | Make file executable                        |
| `chmod 755 file`               | Set rwxr-xr-x permissions                   |
| `chmod -R 644 dir/`            | Set permissions recursively                 |
| `chown user:group file`        | Change owner and group                      |
| `chgrp staff file`             | Change group only                           |
| `sudo chown root file`         | Change owner to root                        |
| `stat file`                    | Show detailed file information              |

---

## Process Management

| Command                        | Description                                 |
|--------------------------------|---------------------------------------------|
| `ps aux`                       | Show all running processes                  |
| `ps -ef`                       | Alternative process listing                 |
| `pstree`                       | Show process tree                           |
| `top`                          | Real-time process viewer                    |
| `htop`                         | Enhanced process viewer                     |
| `jobs`                         | Show active jobs                            |
| `bg %1`                        | Put job 1 in background                     |
| `fg %1`                        | Bring job 1 to foreground                   |
| `nohup command &`              | Run command immune to hangups               |
| `kill -9 PID`                  | Force kill process                          |
| `killall process_name`         | Kill all processes by name                  |
| `pidof process_name`           | Find process ID by name                     |

---

## Network Operations

| Command                        | Description                                 |
|--------------------------------|---------------------------------------------|
| `ping -c 4 google.com`         | Ping with 4 packets                         |
| `wget https://url/file`        | Download file from URL                      |
| `curl -O https://url/file`     | Download file with curl                     |
| `curl -I https://url`          | Get HTTP headers only                       |
| `ssh user@hostname`            | Connect via SSH                             |
| `scp file user@host:/path`     | Copy file over SSH                          |
| `rsync -av src/ dest/`         | Sync directories                            |
| `netstat -tuln`                | Show listening ports                        |
| `ss -tuln`                     | Modern alternative to netstat               |
| `lsof -i :8080`                | Show what's using port 8080                 |

---

## Archive & Compression

| Command                                | Description                                 |
|----------------------------------------|---------------------------------------------|
| `tar -czf archive.tar.gz dir/`         | Create compressed archive                   |
| `tar -xzf archive.tar.gz`              | Extract compressed archive                  |
| `tar -tzf archive.tar.gz`              | List archive contents                       |
| `tar -xzf file.tar.gz -C /path`        | Extract to specific directory               |
| `zip -r archive.zip dir/`              | Create ZIP archive                          |
| `unzip archive.zip`                    | Extract ZIP archive                         |
| `unzip -l archive.zip`                 | List ZIP contents                           |
| `gzip file`                            | Compress single file                        |
| `gunzip file.gz`                       | Decompress gzip file                        |

---

## System Monitoring & Performance

| Command                        | Description                                 |
|--------------------------------|---------------------------------------------|
| `free -h`                      | Show memory usage                           |
| `df -h`                        | Show disk space usage                       |
| `du -sh *`                     | Show directory sizes                        |
| `du -h --max-depth=1`          | Limit directory depth                       |
| `iostat 1`                     | Show I/O statistics                         |
| `vmstat 1`                     | Show system statistics                      |
| `sar -u 1 10`                  | CPU usage for 10 seconds                    |
| `dmesg \| tail`                | Show recent kernel messages                 |
| `journalctl -f`                | Follow system journal                       |
| `systemctl status service`     | Check service status                        |

---

## File Finding & Searching

| Command                        | Description                                 |
|--------------------------------|---------------------------------------------|
| `find . -name "*.txt"`         | Find files by extension                     |
| `find . -type f -size +1M`     | Find files larger than 1MB                  |
| `find . -mtime -7`             | Find files modified in last 7 days          |
| `find . -empty`                | Find empty files and directories            |
| `find . -executable`           | Find executable files                       |
| `locate filename`              | Quick file search (if updatedb run)         |
| `which command`                | Show command location                       |
| `whereis command`              | Show command, source, manual locations      |

---

## Text Editors & File Creation

| Command                        | Description                                 |
|--------------------------------|---------------------------------------------|
| `nano file`                    | Simple text editor                          |
| `vim file`                     | Vi/Vim editor                               |
| `emacs file`                   | Emacs editor                                |
| `touch file{1,2,3}.txt`        | Create multiple files                       |
| `echo "text" > file`           | Write text to file (overwrite)              |
| `echo "text" >> file`          | Append text to file                         |
| `cat > file`                   | Create file with input                      |
| `cat >> file`                  | Append to file with input                   |

---

## Environment & Variables

| Command                        | Description                                 |
|--------------------------------|---------------------------------------------|
| `export VAR=value`             | Set environment variable                    |
| `echo $PATH`                   | Show PATH variable                          |
| `echo $HOME`                   | Show home directory                         |
| `printenv`                     | Show all environment variables              |
| `alias ll='ls -la'`            | Create command alias                        |
| `unalias ll`                   | Remove alias                                |
| `source ~/.bashrc`             | Reload bash configuration                   |

---

## Advanced Operations

| Command                                | Description                                 |
|----------------------------------------|---------------------------------------------|
| `xargs`                                | Build command lines from input              |
| `command \| tee file`                  | Output to both screen and file              |
| `command1 && command2`                 | Run command2 only if command1 succeeds      |
| `command1 || command2`                 | Run command2 only if command1 fails         |
| `command1 ; command2`                  | Run commands sequentially                   |
| `command &`                            | Run command in background                   |
| `watch -n 2 command`                   | Run command every 2 seconds                 |
| `crontab -e`                           | Edit scheduled tasks                        |
| `at now + 1 hour`                      | Schedule one-time task                      |
| `screen -S session_name`               | Create named screen session                 |
| `tmux new -s session_name`             | Create named tmux session                   |

---

## System Administration

| Command                        | Description                                 |
|--------------------------------|---------------------------------------------|
| `sudo command`                 | Run command as root                         |
| `su - username`                | Switch to another user                      |
| `passwd`                       | Change password                             |
| `usermod -aG group user`       | Add user to group                           |
| `systemctl start service`      | Start system service                        |
| `systemctl enable service`     | Enable service at boot                      |
| `systemctl reload service`     | Reload service configuration                |
| `mount /dev/sdb1 /mnt`         | Mount filesystem                            |
| `umount /mnt`                  | Unmount filesystem                          |
| `fdisk -l`                     | List disk partitions                        |