# ludus_secondary_child_dc

Ansible role to promote a Windows Server to be an *additional* (secondary) domain controller in an *existing* child domain.

## Description
This role is designed to be used after a primary child domain controller has already been created. It adds a second, redundant DC to that child domain.

This role is optimized to inherit credentials (`ad_domain_admin`, `ad_domain_admin_password`, `ad_domain_safe_mode_password`) directly from the `defaults` block of your main `ludus-config.yml`, which simplifies configuration and reduces errors.

## WARNING
This role requires Enterprise Admin credentials from the **parent domain** to authorize the promotion. Ensure the `ad_domain_admin` user in your `defaults` block is a member of the "Enterprise Admins" group in the parent domain. (ludus does this by default with its built-in "primary-dc" role.)

## Example

```yaml
# In your main ludus-config.yml

defaults:
  # ... other defaults
  ad_domain_admin: "domainadmin" 
  ad_domain_admin_password: "password"
  ad_domain_safe_mode_password: "YourComplexPassword!"
  # ...

ludus:
  # ... parent and primary child DCs are defined here ...

  - vm_name: "{{ range_id }}-CHILD-DC2"
    hostname: "CHILD-DC2"
    template: win2022-server-x64-template
    vlan: 30
    ip_last_octet: 11
    windows:
      sysprep: true
    roles:
      - name: ludus_secondary_child_dc
        depends_on:
          - vm_name: "{{ range_id }}-CHILD-DC1"
            role: "ludus_create_child_domain"
    role_vars:
      # NOTE: The role_vars block is now much simpler.
      dns_domain_name: "child.parent.local"
      parent_domain_netbios_name: "ERSHON" # The NETBIOS name of the PARENT domain
      existing_dc_ip: "10.2.30.10" # IP of the PRIMARY child DC
      # The role will inherit credentials from the 'defaults' block automatically.
```
