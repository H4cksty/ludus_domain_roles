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
  complex_password: &complex_password "YourComplexPassword!"
  simple_password: &simple_password "password"
  domain_admin_user: &domain_admin_user "domainadmin"
  parent_netbios: &parent_netbios "PARENT"

ludus:
  - vm_name: "{{ range_id }}-CHILD2-DC2"
    roles:
      - name: ludus_secondary_child_dc
        depends_on:
          - { vm_name: "{{ range_id }}-CHILD2-DC1", role: "ludus_create_child_domain" }
    role_vars:
      dns_domain_name: "child2.parent.local"
      parent_domain_netbios_name: *parent_netbios
      existing_dc_ip: "10.2.30.10"
      ad_domain_admin: *domain_admin_user
      ad_domain_admin_password: *simple_password
      ad_domain_safe_mode_password: *complex_password
```
