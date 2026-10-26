# Infrastructure Labs

Hands-on infrastructure labs documenting practical learning, verified results, and work in progress.

## Projects

### Secure Linux Server Baseline

An Ubuntu Server home lab focused on Linux administration and secure administrative access.

Topics include:

- Hardware, operating system, storage, and network inventory
- Time synchronization
- SSH key-based authentication
- Linux ownership and permissions
- Service and listening-port inspection
- Planned firewall hardening
- Planned Ansible automation

**Status:** In progress. Verified results and pending tasks are documented in the project README.

[View the Linux Server Baseline project](linux/server-baseline/README.md)

## Repository Layout

- `README.md`: repository overview
- `linux/server-baseline/README.md`: Linux server inventory, verified configuration, exercises, and pending tasks

## Documentation Principles

- Record actual observations and verified results.
- Distinguish completed work from planned or unverified tasks.
- Document troubleshooting steps and operational limitations.
- Review changes before publishing.

## Security and Privacy

Do not commit:

- Passwords, tokens, or other credentials
- Private SSH keys
- VPN subscription links
- Configuration files containing credentials
- Sensitive machine identifiers or unnecessary network details

Sanitize logs and screenshots before publishing.

## Scope

This repository contains learning labs. It is not a completed production security baseline.

The Docker project is maintained in a separate repository. Azure design work is also kept separate from the Linux server baseline.
