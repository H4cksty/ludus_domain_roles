# 🏗️ ludus_create_child_domain

Creates a new child Active Directory domain in an existing forest and promotes the current host to be its first Domain Controller (DC). This role is designed for security and robustness, with built-in credential protection, readiness checks, and automatic account creation.

---

## 🧠 Description

This role is intended for use on a Windows VM that will become the first DC of a new child domain. It automates the entire provisioning process, from installing the required Windows features to creating default user accounts.

It is designed to be idempotent and safe to run multiple times. Passwords and other secrets are handled securely and will not be logged.

---

## ‼️ Requirements

Before using this role, ensure the following requirements are met:

1.  **Ansible Collection:** The `ansible.windows` collection must be installed on your Ludus server. You can install it with:
    ```bash
    ludus ansible collection add ansible.windows
    ```
2.  **Role Dependency:** This role depends on `ludus_verify_dc_ready`. The `meta/main.yml` file handles this dependency automatically, so Ansible will ensure the parent DC is ready before this role runs.

---

## 📌 Example — `ludus-config.yml`

This example demonstrates how to use a `defaults` block with YAML anchors to define credentials once and reuse them across multiple roles, keeping the configuration clean.

```yaml
# The 'defaults' block sets global values for the entire range.
# We use YAML anchors (&) to define reusable blocks for credentials.
defaults:
  role_vars:
    credentials: &credentials
      ad_domain_admin: "Administrator@parent.local"
      ad_domain_admin_password: "ChangeMe123!"
      ad_domain_safe_mode_password: "SafeModePwd!"
      ad_domain_user_password: "UserUserPwd!"

ludus:
  - vm_name: "{{ range_id }}-PARENT-DC1"
    hostname: "PARENT-DC1"
    template: win2019-server-x64-template
    vlan: 10
    ip_last_octet: 10
    domain:
      fqdn: "parent.local"
      role: "primary-dc"
    roles:
      # This role is used as a dependency check by the child DC.
      - name: ludus_verify_dc_ready
        vars:
          ldap_timeout: 300

  - vm_name: "{{ range_id }}-CHILD-DC1"
    hostname: "CHILD-DC1"
    template: win2019-server-x64-template
    vlan: 20
    ip_last_octet: 10
    roles:
      - name: ludus_create_child_domain
        # This 'depends_on' block ensures this role only runs AFTER
        # the parent DC is verified to be ready.
        depends_on:
          - vm_name: "{{ range_id }}-PARENT-DC1"
            role: ludus_verify_dc_ready
        vars:
          # --- Required Variables ---
          dns_domain_name: "child.parent.local"
          parent_domain_netbios_name: "PARENT"
          parent_dc_ip: "10.2.10.10" # Use the IP of the parent DC

          # --- Optional Variables (overriding defaults) ---
          site_name: "Child-Site"

          # Use the YAML merge key (<<) to include the credentials anchor.
          <<: *credentials
```

---

## 🔧 Variables

### Required

| Variable                       | Description                                                  | Example                        |
| ------------------------------ | ------------------------------------------------------------ | ------------------------------ |
| `dns_domain_name`              | FQDN of the new child domain.                                | `child.parent.local`           |
| `parent_domain_netbios_name`   | NETBIOS name of the parent domain.                           | `PARENT`                       |
| `parent_dc_ip`                 | IP address of a Domain Controller in the parent domain.      | `10.2.10.10`                   |
| `ad_domain_admin`              | Admin UPN with Enterprise Admins or Domain Admins of the forest root permissions. | `Administrator@parent.local`   |
| `ad_domain_admin_password`     | Password for the forest-level admin account.                 | `"ChangeMe123!"`               |
| `ad_domain_safe_mode_password` | DSRM password for recovery mode on the new DC.               | `"SafeModePwd!"`               |
| `ad_domain_user_password`      | Password for the new `domainadmin` and `domainuser` accounts. | `"UserUserPwd!"`               |

### Optional

These variables have default values defined in `defaults/main.yml`.

| Variable         | Default                     | Description                                       |
| ---------------- | --------------------------- | ------------------------------------------------- |
| `site_name`      | `"Default-First-Site-Name"` | AD site name where this DC will be placed.        |
| `dns_delegation` | `no`                        | Whether to create a DNS delegation in the parent. |
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
