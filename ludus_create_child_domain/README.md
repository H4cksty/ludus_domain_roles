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
  # Passwords
  complex_password: &complex_password "YourComplexPassword!1"
  simple_password: &simple_password "password"
  
  # Usernames
  domain_admin_user: &domain_admin_user "domainadmin"
  domain_user_user: &domain_user_user "domainuser"
  
  # Parent Domain Info
  parent_domain: &parent_domain "parent.local"
  parent_dc_ip: &parent_dc_ip "10.2.10.10"

  # Global Settings
  functional_level: &functional_level "Win2012R2"
  full_clone: &full_clone false

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
      ad_domain_admin: *domain_admin_user
      domain_admin_password: *simple_password
      ad_domain_user: *domain_user_user
      domain_user_password: *simple_password
      safe_mode_password: *complex_password
      domain_mode: *functional_level
```
