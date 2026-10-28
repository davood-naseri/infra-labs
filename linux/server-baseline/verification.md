# Server Baseline Verification

This document records the supplied Day 4 evidence only. Exact host/client addresses, key fingerprints, boot IDs, and raw logs are omitted.

## Day 4 — Services, Ports, and Logs

Verification evidence dates: 2026-10-27 and 2026-10-28 (Asia/Tehran, +0330), as reported by the server. Current NTP synchronization was confirmed by the supplied outputs.

Scope: Read-only baseline inspection. Supplied output batches may represent different sessions or boots; they must not be treated as one simultaneous snapshot.

### System Health

- System state: `running`.
- Failed units: Zero listed by `systemctl --failed`.
- Current time synchronization: Confirmed; system clock synchronized `yes`, NTP active, RTC maintained in UTC. systemd-timesyncd is active and enabled, contacting ntp.ubuntu.com. Reported offset: +14.500 ms; stratum: 2.
- Reported OS: Ubuntu 24.04.5 LTS; kernel: 6.8.0-147-generic. These are recorded from supplied outputs, not independently validated against release records.
- Clock follow-up: One retained boot has a first-entry timestamp later than its last-entry timestamp. Investigate clock adjustments; do not infer a cause from this alone.

### Service Inventory

| Unit | Observed state | Enablement state | Purpose | Follow-up |
|---|---|---|---|---|
| ssh.socket | active (running); port 22 sockets listed | enabled | SSH socket activation | No change needed for this inspection |
| ssh.service | active (running) | disabled | SSH authentication and remote administration | Triggered by ssh.socket; disabled does not imply unavailable |
| systemd-resolved.service | active (running) | enabled | Local DNS resolution | Investigate repeated DNS feature fallback if resolution problems occur |
| systemd-networkd.service | active (running) | enabled | Network configuration | Link loss and DHCP address change observed |
| systemd-timesyncd.service | active (running) | enabled | Time synchronization | Current synchronization confirmed |
| cron.service | active (running) | enabled | Scheduled jobs | Jobs observed despite earlier environment warning |
| ufw.service | active (exited) | enabled | Firewall startup integration | Does not establish active filtering; ufw status was inactive |
| xray.service | active (running) | enabled | Service labelled Xray | Runtime and socket snapshots reviewed; intended role and installation provenance not established |

The table summarizes selected units. Supplied inventories list 165 loaded service entries and 246 service unit files; some names/descriptions are ellipsized. `not-found` entries are not the same as failed units. Other running services include logging, device, storage, power-management, and wireless components. No service removal is justified by this inventory alone.

### Listening Ports

Exact host addresses are omitted. These entries describe the supplied `sudo ss -tulpen` snapshot, not Internet reachability.

| Protocol | Port | Bind scope | Process or unit | Purpose | Follow-up |
|---|---|---|---|---|---|
| TCP / IPv4 | 22 | All IPv4 interfaces | sshd / systemd; ssh.socket | SSH | Review intended exposure during later firewall hardening |
| TCP / IPv6 | 22 | All IPv6 interfaces; IPv6-only socket | sshd / systemd; ssh.socket | SSH | Include IPv6 in later firewall review |
| TCP and UDP / IPv4 | 53 | Two loopback addresses only | systemd-resolved | Local DNS resolver endpoints | No non-loopback DNS bind observed |
| UDP / IPv4 | 68 | Assigned address on wireless interface | systemd-networkd | DHCP client | Retain network functionality; not an inbound application service |
| UDP / IPv6 | 546 | Link-local address on wireless interface | systemd-networkd | DHCPv6 client | Observed in the later snapshot |

- No other TCP listeners or bound UDP sockets appeared in the later supplied snapshot. No Xray-owned socket appeared in that output.
- A separate `sudo ss -tpn` snapshot showed only an established SSH connection. This does not establish absence of past traffic, UDP traffic, or activity in other network namespaces.
- UDP `UNCONN` is normal for these sockets; UDP does not use TCP's LISTEN state.
- Wildcard SSH binds do not prove external or Internet accessibility. Routing, NAT, and upstream filtering remain unverified.

### SSH Verification

