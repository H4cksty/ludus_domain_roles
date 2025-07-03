# 🏗️ ludus_create_child_domain

Creates a new child Active Directory domain in an existing forest and promotes the current host to a Domain Controller (DC). This role ensures the new DC is fully provisioned and includes built-in LDAP readiness checks and account creation.

---

## 🧠 Description

This role is intended for use on a Windows VM that will become the first DC of a child domain. It installs the required AD DS features, performs the promotion into the child domain, waits for services like LDAP to start, and creates two basic domain accounts:

- `domainadmin@child.domain.local`
- `domainuser@child.domain.local`

---

## 📌 Example — `ludus_config.yml`

```yaml
global_role_vars:
  ad_domain_admin: "Administrator@parent.local"
  ad_domain_admin_password: "ChangeMe123!"
  ad_domain_safe_mode_password: "SafeModePwd!"
  ad_domain_user_password: "UserUserPwd!"

  base_retry: &base_retry
    retries: 5
    delay: 30

- vm_name: "{{ range_id }}-PARENT-DC1"
  hostname: "PARENT-DC1"
  template: win2019-server-x64-template
  vlan: 10
  ip_last_octet: 10
  domain:
    fqdn: "parent.local"
    role: "primary-dc"
  roles:
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
      depends_on:
        - vm_name: "{{ range_id }}-PARENT-DC1"
          role: ludus_verify_dc_ready
      vars:
        <<: *base_retry

        dns_domain_name: "child.parent.local"
        parent_domain_netbios_name: "PARENT"
        parent_dc_ip: "192.168.10.10"

        site_name: "Default-First-Site-Name"
        dns_delegation: false
        ldap_port: 389
        ldap_timeout: 300
        ldap_delay: 10

        ad_domain_admin: "{{ global_role_vars.ad_domain_admin }}"
        ad_domain_admin_password: "{{ global_role_vars.ad_domain_admin_password }}"
        ad_domain_safe_mode_password: "{{ global_role_vars.ad_domain_safe_mode_password }}"
        ad_domain_user_password: "{{ global_role_vars.ad_domain_user_password }}"
```
## 🔧 Required Variables

| Variable                      | Description                                | Example                        |
|-------------------------------|--------------------------------------------|--------------------------------|
| `dns_domain_name`             | FQDN of the new child domain               | `child.parent.local`           |
| `parent_domain_netbios_name` | NETBIOS name of the parent domain          | `PARENT`                       |
| `parent_dc_ip`               | IP address of the parent Domain Controller | `192.168.10.10`                |
| `ad_domain_admin`            | Admin UPN with forest-level permissions    | `Administrator@parent.local`   |
| `ad_domain_admin_password`   | Password for the above admin               | `"ChangeMe123!"`               |
| `ad_domain_safe_mode_password` | DSRM password for recovery mode          | `"SafeModePwd!"`               |
| `ad_domain_user_password`    | Password assigned to domainadmin/user      | `"UserUserPwd!"`               |

**Optional:**

| Variable         | Default                     | Description                              |
|------------------|-----------------------------|------------------------------------------|
| `site_name`      | `"Default-First-Site-Name"` | AD site name where this DC will be placed |
| `dns_delegation` | `false`                     | Whether to delegate DNS                  |
| `ldap_port`      | `389`                       | Port for LDAP readiness check            |
| `ldap_timeout`   | `300`                       | Max time to wait for LDAP (seconds)      |
| `ldap_delay`     | `10`                        | Delay before checking LDAP readiness     |

---

## ✅ Behavior

- Installs the AD-Domain-Services Windows feature  
- Promotes the host into a child domain as its first Domain Controller  
- Handles reboots automatically if required  
- Waits for LDAP port 389 to confirm DC readiness  
- Creates `domainadmin@child.domain` (Domain Admins) and `domainuser@child.domain` (Domain Users)

---

## 📎 License

MIT © H4cksty
