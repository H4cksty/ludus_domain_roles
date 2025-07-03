# 🔐 Ludus Create Child Domain

This Ansible role provisions a new **child domain** inside an existing Active Directory forest using Windows Server. It installs AD DS, promotes the host to a domain controller (DC), and ensures proper domain user provisioning in accordance with Ludus conventions.

---

## 🧩 Role Metadata

| Key         | Value                        |
|-------------|------------------------------|
| **Role Name** | `ludus_create_child_domain`  |
| **Role Type** | `user-defined-role`          |
| **Dependencies** | A working parent domain controller must be reachable from this host. |
| **Supports Reboot** | ✅ Yes — performs controlled reboots when required. |
| **OS Compatibility** | Windows Server 2016, 2019, 2022 |
| **Ludus Constraint Compatibility** | ✅ Uses `global_role_vars`, avoids `depends_on` misuse, UPN format enforced |

---

## 🔧 Required Variables

These variables must be set in `vars:` under the role block in your `ludus_config.yml`.

| Variable Name                | Description                                  | Format / Example |
|-----------------------------|----------------------------------------------|------------------|
| `dns_domain_name`           | FQDN of the new child domain                 | `child.example.local` |
| `parent_domain_netbios_name` | NETBIOS name of the parent domain           | `EXAMPLE` |
| `parent_dc_ip`              | IP address of the parent domain controller   | `192.168.1.1` |

**Credential Variables** — should be declared in `global_role_vars`:

| Variable Name                      | Purpose                               |
|-----------------------------------|----------------------------------------|
| `ad_domain_admin`                 | User with AD join + promote rights     |
| `ad_domain_admin_password`        | Password for that user                 |
| `ad_domain_safe_mode_password`    | Safe Mode (DSRM) password              |
| `ad_domain_user_password`         | Password for domainadmin & domainuser |

Optional:

| Variable Name         | Description                           | Default |
|----------------------|---------------------------------------|---------|
| `site_name`          | AD Site for the DC                    | `Default-First-Site-Name` |
| `dns_delegation`     | Whether to delegate DNS on parent DC  | `false` |

---

## 🛠️ Example `ludus_config.yml`

```yaml
global_role_vars:
  ad_domain_admin: "Administrator"
  ad_domain_admin_password: "ChangeMe123!"
  ad_domain_safe_mode_password: "SafeModePwd!"
  ad_domain_user_password: "UserUserPwd!"

roles:
  - id: 101
    name: ludus_create_child_domain
    type: user-defined-role
    depends_on: [100]
    vars:
      dns_domain_name: "child.example.local"
      parent_domain_netbios_name: "EXAMPLE"
      parent_dc_ip: "192.168.1.1"
      site_name: "Default-First-Site-Name"
      dns_delegation: false

      # Pull in global vars (or use anchors)
      ad_domain_admin: "{{ global_role_vars.ad_domain_admin }}"
      ad_domain_admin_password: "{{ global_role_vars.ad_domain_admin_password }}"
      ad_domain_safe_mode_password: "{{ global_role_vars.ad_domain_safe_mode_password }}"
      ad_domain_user_password: "{{ global_role_vars.ad_domain_user_password }}"
