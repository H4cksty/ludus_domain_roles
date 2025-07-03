# 🧱 ludus_secondary_child_dc

Promotes a secondary Domain Controller into an existing child domain. This role ensures redundancy and replication in your Ludus forest by adding a second DC to a child domain created with `ludus_create_child_domain`.

---

## 🧠 Description

This role installs AD DS, promotes the host as a replica DC, and waits for LDAP services to become available. It is intended to run on a second VM in the same VLAN as the first child DC.

---

## 📌 Example — `ludus_config.yml`

```yaml
global_role_vars:
  ad_domain_admin: "Administrator@child.parent.local"
  ad_domain_admin_password: "ChangeMe123!"
  ad_domain_safe_mode_password: "SafeModePwd!"
  ad_domain_user_password: "UserUserPwd!"

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
        dns_domain_name: "child.parent.local"
        parent_domain_netbios_name: "PARENT"
        parent_dc_ip: "10.2.10.10"
        ad_domain_admin: "{{ global_role_vars.ad_domain_admin }}"
        ad_domain_admin_password: "{{ global_role_vars.ad_domain_admin_password }}"
        ad_domain_safe_mode_password: "{{ global_role_vars.ad_domain_safe_mode_password }}"
        ad_domain_user_password: "{{ global_role_vars.ad_domain_user_password }}"

- vm_name: "{{ range_id }}-CHILD-DC2"
  hostname: "CHILD-DC2"
  template: win2019-server-x64-template
  vlan: 20
  ip_last_octet: 11
  roles:
    - name: ludus_secondary_child_dc
      depends_on:
        - vm_name: "{{ range_id }}-CHILD-DC1"
          role: ludus_create_child_domain
      vars:
        dns_domain_name: "child.parent.local"
        parent_domain_netbios_name: "PARENT"
        existing_dc_ip: "10.2.20.10"
        site_name: "Default-First-Site-Name"
        dns_delegation: false
        ad_domain_admin: "{{ global_role_vars.ad_domain_admin }}"
        ad_domain_admin_password: "{{ global_role_vars.ad_domain_admin_password }}"
        ad_domain_safe_mode_password: "{{ global_role_vars.ad_domain_safe_mode_password }}"
```
---

## 🔧 Required Variables

| Variable                     | Description                                  | Example                    |
|------------------------------|----------------------------------------------|----------------------------|
| `dns_domain_name`            | FQDN of the child domain                     | `child.parent.local`       |
| `parent_domain_netbios_name`| NETBIOS name of parent                       | `PARENT`                   |
| `existing_dc_ip`            | IP address of the first child DC             | `10.2.20.10`               |
| `ad_domain_admin`           | Admin UPN of the domain                      | `Administrator@child.parent.local` |
| `ad_domain_admin_password`  | Password for the domain admin                | `"ChangeMe123!"`           |
| `ad_domain_safe_mode_password` | Safe Mode (DSRM) password                 | `"SafeModePwd!"`           |

Optional:

| Variable         | Default                      | Description                          |
|------------------|------------------------------|--------------------------------------|
| `site_name`      | `"Default-First-Site-Name"`  | AD Site to place this DC             |
| `dns_delegation` | `false`                      | Whether to allow DNS delegation      |
| `ldap_port`      | `389`                        | Port to probe during readiness check |
| `ldap_timeout`   | `300`                        | Max time (seconds) to wait for LDAP  |
| `ldap_delay`     | `10`                         | Delay before probing LDAP            |

---

## ✅ Behavior

- Installs AD DS if not present
- Promotes the host as a replica Domain Controller in an existing child domain
- Supports reboot after promotion (if required)
- Waits for the LDAP service (port 389) to confirm readiness
- Fully idempotent and safe to rerun

---

## 📎 License

MIT © H4cksty
