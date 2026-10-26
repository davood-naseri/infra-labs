# Secure Linux Server Baseline

A documented Ubuntu Server home lab for practicing Linux administration, securing administrative access, and preparing for infrastructure automation.

## Scenario and Scope

Novatech is a fictional company used for this learning scenario. The lab server represents a non-production application host.

The baseline currently includes system inventory, time-synchronization verification, SSH service inspection, and key-based administrative access. Firewall hardening, post-reboot verification, and Ansible automation remain pending.

Docker and Azure projects are maintained separately and are not implementations within this baseline. Links to their repositories will be added when their URLs are confirmed.

## Hardware and Operating System

| Item | Observed value |
|---|---|
| Device role | Local Linux administration lab server |
| Hostname | `lab-server`, observed in the shell prompt and service logs; explicit `hostnamectl` verification pending |
| CPU | Intel Core i3 (user-reported; exact model pending) |
| Operating system | Ubuntu 24.04.5 LTS, as previously reported by `lsb_release -a` |
| Codename | noble |
| Installed RAM | 8 GB (user-reported) |
| Usable RAM | 7.7 GiB |
| Available RAM at inspection | 7.2 GiB |
| Swap | 4.0 GiB; unused at inspection |
| Physical disk | `/dev/sda`, 465.8 GiB (approximately 500 GB nominal) |
| Root filesystem | ext4, mounted at `/` |
| Root filesystem capacity | 98 GiB |
| Root filesystem usage | 7.1 GiB used; 86 GiB available; 8% usage |

Memory usage and available disk space are point-in-time observations. The swap backing file/device has not yet been recorded.

## Storage Layout

```text
sda                         465.8 GiB  disk
├── sda1                       1 MiB  partition; purpose not yet verified
├── sda2                       2 GiB  partition mounted at /boot
└── sda3                   463.8 GiB  partition backing LVM
    └── ubuntu-vg/ubuntu-lv   100 GiB  logical volume mounted at /
```

| LVM item | Observed value |
|---|---|
| Volume group | `ubuntu-vg` |
| Physical volumes in group | 1 |
| Logical volumes in group | 1 |
| Volume group capacity | `<463.76 GiB` |
| Unallocated volume group space | `<363.76 GiB` |
| Root logical volume | `ubuntu-lv`, 100.00 GiB |

### Why a 500 GB SSD has a root filesystem of about 100 GiB

- The nominal 500 GB disk appears as approximately 465.8 GiB because GB and GiB use different units.
- Only 100 GiB of the volume group has been allocated to the root logical volume.
- Approximately 363.76 GiB remains unallocated **inside the volume group**. It is not free space already available to `/`.
- Filesystem overhead and reporting account for the difference between the 100 GiB logical volume and the approximately 98 GiB filesystem capacity.
- Filesystem reservations and rounding can cause `Used + Avail` to differ from `Size`.
- No partition or logical-volume resizing was performed during inventory.

An optical-device entry, `/dev/sr0`, also appeared in `lsblk`; it is not an additional SSD.

## Network Inventory

| Interface | Observed status | Role |
|---|---|---|
| `lo` | UNKNOWN | Loopback |
| `enp19s0` | DOWN | Ethernet interface |
| `wlp7s0` | UP | Active Wi-Fi interface with DHCP-provided IPv4 configuration |

At inspection, Wi-Fi used a `/24` IPv4 network prefix and a DHCP-provided default route through `wlp7s0`, with metric `600`. A link-local IPv6 address was also present.

Exact LAN addresses are intentionally omitted. The server address changed during the lab; use its current address when connecting.

An IP address and default route alone do not verify DNS resolution or Internet connectivity. Listening on all interfaces does not establish Internet reachability.

## Time Synchronization

Verified at inspection:

- `systemd-timesyncd` was enabled and running.
- NTP was active and the system clock reported synchronized.
- The service reported contacting `ntp.ubuntu.com`.
- Timezone: `Asia/Tehran`.
- Hardware clock: UTC (`RTC in local TZ: no`).

## Administrative Access and SSH Verification

### Verified observations

- SSH was running with socket activation enabled.
- `ssh.socket` was enabled and listening on TCP port 22 on IPv4 and IPv6.
- `ssh.service` was running, although not independently enabled; the enabled socket triggers it.
- Initial password-based login succeeded before hardening.
- Public-key login from Windows PowerShell was verified using a dedicated Ed25519 key.
- Password and keyboard-interactive authentication were subsequently disabled.
- After reloading SSH, a login attempt with public-key authentication disabled was rejected with `Permission denied (publickey)`.
- UFW was inactive at the last inspection; firewall hardening is pending.

