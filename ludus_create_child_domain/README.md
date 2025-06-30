# ludus_create_child_domain

## Ansible role to create a new child domain and its first domain controller.

## Description
This role automates the creation of a new child domain within an existing Active Directory forest. It performs the following actions:
1.  Promotes the target server to a domain controller for the new child domain.
2.  Creates a `domainadmin` user with administrative privileges.
3.  Creates a standard `domainuser`.

This role is designed to integrate seamlessly with the `defaults` block of your `ludus-config.yml`. It will use the values for `ad_domain_admin`, `ad_domain_admin_password`, etc., that you have defined globally for your range.

## WARNING
This role uses the parent domain's Enterprise Admin credentials for the initial authorization. However, the `domainadmin` and `domainuser` accounts are created in the **new child domain**.

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
  # ... parent DC for parent.local is defined here ...

  - vm_name: "{{ range_id }}-CHILD-DC1"
    hostname: "CHILD-DC1"
    template: win2019-server-x64-template
    vlan: 20
    ip_last_octet: 10
    ram_gb: 8
    cpus: 4
    windows:
      sysprep: true
    roles:
      - name: ludus_create_child_domain
        depends_on:
          - vm_name: "{{ range_id }}-CHILD-DC1"
            role: "ludus-ad-content"          # This could be any arbitrary role assigned to your Primary Parent DC, it just needs _something_ to depend on.
    role_vars:
      # Variables for the role to create the domain
      dns_domain_name: "child.parent.local"
      parent_ea_user: "parent\\domainadmin" # Enterprise Admin from PARENT domain
      parent_ea_password: "password"
      parent_dc_ip: "10.2.10.10"
      current_host_ip: "10.2.20.10"
      # The role will now use the variables from the 'defaults' block above
      # to create the domainadmin and domainuser accounts automatically.
```
