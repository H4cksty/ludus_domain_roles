# ludus_join_child_domain

Ansible role to join a machine to a child domain created by the `ludus_create_child_domain` Ansible role.

## Description
This role automates joining a Windows machine to an existing child domain. It is designed to work in tandem with the `ludus_create_child_domain` role, which creates the necessary `domainadmin` user account in the new child domain.

## IMPORTANT
This role requires all variables to be passed explicitly via `role_vars`. It is designed to be used with a `global_role_vars` block and YAML anchors in your main `ludus-config.yml`.

## Example

```yaml
# In your main ludus-config.yml
global_role_vars:
  simple_password: &simple_password "password"
  domain_admin_user: &domain_admin_user "domainadmin"

ludus:
  - vm_name: "{{ range_id }}-workstation-01"
    roles:
      - name: ludus_join_child_domain
        depends_on:
          - { vm_name: "{{ range_id }}-CHILD1-DC1", role: "ludus_create_child_domain" }
    role_vars:
      dc_ip: "10.2.20.10"
      dns_domain_name: "child1.parent.local"
      child_domain_netbios_name: "CHILD1"
      ad_domain_admin: *domain_admin_user
      ad_domain_admin_password: *simple_password
```
