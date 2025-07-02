# ludus_secondary_child_dc

Ansible role to promote a Windows Server to be an *additional* (secondary) domain controller in an *existing* child domain.

## Description
This role is designed to be used after a primary child domain controller has already been created by the `ludus_create_child_domain` role. It will add a second, redundant DC to that child domain.

This role is optimized to inherit credentials (`ad_domain_admin`, `ad_domain_admin_password`, `ad_domain_safe_mode_password`) directly from the `defaults` block of your main `ludus-config.yml`, which simplifies configuration and reduces errors.

## WARNING
This role requires Enterprise Admin credentials from the **parent domain** to authorize the promotion. Ensure the `ad_domain_admin` user in your `defaults` block is a member of the "Enterprise Admins" group in the parent domain.

## Example

```yaml
# In your main ludus-config.yml

defaults:
  # ... other defaults
  ad_domain_admin: domainadmin
  ad_domain_admin_password: "password"
  ad_domain_safe_mode_password: "YourComplexPassword!"
  # ...

ludus:
  # ... parent and primary child DCs are defined here ...

  - vm_name: "{{ range_id }}-CHILD2-DC2"
    hostname: "CHILD2-DC2"
    template: win2022-server-x64-template
    vlan: 30
    ip_last_octet: 11
    windows:
      sysprep: true
    roles:
      - name: ludus_secondary_child_dc
        depends_on:
          - vm_name: "{{ range_id }}-CHILD2-DC1"
            role: "ludus_create_child_domain"
    role_vars:
      dns_domain_name: "child2.parent.local"
      parent_domain_netbios_name: "PARENT" # The NETBIOS name of the PARENT domain
      existing_dc_ip: "10.2.30.10" # IP of the PRIMARY child DC
      # Credentials are inherited from defaults.
```
