---

## 🔧 Required Variables

| Variable                     | Description                                  | Example                    |
|------------------------------|----------------------------------------------|----------------------------|
| `dns_domain_name`            | FQDN of the child domain                     | `child.parent.local`       |
| `child_domain_netbios_name` | NETBIOS name of the child domain             | `CHILD`                    |
| `dc_ip`                      | IP address of a reachable domain controller  | `10.2.20.10`               |
| `ad_domain_admin`           | Admin UPN of the domain                      | `Administrator@child.parent.local` |
| `ad_domain_admin_password`  | Password for the domain admin                | `"ChangeMe123!"`           |

Optional:

| Variable         | Default                      | Description                          |
|------------------|------------------------------|--------------------------------------|
| `join_retries`   | `5`                          | Number of retries for domain join    |
| `join_delay`     | `15`                         | Delay between retries (seconds)      |
| `ldap_port`      | `389`                        | Port to probe during readiness check |
| `ldap_timeout`   | `300`                        | Max time (seconds) to wait for LDAP  |
| `ldap_delay`     | `10`                         | Delay before probing LDAP            |
| `install_rsat`   | `true`                       | Install RSAT tools on Server OS      |

---

## ✅ Behavior

- Waits for LDAP on the target DC
- Joins the host to the specified child domain
- Retries on failure (configurable)
- Reboots if required
- Installs RSAT tools on Server OS (optional)

---

## 📌 Example — `ludus_config.yml`

```yaml
global_role_vars:
  ad_domain_admin: "Administrator@child.parent.local"
  ad_domain_admin_password: "ChangeMe123!"
  ad_domain_safe_mode_password: "SafeModePwd!"
  ad_domain_user_password: "UserUserPwd!"

- vm_name: "{{ range_id }}-CHILD-WKS1"
  hostname: "CHILD-WKS1"
  template: win10-22h2-x64-enterprise-template
  vlan: 20
  ip_last_octet: 100
  roles:
    - name: ludus_join_child_domain
      depends_on:
        - vm_name: "{{ range_id }}-CHILD-DC1"
          role: ludus_create_child_domain
      vars:
        dns_domain_name: "child.parent.local"
        child_domain_netbios_name: "CHILD"
        dc_ip: "10.2.20.10"
        ad_domain_admin: "{{ global_role_vars.ad_domain_admin }}"
        ad_domain_admin_password: "{{ global_role_vars.ad_domain_admin_password }}"
        join_retries: 5
        join_delay: 15
        install_rsat: false  # Skip RSAT on workstations
```
