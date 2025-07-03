# Ludus Forest Build Roles

A collection of Ansible roles designed to automate the creation of complex, multi-domain Active Directory forests within the [Ludus](https://github.com/badsectorlabs/ludus) cyber range platform.

This suite moves beyond Ludus’s native domain creation to provide granular control over child domains, secondary controllers, and member joins—ideal for rapid deployment of realistic red-team/blue-team lab environments.

---

## Core Philosophy

These roles are designed to be:

- Modular: each role does one thing, enabling composition like building blocks.  
- Integrated: credentials and settings are inherited from the global `defaults` block in your `ludus-config.yml`.  
- Robust: built-in readiness checks, retries, and conditional logic prevent race conditions and handle OS differences gracefully.

---

## Roles in this Collection

1. **ludus_verify_dc_ready**  
   A minimal, lightweight role that waits for LDAP (port 389) on a target DC. Use it as a `depends_on` guard for any domain-sensitive role.

2. **ludus_create_child_domain**  
   Creates a new child domain and promotes the first DC. Automates AD DS installation, promotion, post-promotion LDAP wait, and creation of `domainadmin`/`domainuser` accounts.

3. **ludus_secondary_child_dc**  
   Adds a secondary (replica) DC into an existing child domain. Ensures failover and realistic AD replication topology.

4. **ludus_join_child_domain**  
   Joins a Windows member (workstation or server) to a child domain. Includes LDAP-ready wait, join retries, optional RSAT install, and auto-reboot.

---

## Installation

Run this one-liner to fetch and install all roles into your current directory:

```bash
wget https://raw.githubusercontent.com/H4cksty/ludus_forest_build_roles/main/install_forest_build_roles.sh -O - | bash
```
This clones the repo, installs the roles into `roles/`, and readies you for Ludus.

---

## Acknowledgements

Inspired by [ChoiSG/ludus_ansible_roles](https://github.com/ChoiSG/ludus_ansible_roles). Refactored and extended to provide a cohesive, robust, and Ludus-native role suite.

---

## Comprehensive Example: Multi-Domain Forest

Below is a complete `ludus-config.yml` showing how to use these roles alongside Ludus’s native features to build:

- A parent domain with primary/secondary DCs and a member workstation.
- Two child domains (`child1` and `child2`), each with primary/secondary DCs and member servers.

```yaml
# yaml-language-server: $schema=https://docs.ludus.cloud/schemas/range-config.json

defaults:
  ad_domain_functional_level: Win2012R2
  ad_forest_functional_level: Win2012R2
  ad_domain_admin: domainadmin
  ad_domain_admin_password: "password"
  ad_domain_user: domainuser
  ad_domain_user_password: "password"
  ad_domain_safe_mode_password: "YourComplexPassword!"
  timezone: America/Chicago

ludus:
  # ----------------------------------------------------------------------
  # PARENT DOMAIN: parent.local (VLAN 10)
  # ----------------------------------------------------------------------
  - vm_name: "{{ range_id }}-PARENT-DC1"
    hostname: "PARENT-DC1"
    template: win2019-server-x64-template
    vlan: 10
    ip_last_octet: 10
    ram_gb: 6
    cpus: 2
    windows:
      sysprep: true
      domain:
        fqdn: "parent.local"
        role: "primary-dc"
    roles:
      - ludus_verify_dc_ready

  - vm_name: "{{ range_id }}-PARENT-DC2"
    hostname: "PARENT-DC2"
    template: win2019-server-x64-template
    vlan: 10
    ip_last_octet: 11
    ram_gb: 4
    cpus: 2
    windows:
      sysprep: true
      domain:
        fqdn: "parent.local"
        role: "alt-dc"

  - vm_name: "{{ range_id }}-PARENT-WKS1"
    hostname: "PARENT-WKS1"
    template: win10-22h2-x64-enterprise-template
    vlan: 10
    ip_last_octet: 100
    ram_gb: 4
    cpus: 2
    windows:
      sysprep: true
      domain:
        fqdn: "parent.local"
        role: "member"

  # ----------------------------------------------------------------------
  # CHILD DOMAIN 1: child1.parent.local (VLAN 20)
  # ----------------------------------------------------------------------
  - vm_name: "{{ range_id }}-CHILD1-DC1"
    hostname: "CHILD1-DC1"
    template: win2019-server-x64-template
    vlan: 20
    ip_last_octet: 10
    ram_gb: 4
    cpus: 2
    windows: { sysprep: true }
    roles:
      - name: ludus_create_child_domain
        depends_on:
          - { vm_name: "{{ range_id }}-PARENT-DC1", role: ludus_verify_dc_ready }
    role_vars:
      dns_domain_name: "child1.parent.local"
      parent_domain_netbios_name: "PARENT"
      parent_dc_ip: "10.2.10.10"

  - vm_name: "{{ range_id }}-CHILD1-WKS1"
    hostname: "CHILD1-WKS1"
    template: win10-22h2-x64-enterprise-template
    vlan: 20
    ip_last_octet: 100
    ram_gb: 4
    cpus: 2
    windows: { sysprep: true }
    roles:
      - name: ludus_join_child_domain
        depends_on:
          - { vm_name: "{{ range_id }}-CHILD1-DC1", role: ludus_create_child_domain }
    role_vars:
      dc_ip: "10.2.20.10"
      dns_domain_name: "child1.parent.local"
      child_domain_netbios_name: "CHILD1"

  # ----------------------------------------------------------------------
  # CHILD DOMAIN 2: child2.parent.local (VLAN 30)
  # ----------------------------------------------------------------------
  - vm_name: "{{ range_id }}-CHILD2-DC1"
    hostname: "CHILD2-DC1"
    template: win2022-server-x64-template
    vlan: 30
    ip_last_octet: 10
    ram_gb: 4
    cpus: 2
    windows: { sysprep: true }
    roles:
      - name: ludus_create_child_domain
        depends_on:
          - { vm_name: "{{ range_id }}-PARENT-DC1", role: ludus_verify_dc_ready }
    role_vars:
      dns_domain_name: "child2.parent.local"
      parent_domain_netbios_name: "PARENT"
      parent_dc_ip: "10.2.10.10"

  - vm_name: "{{ range_id }}-CHILD2-DC2"
    hostname: "CHILD2-DC2"
    template: win2022-server-x64-template
    vlan: 30
    ip_last_octet: 11
    ram_gb: 4
    cpus: 2
    windows: { sysprep: true }
    roles:
      - name: ludus_secondary_child_dc
        depends_on:
          - { vm_name: "{{ range_id }}-CHILD2-DC1", role: ludus_create_child_domain }
    role_vars:
      dns_domain_name: "child2.parent.local"
      parent_domain_netbios_name: "PARENT"
      existing_dc_ip: "10.2.30.10"

  - vm_name: "{{ range_id }}-CHILD2-FS1"
    hostname: "CHILD2-FS1"
    template: win2022-server-x64-template
    vlan: 30
    ip_last_octet: 50
    ram_gb: 4
    cpus: 2
    windows: { sysprep: true }
    roles:
      - name: ludus_join_child_domain
        depends_on:
          - { vm_name: "{{ range_id }}-CHILD2-DC1", role: ludus_create_child_domain }
    role_vars:
      dc_ip: "10.2.30.10"
      dns_domain_name: "child2.parent.local"
      child_domain_netbios_name: "CHILD2"
```
---

## 📎 License

MIT © H4cksty
