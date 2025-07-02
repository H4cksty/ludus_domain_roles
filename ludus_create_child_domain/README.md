# ludus_create_child_domain

Ansible role to create a new child domain and its first domain controller.

## Description
This role automates the creation of a new child domain within an existing Active Directory forest. It performs the following actions:
1.  Promotes the target server to a domain controller for the new child domain.
2.  Creates a `domainadmin` user with administrative privileges in the new child domain.
3.  Creates a standard `domainuser` in the new child domain.

This role is designed to integrate seamlessly with the `defaults` block of your `ludus-config.yml`. It will use the values for `ad_domain_admin`, `ad_domain_admin_password`, etc., that you have defined globally for your range.

## WARNING
This role uses the parent domain's Enterprise Admin credentials for the initial authorization. Ensure the `ad_domain_admin` user in your `defaults` block is a member of the "Enterprise Admins" group in the parent domain.

## Example

```yaml
# In your main ludus-config.yml

defaults:
  # ... other defaults
  ad_domain_admin: domainadmin
  ad_domain_admin_password: "password"
  ad_domain_user: domainuser
  ad_domain_user_password: "password"
  ad_domain_safe_mode_password: "YourComplexPassword!"

ludus:
  # ... parent DC for ershon.local is defined here ...

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
      parent_domain_netbios_name: "PARENT"
      parent_dc_ip: "10.2.10.10"
```
