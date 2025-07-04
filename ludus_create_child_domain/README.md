# 🏗️ ludus_create_child_domain

Creates a new child Active Directory domain in an existing forest and promotes the current host to be its first Domain Controller (DC). This role is designed for security and robustness, with built-in credential protection, readiness checks, and automatic account creation.

---

## 🧠 Description

This role is intended for use on a Windows VM that will become the first DC of a new child domain. It automates the entire provisioning process, from installing the required Windows features to creating default user accounts.

It is designed to be idempotent and safe to run multiple times. Passwords and other secrets are handled securely and will not be logged during production runs (by re-enabling `no_log: true`).

---

## ‼️ Requirements (these are usually installed in Ludus by default)

Before using this role, ensure the following requirements are met:

1.  **Ansible Collections:** The following Ansible collections must be installed on your Ludus server.
    ```bash
    ludus ansible collection add ansible.windows
    ludus ansible collection add microsoft.ad
    ```
2.  **Cross-VM Dependency:** This role requires that the parent domain controller is fully operational before it runs. This dependency **must** be managed using the `depends_on` key in your `ludus-config.yml`, as shown in the example. This prevents a race condition by ensuring the parent DC is ready before the child DC promotion begins.

---

## 📌 Example — `ludus-config.yml`

This example demonstrates the correct structure for a Ludus configuration file. Note that `roles` and `role_vars` are sibling keys under the VM definition.

```yaml
#================================================================================
# Wide open networking for setup, troubleshooting, and downloading tools
#================================================================================
network:
  inter_vlan_default: ACCEPT
  external_default: ACCEPT

#================================================================================
#   Global vars... are global, even in user-defined-roles. "Namespaced" and 
#   YAML anchors added for modularity and groupings.
#================================================================================
global_role_vars:
  # The first set of variables are "namespaced" to prevent 
  credentials: &credentials
    ad_domain_admin: "domainadmin"
    ad_domain_admin_password: "ChangeMe123!"
    ad_domain_user: "domainuser"
    ad_domain_user_password: "UserUserPwd!"
    ad_domain_safe_mode_password: "SafeModePwd!"
  functional_level: &functional_level "Win2012R2"
  windows_hw_defaults: &windows_hw_defaults
    ram_min_gb: 1
    ram_gb: 8
    cpus: 4
  linux_hw_defaults: &linux_hw_defaults
    ram_min_gb: 1
    ram_gb: 2
    cpus: 1
  # The Below Variables will be utilized by all VMs (overriding the defaults)
  # Assigning these manually under the VM SHOULD override this... needs testing
  # Should this VM be a full clone (true) or linked clone (false). Default: false
  full_clone: false
  testing:
    snapshot: true          # Snapshot this VM going into testing, and revert it coming out of testing. Default: true
    block_internet: true    # Cut this VM off from the internet during testing. Default true

#================================================================================
#   Default must All be declared if any are.
#================================================================================
defaults:
  snapshot_with_RAM: false
  stale_hours: 0
  ad_domain_functional_level: *functional_level
  ad_forest_functional_level: *functional_level
  <<: *credentials
  timezone: "America/Chicago"
  enable_dynamic_wallpaper: true

#================================================================================
#   The VMS!!!!
#================================================================================
ludus:
  - vm_name: "{{ range_id }}-PARENT-DC1"
    hostname: "PARENT-DC1"
    template: win2019-server-x64-template
    <<: *windows_hw_defaults  # single line for vars that will be duplicated
    windows:
      sysprep: true
    vlan: 10
    ip_last_octet: 10
    domain:
      fqdn: "parent.local"
      role: "primary-dc"
    roles:
      - name: ludus_verify_dc_ready  # make sure the dc is running before others try to connect

  - vm_name: "{{ range_id }}-CHILD-DC1"
    hostname: "CHILD-DC1"
    template: win2019-server-x64-template
    <<: *windows_hw_defaults
    windows:
      sysprep: true
    vlan: 20
    ip_last_octet: 10
    roles:
      - name: ludus_create_child_domain
        depends_on:
          - vm_name: "{{ range_id }}-PARENT-DC1"
            role: ludus_verify_dc_ready
    # 'role_vars' is at the same level as 'roles', 'vlan', etc.
    # Its contents are passed to all roles listed above for this VM.
    role_vars:
      # --- Required Role Variables ---
      dns_domain_name: "child.parent.local"
      parent_domain_name: "parent.local"
      # Pass credentials using the anchor
      <<: *credentials
```
---

## 🔧 Variables

### Required

| Variable                       | Description                                                  | Example                        |
| ------------------------------ | ------------------------------------------------------------ | ------------------------------ |
| `dns_domain_name`              | FQDN of the new child domain.                                | `child.parent.local`           |
| `parent_domain_name`           | FQDN of the parent domain.                                   | `parent.local`                 |
| `ad_domain_admin`              | Admin UPN with Enterprise Admins or Domain Admins of the forest root permissions. | `domainadmin`   |
| `ad_domain_admin_password`     | Password for the forest-level admin account.                 | `"ChangeMe123!"`               |
| `ad_domain_safe_mode_password` | DSRM password for recovery mode on the new DC.               | `"SafeModePwd!"`               |
| `ad_domain_user_password`      | Password for the new `domainadmin` and `domainuser` accounts. | `"UserUserPwd!"`               |

### Optional

These variables have default values defined in `defaults/main.yml`.

| Variable         | Default                     | Description                                       |
| ---------------- | --------------------------- | ------------------------------------------------- |
| `ldap_port`      | `389`                       | Port for the LDAP readiness check.                |
| `ldap_timeout`   | `300`                       | Max time in seconds to wait for LDAP to be ready. |
| `ldap_delay`     | `15`                        | Delay in seconds before starting LDAP checks.     |

---

## ✅ Behavior

- Installs the `AD-Domain-Services` Windows feature.
- Promotes the host into a child domain as its first Domain Controller.
- Handles reboots automatically if required.
- Waits for the LDAP port (`389`) to confirm DC services are running.
- Creates two new accounts in the child domain:
  - `domainadmin@<child_domain>` (member of Domain Admins)
  - `domainuser@<child_domain>` (member of Domain Users)

---

## 📎 License

MIT © H4cksty
