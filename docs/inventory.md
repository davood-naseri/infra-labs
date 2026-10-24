# Novatech Logistics Infrastructure Inventory

This document provides a human-readablech Logistics Infrastructure Inventory

This document provides a human-readable inventory of the planned infrastructure assets lab environment and is based on the source data stored in:
```text
data/inventory.yaml

## Inventory Summary

| Site | Location | Asset Count |
|---|---|---:|
| HQ | Amsterdam | 5 |
| Branch | Rotterdam | 3 |
| Azure | West Europe | 4 |
| **Total** | **All locations** | **12** |

## HQ — Amsterdam

| Asset | Type | IP Address | Subnet | Role |
|---|---|---|---|---|
| `hq-fw-01` | Firewall | `10.10.0.1` | `10.10.0.0/24` | Edge firewall and VPN endpoint |
| `hq-core-sw01` | Layer 3 switch | `10.10.1.1` | `10.10.1.0/24` | Core switching and routing |
| `hq-dc-01` | Server | `10.10.10.10` | `10.10.10.0/24` | Active Directory and DNS |
| `hq-mon-01` | Server | `10.10.10.50` | `10.10.10.0/24` | Infrastructure monitoring |
| `hq-nas-backup` | NAS | `10.10.20.15` | `10.10.20.0/24` | Central backup repository |

### HQ Notes

- `hq-fw-01` provides Internet access and VPN connectivity.
- `hq-core-sw01` provides Layer 3 routing between internal networks.
- `hq-dc-01` provides Active Directory Domain Services and DNS.
- `hq-mon-01` is used for infrastructure monitoring.
- `hq-nas-backup` stores backup data for supported systems.

## Branch — Rotterdam

| Asset | Type | IP Address | Subnet | Role |
|---|---|---|---|---|
| `rtm-fw-01` | Firewall | `10.20.0.1` | `10.20.0.0/24` | Branch firewall and VPN endpoint |
| `rtm-acc-sw01` | Access switch | `10.20.1.10` | `10.20.1.0/24` | Warehouse access switching |
| `rtm-app-01` | Server | `10.20.10.20` | `10.20.10.0/24` | Warehouse Management System |

### Branch Notes

- `rtm-fw-01` provides local security controls and the IPsec VPN connection to HQ.
- `rtm-acc-sw01` connects warehouse devices and local infrastructure.
- `rtm-app-01` hosts the local Warehouse Management System application.

## Azure — West Europe

| Asset | Type | Address or Endpoint | Subnet | Role |
|---|---|---|---|---|
| `az-vnet-gw` | Azure VPN Gateway | Azure-managed allocation | `GatewaySubnet` | Site-to-site VPN |
| `az-id-sync01` | Virtual machine | `10.30.10.4` | `10.30.10.0/24` | Microsoft Entra Connect Sync |
| `az-app-prod01` | Virtual machine | `10.30.20.10` | `10.30.20.0/24` | Docker logistics application |
| `az-db-prod01` | SQL Managed Instance | Service-provided endpoint | `10.30.30.0/24` | Application database |

### Azure Notes

- The Azure virtual network uses the address space `10.30.0.0/16`.
- `GatewaySubnet` is reserved for the Azure VPN Gateway.
- `az-id-sync01` requires connectivity to the on-premises Active Directory environment.
- `az-app-prod01` hosts the logistics tracking application.
- `az-db-prod01` provides the database service for the application.

## Network Relationships

text
Internet
  |
  hq-fw-01
  |
  hq-core-sw01
  |-- hq-dc-01
  |-- hq-mon-01
  `-- hq-nas-backup

rtm-fw-01
  |
  rtm-acc-sw01
  `-- rtm-app-01

rtm-fw-01 <--- IPsec site-to-site VPN ---> hq-fw-01

hq-fw-01 <--- IPsec site-to-site VPN ---> az-vnet-gw

hq-dc-01 <--- Active Directory connectivity ---> az-id-sync01

az-id-sync01--- Active Directory connectivity ---> az-id-sync01

az-id-sync01 ---> Microsoft Entra ID Addressing Summary

| Network | Location | Intended Use |
|---|---|---|
| `10.10.0.0/24` | HQ | Firewall network |
| `10.10.1.0/24` | HQ | Core switch or routed network |
| `10.10.10.0/24` | HQ | Server network |
| `10.10.20.0/24` | HQ | Backup network |
| `10.20.0.0/24` | Rotterdam | Firewall network |
| `10.20.1.0/24` | Rotterdam | Access switch network |
| `10.20.10.0/24` | Rotterdam | Application network |
| `10.30.0.0/16` | Azure | Azure virtual network |
| `10.30.0.0/24` | Azure | VPN Gateway subnet |
| `10.30.10.0/24` | Azure | Identity synchronization |
| `10.30.20.0/24` | Azure | Application workload |
| `10.30.30.0/24` | Azure | Database workload |

## Operational Considerations

- The IP addresses in this document are planned lab addresses.
- Production firewall policies are not included in this inventory.
- VPN tunnel configuration details are intentionally omitted.
- Backup retention and monitoring thresholds require separate documentation.
- Azure VPN Gateway addresses are managed by Azure and are not manually assigned in this inventory.
- SQL Managed Instance uses a service-provided DNS endpoint rather than a manually assigned host address.

## Source and Generation

The source inventory is stored at:

```text
data/inventory.yaml

