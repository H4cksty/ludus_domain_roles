# 🔗 ludus_join_child_domain

Joins a Windows host to an existing child domain within your Ludus forest. This role handles wait logic, retries, rebooting if needed, and optional RSAT installation. It's a dependable building block for member workstations, utility servers, or any domain-bound infrastructure.

---

## 🧠 Description

This role performs a secure and automated domain join against a previously created child domain. It waits for LDAP services to be ready, retries joining if the DC isn’t immediately responsive, and reboots the machine when successful.

You can use this role on either Server or Workstation templates. It supports both `user@domain.local` UPN-based logins and Ludus’s YAML-driven sequencing.

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
        install_rsat: false
```
## 🔧 Required Variables

| Variable                     | Description                                  | Example                         |
|-----------------------------|----------------------------------------------|---------------------------------|
| `dns_domain_name`           | FQDN of the child domain                     | `child.parent.local`            |
| `child_domain_netbios_name`| NETBIOS name of the domain                   | `CHILD`                         |
| `dc_ip`                     | IP address of a reachable DC                | `10.2.20.10`                    |
| `ad_domain_admin`           | Admin UPN for the domain join               | `Administrator@child.parent.local` |
| `ad_domain_admin_password`  | Password for the above                      | `"ChangeMe123!"`                |

**Optional:**

| Variable         | Default  | Description                              |
|------------------|----------|------------------------------------------|
| `join_retries`   | `5`      | Number of times to retry join            |
| `join_delay`     | `15`     | Seconds between retries                  |
| `install_rsat`   | `true`   | Installs RSAT tools on Server OS         |
| `ldap_port`      | `389`    | Port used to check LDAP availability     |
| `ldap_timeout`   | `300`    | Timeout for LDAP check (seconds)         |
| `ldap_delay`     | `10`     | Delay before starting LDAP check         |

---

## ✅ Behavior

- Waits for the child DC’s LDAP service to be online  
- Joins the machine to the specified domain  
- Retries if join fails initially  
- Reboots if required after successful join  
- Optionally installs RSAT (only on Server editions)

---

## 📎 License

MIT © H4cksty
