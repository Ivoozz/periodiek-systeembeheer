---
name: ssh-management
description: Management and execution of commands on remote LXC containers or servers via SSH. Use when the user needs to perform operations on a different machine (e.g., PO-APP) than the current one.
---

# SSH Management

This skill allows Gemini CLI to interact with remote systems securely and efficiently.

## Core Mandates

1. **Security**: NEVER ask for, handle, or store private SSH keys. 
2. **Key-based Auth**: Only use key-based authentication (SSH keys). If a connection requires a password, inform the user to set up `ssh-copy-id`.
3. **Non-Interactive**: Always prefer non-interactive SSH flags to avoid hanging.

## Workflow

### 1. Connection Verification
Before running complex commands, verify the connection:
```bash
ssh -o BatchMode=yes -o ConnectTimeout=5 user@remote-ip "echo 'Connection OK'"
```

### 2. Remote Command Execution
Use the following pattern for executing commands remotely:
```bash
ssh user@remote-ip "cd /path/to/project && ./some-script.sh"
```

### 3. File Transfer
Use `scp` or `rsync` for transferring files between the local environment and the remote system:
```bash
# Upload
scp -r ./local-dir user@remote-ip:/remote-path
# Download
scp user@remote-ip:/remote-path/file.txt ./local-path
```

### 4. SSH Config
Encourage the use of `~/.ssh/config` for easier management of multiple LXCs:
```text
Host po-app
    HostName 192.168.1.100
    User root
    IdentityFile ~/.ssh/id_ed25519
```
If this is set up, you can simply run: `ssh po-app "ls -la"`.

## Troubleshooting

- **Host Key Verification Failed**: If the remote host has changed, ask the user to run `ssh-keygen -R <ip>`.
- **Permission Denied**: Ensure the public key is in `~/.ssh/authorized_keys` on the remote and that permissions are correct (700 for `.ssh`, 600 for `authorized_keys`).
