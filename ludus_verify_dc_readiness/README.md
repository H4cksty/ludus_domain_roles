# ludus_verify_dc_ready

A minimal Ansible role whose only purpose is to verify that a Domain Controller is online and its Active Directory services are responsive.

## Description
This role performs a single check: it waits for up to 5 minutes for the standard AD LDAP port (389) to become available on the host it is running on.

Its primary use is to serve as a reliable dependency target (`depends_on`) for other roles. By applying this role to your primary parent DC, you can make your child domain creation roles wait until the parent is truly ready, preventing race conditions.

This role requires no `role_vars`.

## Example

```yaml
# In your main ludus-config.yml

ludus:
  - vm_name: "{{ range_id }}-PARENT-DC1"
    hostname: "PARENT-DC1"
    template: win2019-server-x64-template
    vlan: 10
    ip_last_octet: 10
    domain:
      fqdn: "parent.local"
      role: "primary-dc"
    roles:
      # This role runs after the DC is promoted and serves as the "ready" signal.
      - ludus_verify_dc_ready

  - vm_name: "{{ range_id }}-CHILD-DC1"
    hostname: "CHILD-DC1"
    template: win2019-server-x64-template
    vlan: 20
    ip_last_octet: 10
    roles:
      - name: ludus_create_child_domain
        depends_on:
          # This now waits for the verification role to complete.
          - vm_name: "{{ range_id }}-PARENT-DC1"
            role: "ludus_verify_dc_ready"
    role_vars:
      # ... role vars for creating the child domain
```