### SSH configuration

Local configuration file:

```text
/etc/ssh/sshd_config.d/00-local-key-only.conf
```

```text
PubkeyAuthentication yes
PasswordAuthentication no
KbdInteractiveAuthentication no
```

Validate configuration before applying changes:

```bash
sudo /usr/sbin/sshd -t
sudo /usr/sbin/sshd -T | grep -E '^(pubkeyauthentication|passwordauthentication|kbdinteractiveauthentication) '
```

The first command should exit successfully without output. The second should report `yes`, `no`, and `no`, respectively. Connection-specific `Match` rules, if introduced later, require additional verification.

Reload only after successful validation, with an existing session and recovery access available:

```bash
sudo systemctl reload ssh
```

Disabling SSH password authentication does not remove the account password or disable its use with `sudo` or local-console login.

### Ubuntu management VM — pending final verification

The intended management environment is an Ubuntu Server VM on VMware, without a graphical desktop. It will later act as the Ansible control node.

- Use a separate Ed25519 key generated inside the VM.
- Install only its public key on the server.
- Keep the private key on the VM.
- Preserve the Windows public key when editing `authorized_keys`.
- Verify the server host-key fingerprint through a trusted channel.
- Confirm a new key-only session from the VM.
- Re-test Windows key access after recovering its accidentally removed public-key entry.

Final completion of these VM and recovery checks has not yet been recorded in this document.

## Listening Ports Observed

The TCP listener inspection used `sudo ss -lntp`.

| Listener | Process/service | Exposure at inspection |
|---|---|---|
| TCP 22 | SSH / systemd socket activation | All IPv4 and IPv6 interfaces |
| TCP 53 | systemd-resolved | IPv4 loopback addresses only |

This is a point-in-time TCP inventory, not a complete UDP inventory or an external firewall test.

## Management and Recovery

- Keep an established SSH session open while changing authentication settings.
- Ensure direct keyboard/display access is available before risky changes; explicitly testing console recovery remains pending.
- Validate SSH configuration before reloading it.
- Test new access in a separate session before closing the original session.
- If a public-key entry is accidentally removed, restore the public key from its client using an existing session or the local console. Do not transfer the private key.
- Back up `authorized_keys` before editing it and retain one public key per line.
- Check the current server address after changing networks.
- Diagnose failures in this order: address → network route → port → service → authentication.

A previous SSH connection reset remains unexplained. Later successful logins do not prove the original cause was resolved.

## Day 3 — Users, Ownership, and Permissions

**Status: planned; execution and results have not yet been verified.**

### Objective

Create an isolated application-data directory, apply deliberate ownership and permissions, and verify access as an ordinary user without using `chmod 777`.

Run the following exercises on **lab-server**, after connecting from a management client. They do not require changes to SSH or firewall settings.

### Concepts

- A user identifies an account; groups support shared access control.
- Each file has a user owner and a group owner.
- `chown` changes ownership; `chmod` changes permission bits.
- `sudo` runs an authorized command with elevated privileges. Do not use it for ordinary permission tests because it can bypass the restrictions being tested.

| Permission | Value | File meaning | Directory meaning |
|---|---:|---|---|
| Read (`r`) | 4 | Read contents | List entry names |
| Write (`w`) | 2 | Modify contents | Create/remove entries, normally requiring execute permission too |
| Execute (`x`) | 1 | Execute a suitable file | Traverse/search the directory |

| Mode | Symbolic permissions | Example |
|---|---|---|
| `644` | `rw-r--r--` | Non-sensitive file |
| `600` | `rw-------` | Owner-only private file |
| `755` | `rwxr-xr-x` | Directory allowing others to list and traverse |
| `700` | `rwx------` | Owner-only directory |
| `750` | `rwxr-x---` | Directory restricted to owner and group |

These permissions are owner/group/other permissions. Parent-directory traversal permissions also affect access. File deletion is primarily governed by the parent directory, with additional restrictions such as the sticky bit potentially applying.

### Exercise 1: Verify identity and create the lab directory

```bash
whoami
hostname
id
ls -ld /srv/novatech-permissions-lab
```

Confirm that this is the intended account on `lab-server`. If the lab directory already exists, inspect it before making changes. A missing-directory error is expected for a new exercise.

For a new directory:

```bash
sudo mkdir /srv/novatech-permissions-lab
sudo chown "$(id -un):$(id -gn)" /srv/novatech-permissions-lab
sudo chmod 750 /srv/novatech-permissions-lab
ls -ld /srv/novatech-permissions-lab
```

