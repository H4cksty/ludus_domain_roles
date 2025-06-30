# Ludus Forest Build Roles

A collection of Ansible roles designed to automate the creation of complex, multi-domain Active Directory forests within the [Ludus](https://github.com/badsectorlabs/ludus) cyber range platform.

This suite of roles moves beyond Ludus's native domain creation capabilities to provide granular control over child domains, secondary controllers, and domain join processes, enabling the rapid deployment of sophisticated and realistic lab environments for red team and blue team training.

## Core Philosophy

These roles are designed to be:

* **Modular:** Each role has a single, specific purpose, allowing them to be composed like building blocks.
* **Integrated:** Roles are built to inherit credentials and settings from the global `defaults` block of your `ludus-config.yml`, simplifying configuration and reducing errors.
* **Robust:** Roles include logic to handle race conditions and environmental differences (e.g., Server vs. Client OS), making deployments more reliable.

---

## Roles in this Collection

This repository contains the following four roles:

### 1. `ludus_verify_dc_ready`

A minimal, lightweight role whose only purpose is to verify that a Domain Controller is online and its Active Directory services are responsive. It waits for the LDAP port (389) to become available. Its primary use is to serve as a reliable dependency target (`depends_on`) for other roles.

### 2. `ludus_create_child_domain`

Creates a new child domain and its first domain controller within an existing forest. This role automates the domain promotion and also creates the standard `domainadmin` and `domainuser` accounts in the new child domain, inheriting their credentials from the Ludus `defaults` block.

### 3. `ludus_secondary_child_dc`

Adds a secondary (backup) domain controller to an *existing* child domain. This is essential for building resilient and realistic domain structures. It also inherits its configuration from the Ludus `defaults` block where possible.

### 4. `ludus_join_child_domain`

Joins a Windows workstation or member server to a child domain created by the `ludus_create_child_domain` role. It includes logic to wait for the DC to be ready, retry the join process, and conditionally install RSAT tools on Server operating systems.

---

## Installation

To use these roles, clone this repository into a directory on your local machine. Then, for each role, use the `ludus ansible role add` command to upload it to your Ludus user environment.

```bash
# Example for one role
git clone [https://github.com/H4cksty/ludus_forest_build_roles.git](https://github.com/H4cksty/ludus_forest_build_roles.git)
cd ludus_forest_build_roles
ludus ansible role add -d ./ludus_create_child_domain
ludus ansible role add -d ./ludus_secondary_child_dc
# ... and so on for the other roles
```

---

## Comprehensive Example: Multi-Domain Forest

The following `ludus-config.yml` demonstrates how to use these roles in concert with Ludus's native capabilities to build a complete forest.

**Scenario:**

* A parent domain, `parent.local`, with a primary and secondary DC.
* A child domain, `child1.parent.local`.
* A second child domain, `child2.parent.local`, with a primary and secondary DC.
* A workstation joined to the parent domain.
* A workstation joined to the `child1` child domain.
* A file server joined to the `child2` child domain.

### `ludus-config.yml`

```yaml
# yaml-language-server: $schema=[https://docs.ludus.cloud/schemas/range-config.json](https://docs.ludus.cloud/schemas/range-config.json)
defaults:
  ad_domain_functional_level: Win2012R2
  ad_forest_functional_level: Win2012R2
  ad_domain_admin: domainadmin
  ad_domain_admin_password: "YourComplexPassword!"
  ad_domain_user: domainuser
  ad_domain_user_password: "AnotherPassword!"
  ad_domain_safe_mode_password: "YourComplexPassword!"
  timezone: America/Chicago

ludus:
  # =======================================================================
  # PARENT DOMAIN: parent.local (VLAN 10)
  # =======================================================================
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
        role: "primary-dc" # Using native Ludus role for the parent
    roles:
      # Apply the readiness check role so child domains can depend on it.
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
        role: "alt-dc" # Using native Ludus role for the secondary parent DC

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
        role: "member" # Using native Ludus role to join the parent domain

  # =======================================================================
  # CHILD DOMAIN 1: child1.parent.local (VLAN 20)
  # =======================================================================
  - vm_name: "{{ range_id }}-CHILD1-DC1"
    hostname: "CHILD1-DC1"
    template: win2019-server-x64-template
    vlan: 20
    ip_last_octet: 10
    ram_gb: 4
    cpus: 2
    windows:
      sysprep: true
    roles:
      - name: ludus_create_child_domain
        depends_on:
          - vm_name: "{{ range_id }}-PARENT-DC1"
            role: "ludus_verify_dc_ready"
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
    windows:
      sysprep: true
    roles:
      - name: ludus_join_child_domain
        depends_on:
          - vm_name: "{{ range_id }}-CHILD1-DC1"
            role: "ludus_create_child_domain"
    role_vars:
      dc_ip: "10.2.20.10"
      dns_domain_name: "child1.parent.local"

  # =======================================================================
  # CHILD DOMAIN 2: child2.parent.local (VLAN 30)
  # =======================================================================
  - vm_name: "{{ range_id }}-CHILD2-DC1"
    hostname: "CHILD2-DC1"
    template: win2022-server-x64-template
    vlan: 30
    ip_last_octet: 10
    ram_gb: 4
    cpus: 2
    windows:
      sysprep: true
    roles:
      - name: ludus_create_child_domain
        depends_on:
          - vm_name: "{{ range_id }}-PARENT-DC1"
            role: "ludus_verify_dc_ready"
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
    windows:
      sysprep: true
    roles:
      - name: ludus_secondary_child_dc
        depends_on:
          - vm_name: "{{ range_id }}-CHILD2-DC1"
            role: "ludus_create_child_domain"
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
    windows:
      sysprep: true
    roles:
      - name: ludus_join_child_domain
        depends_on:
          - vm_name: "{{ range_id }}-CHILD2-DC1"
            role: "ludus_create_child_domain"
    role_vars:
      dc_ip: "10.2.30.10"
      dns_domain_name: "child2.parent.local"
