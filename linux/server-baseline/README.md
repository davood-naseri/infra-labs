# Secure Linux Server Baseline

A documented Ubuntu Server home lab for practicing Linux administration and preparing for infrastructure automation.

## Scope and Status

This project currently covers **system inventory and baseline discovery**. Security hardening, Docker deployment, and Ansible automation are not yet verified or implemented as part of this baseline.

This is a local learning project, not a production deployment. Azure and Docker projects are maintained separately.

## Hardware and Operating System

| Item | Observed value |
|---|---|
| Device role | Local Linux administration lab server |
| Hostname | Pending verification |
| CPU | Intel Core i3 (user-reported; exact model pending) |
| Operating system | Ubuntu 24.04.5 LTS, as reported by `lsb_release -a` |
| Codename | noble |
| Installed RAM | 8 GB (user-reported) |
| Usable RAM | 7.7 GiB |
| Available RAM at inspection | 7.2 GiB |
| Swap | 4.0 GiB; unused at inspection |
| Physical disk | `/dev/sda`, 465.8 GiB (approximately 500 GB nominal) |
| Root filesystem | ext4, mounted at `/` |
| Root filesystem capacity | 98 GiB |
| Root filesystem usage | 7.1 GiB used; 86 GiB available; 8% usage |

Memory usage and available disk space are point-in-time observations, not fixed hardware specifications. The swap backing file/device has not yet been recorded.

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

### Storage interpretation

- The nominal 500 GB disk appears as approximately 465.8 GiB because GB and GiB use different units.
- Only 100 GiB of the volume group has been allocated to the root logical volume.
- Approximately 363.76 GiB remains unallocated **inside the volume group**. This is not free space already available to `/`.
- The ext4 filesystem reports about 98 GiB of capacity on the 100 GiB logical volume. Filesystem metadata and reporting account for differences between these figures.
- Filesystem reservations and rounding can also cause `Used + Avail` to differ from `Size`.
- No partition or logical-volume resizing was performed during inventory.

An optical-device entry, `/dev/sr0`, also appeared in `lsblk`; it is not an additional SSD.

## Network Inventory

| Interface | Observed status | Role |
|---|---|---|
| `lo` | UNKNOWN | Loopback; `127.0.0.1` and `::1` |
| `enp19s0` | DOWN | Ethernet interface |
| `wlp7s0` | UP | Active Wi-Fi interface with a DHCP-provided IPv4 configuration |

The Wi-Fi IPv4 address uses a `/24` network prefix. The default route is supplied by DHCP through `wlp7s0`, with metric `600`. A link-local IPv6 address is also present.

Exact LAN addresses are intentionally omitted from this public document. They can change when switching between home Wi-Fi and a mobile hotspot.

The presence of an IP address and a default route does not by itself verify DNS resolution or Internet connectivity.

## Management and Recovery

- Local keyboard/display access is available for recovery.
- Intended remote management: SSH over the local network.
- SSH service configuration and authentication method: pending verification.
- SSH key authentication, firewall rules, and hardening: pending verification.
- Keep local-console access available before changing networking or SSH settings.

## Inventory Commands

Run on the Ubuntu Server:

```bash
lsb_release -a
free -h
df -hT /
lsblk
ip -br addr
ip route
sudo vgs
sudo lvs
```

Additional checks to complete the inventory:

```bash
hostnamectl
lscpu
swapon --show
timedatectl status
systemctl status systemd-timesyncd --no-pager
```

`No LSB modules are available.` was printed by `lsb_release`; the OS version information was still returned successfully.

## Progress Checklist

- [x] Record reported Ubuntu version
- [x] Record usable RAM and swap capacity
- [x] Record root filesystem capacity and usage
- [x] Identify physical disk and LVM layout
- [x] Confirm unallocated volume group space
- [x] Identify active network interface and default route
- [ ] Verify hostname and exact CPU model
- [ ] Identify swap backing file/device
- [x] Verify time synchronization: systemd-timesyncd active, NTP synchronized, timezone Asia/Tehran, hardware clock in UTC
- [ ] Verify SSH access and document recovery steps
- [ ] Configure and test SSH key authentication
- [ ] Inventory listening ports and running services
- [ ] Review and configure firewall rules without losing access
- [ ] Automate verified settings with Ansible

## Known Constraints

- Single physical laptop; no high availability.
- 8 GB installed RAM.
- Wi-Fi connectivity and potentially changing DHCP addresses.
- Some external package repositories and Terraform Registry endpoints may be inaccessible from the current network.
- No eligible Azure subscription is currently available for this lab.

## Repository Safety

Do not commit Wi-Fi passwords, private SSH keys, VPN subscription links, VMess UUIDs, tokens, or configuration files containing credentials. Review every staged change before committing.

Raw `hostnamectl` output may contain machine identifiers that are unnecessary for public documentation. Sanitize logs and screenshots before publishing.

## SSH verification

- SSH is running with socket activation enabled.
- SSH listens on TCP port 22 on all IPv4 and IPv6 interfaces.
- Password-based login with the administrative user was verified.
- UFW is inactive.
- SSH public-key authentication was verified.
- Password and keyboard-interactive authentication are disabled.
- A password-only SSH login attempt was rejected.
- Firewall hardening is pending; UFW is inactive.
- A previous connection reset remains unexplained.