Expected directory mode: `drwxr-x---`. Ownership is assigned to the current administrative user for this exercise, not as a production application-account design.

### Exercise 2: Create ordinary and private files

Use Vim, without `sudo`, and save only dummy information:

```bash
cd /srv/novatech-permissions-lab
vim app-info.txt
chmod 644 app-info.txt
vim private-note.txt
chmod 600 private-note.txt
ls -l app-info.txt private-note.txt
```

Expected file modes: `-rw-r--r--` and `-rw-------`.

Although `app-info.txt` has mode `644`, users denied traversal of the parent directory cannot access it through that path.

### Exercise 3: Compare directory modes

```bash
mkdir shared-demo private-demo
chmod 755 shared-demo
chmod 700 private-demo
ls -ld shared-demo private-demo
```

Expected modes: `drwxr-xr-x` and `drwx------`. The parent directory remains `750`; permissive child-directory bits do not override it.

### Exercise 4: Test a deliberate permission failure

Run as the ordinary owner, without `sudo`:

```bash
chmod 400 private-note.txt
printf 'test\n' >> private-note.txt
```

Expected result: `Permission denied` because write permission is absent.

Restore owner write access and repeat:

```bash
chmod 600 private-note.txt
printf 'test\n' >> private-note.txt
cat private-note.txt
```

Expected result: the write succeeds.

### Exercise 5: Inspect the complete path

```bash
id
ls -ld /srv/novatech-permissions-lab
ls -l /srv/novatech-permissions-lab
namei -l /srv/novatech-permissions-lab/private-note.txt
```

Investigate identity, ownership, group membership, file permissions, and parent-directory permissions before changing access. Do not apply recursive permission changes to system paths or SSH directories as part of this exercise.

### Completion criteria

- [ ] Create the lab directory and verify its ownership and mode.
- [ ] Practice and explain file modes `644` and `600`.
- [ ] Practice and explain directory modes `755` and `700`.
- [ ] Verify a failed write with mode `400` and a successful write after restoring `600`.
- [ ] Explain how parent-directory permissions affect access.
- [ ] Explain why private keys must not be readable by other ordinary users.
- [ ] Record actual results in `verification.md`, using dummy data only.

## Inventory and Verification Commands

Run on the Ubuntu Server:

```bash
hostnamectl
lsb_release -a
free -h
df -hT /
lsblk
ip -br addr
ip route
sudo vgs
sudo lvs
timedatectl status
systemctl status systemd-timesyncd --no-pager
systemctl status ssh --no-pager
systemctl status ssh.socket --no-pager
sudo ss -lntp
sudo ufw status verbose
```

Additional inventory checks still to record:

```bash
lscpu
swapon --show
```

`No LSB modules are available.` appeared during `lsb_release`; OS version information was still returned.

## Progress Checklist

- [x] Record reported Ubuntu version, RAM, swap capacity, and root filesystem usage
- [x] Identify physical disk, LVM layout, and unallocated volume-group space
- [x] Identify active network interface and default route
- [x] Verify time synchronization
- [x] Inspect SSH service and socket activation
- [x] Verify SSH key authentication from Windows
- [x] Disable SSH password and keyboard-interactive authentication and test rejection
- [x] Record observed TCP listeners and inactive UFW status
- [ ] Explicitly verify hostname with `hostnamectl` and record exact CPU model
- [ ] Identify swap backing file/device
- [ ] Record final key-login verification from the Ubuntu management VM
- [ ] Confirm Windows key access after public-key recovery
- [ ] Verify direct-console recovery access
- [ ] Complete Day 3 ownership and permission exercises
- [ ] Complete service and UDP listener inventory
- [ ] Configure and test firewall rules without losing SSH access
- [ ] Complete and test documented troubleshooting procedures
- [ ] Verify networking and SSH after a planned reboot
- [ ] Automate verified settings with Ansible

## Known Constraints

- Single physical server laptop; no high availability.
- 8 GB installed server RAM.
- Wi-Fi connectivity and potentially changing DHCP addresses.
- Some external package repositories and Terraform Registry endpoints may be inaccessible from the current network.
- No eligible Azure subscription is currently available for this lab; Azure work is outside this baseline.

## Repository Safety

Do not commit passwords, private SSH keys, VPN subscription links, VMess UUIDs, tokens, or configuration files containing credentials. Do not publish credential-bearing Netplan files.

Review every staged change. Sanitize logs and screenshots before publishing; raw `hostnamectl` output can include unnecessary machine identifiers. Public-key contents and exact LAN addresses are not required in this README.

Keep planned work separate from verified results. This project must not be described as a completed production-security baseline.