- ssh.socket: Listening observed. Both systemd and sshd hold the SSH socket descriptors in the supplied output.
- ssh.service: Startup and successful authenticated sessions observed.
- Socket activation: Supported by the socket ownership/cgroup evidence and journal sequence: socket listening first, service starting later.
- Unit enablement: ssh.socket enabled; ssh.service disabled. Explicit TriggeredBy/Triggers relationship confirmed.
- Dedicated SSH configuration syntax check (`sshd -t`): Passed, no output and exit code 0. Service startup precheck also reports success.
- Effective authentication settings: Reviewed from supplied configuration output, as listed below.
- New key-based login: Verified by supplied `Accepted publickey` events and subsequent session-open events.
- Authentication event observed in logs: Verified; ED25519 public-key authentication recorded.
- Password-only login test: Verified rejection for the tested connection. With public-key and keyboard-interactive authentication disabled on the client, the supplied client output is `Permission denied (publickey)`.
- Conditional `Match` settings: No active Match lines found by the supplied searches in the main configuration and sshd_config.d. The main file includes /etc/ssh/sshd_config.d/*.conf; no further Include lines appeared in the directory search.
- Loaded runtime configuration versus current on-disk configuration: Not independently compared.

| Setting | Observed value | Interpretation |
|---|---|---|
| port | 22 | Configured port; actual TCP listeners also observed on 22 |
| listenaddress | IPv4 and IPv6 wildcard, port 22 | Configuration agrees with observed bind scope |
| permitrootlogin | without-password | Alias of prohibit-password: root password and keyboard-interactive login disabled; root key login may remain possible subject to other controls |
| pubkeyauthentication | yes | Public-key authentication enabled |
| passwordauthentication | no | SSH password authentication disabled in the reviewed configuration |
| kbdinteractiveauthentication | no | Keyboard-interactive authentication disabled in the reviewed configuration |

`PermitRootLogin without-password` does not mean passwordless unrestricted root access, nor does it mean all direct root login is disabled. No root login test was supplied.

Additional SSH observations:

- One invalid-user attempt preceded a successful login with the intended account. This may be a client username mistake, but its origin must be confirmed by the operator; it is not sufficient evidence of an attack.
- User-requested disconnects and session closures appear in the logs; these entries alone do not indicate an SSH failure.
- Network context: Later networkd logs explicitly show carrier loss, DHCP lease loss, and acquisition of an address on a different private subnet. This explains an observed address transition, but does not establish why the network changed. Boot/session context still differs across batches.

### Firewall Review

- UFW state: Inactive at inspection.
- `sudo nft list ruleset`: Empty output with exit code 0; empty ruleset confirmed for that invocation.
- `sudo iptables -S`: INPUT, FORWARD, and OUTPUT policies all ACCEPT; no additional rules shown.
- `sudo ip6tables -S`: INPUT, FORWARD, and OUTPUT policies all ACCEPT; no additional rules shown.
- No restrictive host filtering is evidenced by the supplied commands. This does not establish the absence of every possible filtering mechanism or upstream firewall.
- The supplied inspection commands do not modify firewall configuration; no firewall change was reported.


### Log Review

- Available journal boots: Eight retained boots listed, indices -7 through 0. This is retained journal history, not necessarily the complete reboot history.
- Current-boot warnings and more severe messages: Supplied last-100-entry query reviewed. Later error-only query reviewed: pam_lastlog module load failures and sudo authentication-conversation failures observed. The latter do not establish a cause such as an incorrect password; later sudo execution succeeded in the supplied terminal session.
- Kernel warnings: Supplied current-boot last-100-entry query reviewed.
- SSH events: Unit and sshd-tag queries reviewed; successful public-key logins and session events observed.
- Journal disk usage: 126.7 MB reported for active and archived journals.
- Filesystem free space: Root filesystem reports 98G total, 7.2G used, 86G available, 8% usage.
- `/var/log`: Resolves to the same filesystem as `/` in the supplied `df` output; it is not a separate filesystem in this evidence.
- No immediate root-filesystem capacity pressure is evident. Inode usage was not checked.

### Findings and Follow-up

| Finding | Evidence and interpretation | Follow-up |
|---|---|---|
| PAM module load failure | Later output identifies `session optional pam_lastlog.so` at /etc/pam.d/login:82, consistent with the login-process module-load error. This supersedes the earlier no-reference search result | Reference identified; remediation not performed. Reason for the differing earlier search remains unknown; do not remove PAM lines blindly |
| CPU mitigation warnings | Intel Core i3-2330M, 2 cores/4 threads. lscpu reports MDS/L1TF mitigations with SMT vulnerable, MMIO stale data unknown/no mitigations, VMSCAPE IBPB mitigation | Some sysfs lines were truncated. Collect complete status and microcode context before mitigation decisions; these reports do not prove compromise |
| Firmware/resource warnings | ACPI address conflicts, gpio resource conflict, and lack of OS ASPM control | Record hardware/firmware context; investigate if relevant symptoms occur. No firmware or power-management change during this exercise |
| Storage capability warning | ATA device reports DRM functions and possible accessibility limitations | Investigate separately if storage symptoms occur; this alone does not establish disk failure |
| IMA configuration warning | Duplicate IMA measurements will not be recorded under the reported kernel configuration | Review only if IMA measurement requirements apply; not evidence of a failed disk or service |
| Energy policy message | ENERGY_PERF_BIAS changed from performance to normal | Record; no performance tuning during baseline inspection |
| Regulator fallback | at24 reports a missing supply and dummy regulator fallback | Record hardware context; impact not established |
| Suppressed audit-related messages | Kernel reports 108 suppressed callbacks | Review surrounding audit/kernel evidence if needed; supplied logs are not a complete audit trail |
| Cron environment warning | EXTRA_OPTS referenced but unset; unit uses an optional environment file. Later cron status is active/enabled and job execution is logged | No service failure demonstrated; no change made |
| Root SSH policy | Root key authentication is not categorically disabled by the reported setting | Decide policy during a separate hardening change, after access recovery verification |
| Host firewall inactive | UFW inactive, ACCEPT policies, no nft rules shown; access prerequisites now verified | 
| Clock consistency | Historical boot timestamps are non-monotonic; current synchronization is confirmed and current-boot clock adjustment is logged | Historical anomaly remains unexplained; no current synchronization failure demonstrated |
| Additional active service | Xray runtime, unit, executable metadata and fresh socket snapshots reviewed; no Xray socket observed in supplied snapshots | Intended role and installation provenance remain unestablished; evidence does not establish compromise |
| DNS feature fallback | Resolver falls back from UDP+EDNS0 to UDP for upstream DNS | Review if persistent or accompanied by lookup failures; not evidence that systemd is degraded |

### Access and Recovery — Verified

- Management-VM key-based SSH: Verified by the operator's successful session after explicitly selecting `~/.ssh/infra_labs_vm_ed25519` with `-i` and `IdentitiesOnly=yes`. Destination outputs identify `lab-server` and `greywolf`; sudo returned 0. The earlier invocation did not offer a key and failed; selecting the custom-named key resolved the tested connection.
- Independent local console: Verified. The operator confirmed using the physical laptop's own display and keyboard. Outputs identify `lab-server`, `greywolf`, `/dev/tty1`, and sudo exit code 0.
- These establish current access paths, not successful recovery after a reboot.

### PAM Follow-up — Evidence Reviewed

- `/etc/pam.d/login:82` contains `session optional pam_lastlog.so`. Current-boot login logs report failure to load that module. Local console login nevertheless succeeded.
- `grep` found no `pam_lastlog` match in `/etc/pam.conf` (exit code 1).
- `/etc/pam.d/login` is owned by package `login`, version `1:4.13+dfsg1-4ubuntu3.2`.
- `libpam0g`, `libpam-modules`, and `libpam-runtime` report version `1.5.3-5ubuntu5.7`.
- No diagnostic output was supplied for `sudo dpkg -V login libpam-modules libpam-runtime`; no exit status was supplied. This is not a complete integrity or security audit.
- The operator reports no PAM configuration or related package changes during this investigation. File timestamps alone do not establish who changed or installed files.


### Xray Follow-up — Evidence Reviewed

- Unit: `/etc/systemd/system/xray.service`, with drop-in `10-donot_touch_single_conf.conf`; active/running and enabled.
- Process runs as `xray` with parent PID 1. Executable: `/usr/local/bin/xray`; configuration: `/usr/local/etc/xray/config.json`.
- Unit sets User/Group `xray`, `NoNewPrivileges=yes`, `UMask=0077`, and bounding/ambient capabilities `CAP_NET_ADMIN`, `CAP_NET_BIND_SERVICE`, `CAP_NET_RAW`. Non-root execution does not imply absence of privileged network capabilities.
- Logs report Xray 26.3.27 and successful startup; the supplied version string has not been independently authenticated.
- Executable is root-owned, mode 0755, size 36,577,406 bytes. `dpkg-query -S` found no owning package for this path; this alone does not establish malicious installation.
- Configuration is owned by root:xray, mode 0640, size 3 bytes. Content was not supplied; an empty JSON object must not be assumed from size alone.
- A SHA-256 hash was collected, but no trusted-reference comparison was performed.
- File metadata records creation/modification around 2026-10-21 in the server's clock context; this does not identify the installer.
- Fresh listening/UDP and established-TCP snapshots were reviewed as described above; no Xray socket was shown. Historical or other network activity is not ruled out.
- Operator context: The server is the operator's personal physical laptop. The operator reports installing the system personally from a trusted source, no known Xray installation or VPN/proxy/panel installation script, and considers third-party access unlikely. These are operator statements, not independent provenance verification of the Xray binary. No compromise is established by the supplied evidence.

### Remaining Work


- Xray: Runtime and socket inspection completed; intended role, installation provenance, configuration structure, and trusted binary comparison remain unverified. No removal or service change performed.
- Service inventory: Reviewed, but some entries are ellipsized; retain complete names if a full service audit is required.
- Historical clock anomalies and complete CPU mitigation/microcode context: Unresolved as described above.
- Git review, commit and push of this document: Not verified.

