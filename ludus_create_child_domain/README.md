# ludus_create_child_domain

Ansible role to create a new child domain and its first domain controller.

## Description
This role automates the creation of a new child domain within an existing Active Directory forest. It performs the following actions:
1.  Promotes the target server to a domain controller for the new child domain.
2.  Creates a `domainadmin` user with administrative privileges in the new child domain.
3.  Creates a standard `domainuser` in the new child domain.

## IMPORTANT
This role requires all variables to be passed explicitly via `role_vars`. It is designed to be used with a `global_role_vars` block and YAML anchors in your main `ludus-config.yml` for clarity and consistency.

## Example

```yaml
# In your main ludus-config.yml
global_role_vars:
  complex_password: &complex_password "YourComplexPassword!"
  simple_password: &simple_password "password"
  domain_admin_user: &domain_admin_user "domainadmin"
  domain_user_user: &domain_user_user "domainuser"
  parent_netbios: &parent_netbios "PARENT"
  parent_dc_ip: &parent_dc_ip "10.2.10.10"

ludus:
  - vm_name: "{{ range_id }}-CHILD-DC1"
    roles:
      - name: ludus_create_child_domain
        depends_on:
          - { vm_name: "{{ range_id }}-PARENT-DC1", role: "ludus_verify_dc_ready" }
    role_vars:
      dns_domain_name: "child.parent.local"
      parent_dc_ip: *parent_dc_ip
      domain_admin_user: "{{ domain_admin_user }}@{{ parent_domain }}"
      domain_admin_password: *simple_password
      ad_domain_user: *domain_user_user
      ad_domain_user_password: *simple_password
      ad_domain_safe_mode_password: *complex_password
      domain_mode: *functional_level
```
