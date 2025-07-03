# ✅ ludus_verify_dc_ready

A simple role that acts as a readiness probe for an Active Directory Domain Controller. It waits for the LDAP service to become available, ensuring a DC is fully operational before other roles attempt to interact with it.

---

## 🧠 Description

This role is a foundational building block for complex, multi-stage Active Directory deployments in Ludus. Its sole purpose is to pause Ansible execution until a target Domain Controller is confirmed to be online and its core services are running. It is most commonly used in the `depends_on` section of a `ludus-config.yml` file to prevent race conditions.

---

## ‼️ Requirements

Before using this role, ensure the following requirement is met:

1.  **Ansible Collection:** The `ansible.windows` collection must be installed on your Ludus server. You can install it with:
    ```bash
    ludus ansible collection add ansible.windows
    ```

---

## 📌 Example — `ludus-config.yml`

This example shows how `ludus_verify_dc_ready` is applied to a primary DC. Another VM (like a child DC) would then list this role in its `depends_on` block to ensure it waits for the primary DC to be ready.

```yaml
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
      # This role runs on the DC to mark it as a dependency target.
      # We can override the default timeout if needed.
      - name: ludus_verify_dc_ready
        vars:
          ldap_timeout: 400

  - vm_name: "{{ range_id }}-SOME-OTHER-VM"
    # ... other vm config
    roles:
      - name: some_other_role
        # This ensures 'some_other_role' does not run until
        # PARENT-DC1 has passed its LDAP readiness check.
        depends_on:
          - vm_name: "{{ range_id }}-PARENT-DC1"
            role: ludus_verify_dc_ready
```

---

## 🔧 Variables

This role has no **required** variables. All variables are optional and have default values.

### Optional

These variables have default values defined in `defaults/main.yml`.

| Variable       | Default | Description                                       |
| -------------- | ------- | ------------------------------------------------- |
| `ldap_port`    | `389`   | The TCP port to check for LDAP service availability. |
| `ldap_timeout` | `300`   | The maximum time in seconds to wait for the port. |
| `ldap_delay`   | `15`    | The delay in seconds before starting the check.   |

---

## ✅ Behavior

- Pauses Ansible execution on the target host.
- Repeatedly checks if the specified `ldap_port` is open.
- Continues the deployment once the port is available or fails if the `ldap_timeout` is reached.

---

## 📎 License

MIT © H4cksty
