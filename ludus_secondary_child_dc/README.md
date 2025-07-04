# 🏗️ ludus_secondary_child_dc

Adds a secondary (replica) Domain Controller to an existing Active Directory domain. This role is designed to be a simple, reliable way to add redundancy and realism to your AD lab environments.

---

## 🧠 Description

This role is intended for use on a Windows VM that will become a replica DC in a domain that has already been created. It automates the installation of AD DS, configures DNS for reliable promotion, and promotes the server.

It is designed to be idempotent and includes a readiness check to ensure the role only completes when the new DC is fully operational.

---

## ‼️ Requirements

Before using this role, ensure the following requirements are met:

1.  **Ansible Collections:** The following Ansible collections must be installed on your Ludus server.
    ```bash
    ludus ansible collection add ansible.windows
    ludus ansible collection add microsoft.ad
    ```
2.  **Cross-VM Dependency:** This role requires that an existing domain controller for the target domain is fully operational before it runs. This dependency **must** be managed using the `depends_on` key in your `ludus-config.yml`, as shown in the example.

---

## 📌 Example — `ludus-config.yml`

This example builds upon our previous forest, adding a secondary DC to the child domain.

```yaml
# global_role_vars is a top-level block for defining reusable variables.
global_role_vars:
  credentials: &credentials
    ad_domain_admin: "domainadmin"
    ad_domain_admin_password: "ChangeMe123!"
    ad_domain_user: "domainuser"
    ad_domain_user_password: "UserUserPwd!"
    ad_domain_safe_mode_password: "SafeModePwd!"
  windows_hw_defaults: &windows_hw_defaults
    ram_gb: 8
    cpus: 4

# The 'defaults' block sets global values required by the Ludus schema.
defaults:
  <<: *credentials
  timezone: "America/Chicago"

# The main ludus block defining the VMs.
ludus:
  - vm_name: "{{ range_id }}-PARENT-DC1"
    # ... (Parent DC definition from previous example) ...
    hostname: "PARENT-DC1"
    template: win2019-server-x64-template
    <<: *windows_hw_defaults
    windows: { sysprep: true }
    vlan: 10
    ip_last_octet: 10
    domain: { fqdn: "parent.local", role: "primary-dc" }
    roles:
      - name: ludus_verify_dc_ready

  - vm_name: "{{ range_id }}-CHILD-DC1"
    # ... (Primary Child DC definition from previous example) ...
    hostname: "CHILD-DC1"
    template: win2019-server-x64-template
    <<: *windows_hw_defaults
    windows: { sysprep: true }
    vlan: 20
    ip_last_octet: 10
    roles:
      - name: ludus_create_child_domain
        depends_on:
          - { vm_name: "{{ range_id }}-PARENT-DC1", role: ludus_verify_dc_ready }
    role_vars:
      dns_domain_name: "child.parent.local"
      parent_dc_ip: "10.2.10.10"
      <<: *credentials

  - vm_name: "{{ range_id }}-CHILD-DC2"
    hostname: "CHILD-DC2"
    template: win2019-server-x64-template
    <<: *windows_hw_defaults
    windows: { sysprep: true }
    vlan: 20
    ip_last_octet: 11 # Give it a new IP in the same VLAN
    roles:
      - name: ludus_secondary_child_dc
        depends_on:
          # This secondary DC depends on the *primary* child DC being ready.
          # The ludus_create_child_domain role includes a readiness check.
          - vm_name: "{{ range_id }}-CHILD-DC1"
            role: ludus_create_child_domain
    role_vars:
      # --- Required Role Variables ---
      dns_domain_name: "child.parent.local"
      existing_dc_ip: "10.2.20.10" # IP of the first child DC
      
      # Pass credentials using the anchor
      <<: *credentials
```
---

## 🔧 Variables

### Required

| Variable                       | Description                                                  | Example                        |
| ------------------------------ | ------------------------------------------------------------ | ------------------------------ |
| `dns_domain_name`              | FQDN of the existing domain to join.                         | `child.parent.local`           |
| `existing_dc_ip`               | IP address of an existing DC in the domain to replicate from. | `10.2.20.10`                   |
| `ad_domain_admin`              | Admin username with permissions to add a DC to the domain.   | `domainadmin`                  |
| `ad_domain_admin_password`     | Password for the administrative account.                     | `"ChangeMe123!"`               |
| `ad_domain_safe_mode_password` | DSRM password for recovery mode on the new DC.               | `"SafeModePwd!"`               |

### Optional

These variables have default values defined in `defaults/main.yml`.

| Variable         | Default                     | Description                                       |
| ---------------- | --------------------------- | ------------------------------------------------- |
| `site_name`      | `"Default-First-Site-Name"` | AD site name where this DC will be placed.        |
| `ldap_port`      | `389`                       | Port for the LDAP readiness check.                |
| `ldap_timeout`   | `300`                       | Max time in seconds to wait for LDAP to be ready. |
| `ldap_delay`     | `15`                        | Delay in seconds before starting LDAP checks.     |

---

## ✅ Behavior

- Installs the `AD-Domain-Services` Windows feature.
- Explicitly sets the server's DNS to point to an existing DC to ensure reliable promotion.
- Promotes the host as a replica Domain Controller in the specified domain.
- Handles reboots automatically if required.
- Waits for the LDAP port (`389`) to confirm the new DC's services are running.

---

## 📎 License

MIT © H4cksty
