# 🏗️ ludus_create_child_domain

Creates a new child Active Directory domain in an existing forest and promotes the current host to a Domain Controller (DC). This role ensures the new DC is fully provisioned and includes built-in LDAP readiness checks and account creation.

---

## 🧠 Description

This role is intended for use on a Windows VM that will become the first DC of a child domain. It installs the required AD DS features, performs the promotion into the child domain, waits for services like LDAP to start, and creates two basic domain accounts:

- `domainadmin@child.domain.local`
- `domainuser@child.domain.local`

---

## 🔌 Usage Example in `ludus_config.yml`

```yaml
# PARENT DC
- vm_name: "{{ range_id }}-PARENT-DC1"
  hostname: "PARENT-DC1"
  template: win2019-server-x64-template
  vlan: 10
  ip_last_octet: 10
  domain:
    fqdn: "parent.local"
    role: "primary-dc"
  roles:
    # Signals when the DC is ready for child joins
    - name: ludus_verify_dc_ready

# CHILD DC
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
        parent_dc_ip: "192.168.10.10"
        site_name: "Default-First-Site-Name"
        dns_delegation: false

        ad_domain_admin: "{{ global_role_vars.ad_domain_admin }}"
        ad_domain_admin_password: "{{ global_role_vars.ad_domain_admin_password }}"
        ad_domain_safe_mode_password: "{{ global_role_vars.ad_domain_safe_mode_password }}"
        ad_domain_user_password: "{{ global_role_vars.ad_domain_user_password }}"
