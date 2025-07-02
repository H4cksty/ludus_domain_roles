# ludus_join_child_domain

Ansible role to join a machine to a child domain created by the `ludus_create_child_domain` Ansible role.

## Description
This role automates joining a Windows machine to an existing child domain. It is designed to work in tandem with the `ludus_create_child_domain` role, which creates the necessary `domainadmin` user account in the new child domain.

This role will use the `ad_domain_admin` and `ad_domain_admin_password` variables defined in the `defaults` block of your main `ludus-config.yml`.

## Example

```yaml
# In your main ludus-config.yml

defaults:
  # ... other defaults
  ad_domain_admin: domainadmin
  ad_domain_admin_password: "password"
  # ...

ludus:
  # ... parent and child DCs are defined here ...

  - vm_name: "{{ range_id }}-workstation-01"
    hostname: "WKS01"
    template: win10-22h2-x64-enterprise-template
    vlan: 20
    ip_last_octet: 101
    windows:
      sysprep: true
    roles:
      - name: ludus_join_child_domain
        depends_on:
          - vm_name: "{{ range_id }}-CHILD1-DC1" # Depends on the child DC
            role: "ludus_create_child_domain"
    role_vars:
      dc_ip: "10.2.20.10"
      dns_domain_name: "child1.parent.local"
      child_domain_netbios_name: "CHILD1" # The NETBIOS name of the domain to join
      # The role will inherit ad_domain_admin and ad_domain_admin_password
      # from the 'defaults' block automatically.
```
