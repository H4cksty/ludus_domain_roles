# ludus_create_child_domain

Ansible role to create a new child domain and its first domain controller.

## Description
This role automates the creation of a new child domain within an existing Active Directory forest. It performs the following actions:
1.  Promotes the target server to a domain controller for the new child domain.
2.  Creates a `domainadmin` user with administrative privileges in the new child domain.
3.  Creates a standard `domainuser` in the new child domain.

## WARNING
This role requires explicit credentials to be passed via `role_vars`.

## Example

```yaml
# In your main ludus-config.yml

defaults:
  # These are still used by the user creation part of the role
  ad_domain_admin: domainadmin
  ad_domain_admin_password: "password"
  ad_domain_user: domainuser
  ad_domain_user_password: "password"

ludus:
  # ... parent DC is defined prior to this ...

  - vm_name: "{{ range_id }}-CHILD-DC1"
    hostname: "CHILD-DC1"
    template: win2019-server-x64-template
    vlan: 20
    ip_last_octet: 10
    roles:
      - name: ludus_create_child_domain
        depends_on:
          - vm_name: "{{ range_id }}-PARENT-DC1"
            role: "ludus_verify_dc_ready"
    role_vars:
      dns_domain_name: "child.parent.local"
      parent_ea_user: "PARENT\\domainadmin"
      parent_ea_password: "password" # Password for the parent domain admin
      safe_mode_password: "YourComplexPassword!" # Must meet complexity requirements
      parent_dc_ip: "10.2.10.10"
```
