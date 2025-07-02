# ludus_secondary_child_dc

Ansible role to promote a Windows Server to be an *additional* (secondary) domain controller in an *existing* child domain.

## Description
This role is designed to be used after a primary child domain controller has already been created. It adds a second, redundant DC to that child domain.

## IMPORTANT
This role requires all variables to be passed explicitly via `role_vars`. It is designed to be used with a `global_role_vars` block and YAML anchors in your main `ludus-config.yml`. The user account provided requires Enterprise Admin rights in the parent domain.

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
  - vm_name: "{{ range_id }}-CHILD2-DC2"
    roles:
      - name: ludus_secondary_child_dc
        depends_on:
          - { vm_name: "{{ range_id }}-CHILD2-DC1", role: "ludus_create_child_domain" }
    role_vars:
      existing_dc_ip: "10.2.30.10"
      dns_domain_name: "child2.parent.local"
      domain_admin_user: "{{ domain_admin_user }}@{{ dns_domain_name }}"
      domain_admin_password: *simple_password
      safe_mode_password: *complex_password
```
