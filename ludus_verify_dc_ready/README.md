# ✅ ludus_verify_dc_ready

A minimalist Ansible role that ensures a Domain Controller (DC) is fully online and its LDAP services are responsive. This role is purpose-built for use within [Ludus](https://github.com/H4cksty/ludus) scenarios as a dependency guard.

---

## 🔍 Purpose

This role probes port **389 (LDAP)** on the target machine and waits until it becomes available. It serves as a "green light" signal—ensuring that the DC has completed promotion and Active Directory services are operational before other roles begin.

It’s ideal as a `depends_on` prerequisite for:

- `ludus_create_child_domain`
- `ludus_join_domain`
- Any GPO or replication-sensitive roles

---

## 🛠️ What It Does

- ✅ Waits up to a defined timeout (`ldap_timeout`)
- ✅ Checks availability of port `389` on the machine's default IPv4 address
- ✅ Logs the wait result for traceability
- ✅ Requires **no credentials** or external systems

---

## 🔧 Role Variables

All variables are optional (defaults shown):

| Variable       | Type    | Description                              | Default |
|----------------|---------|------------------------------------------|---------|
| `ldap_port`    | Integer | Port to probe (typically 389 for LDAP)   | `389`   |
| `ldap_timeout` | Integer | Max time to wait (in seconds)            | `300`   |
| `ldap_delay`   | Integer | Delay before first check (in seconds)    | `10`    |

To override any of these, pass them in the `vars:` block of your `ludus_config.yml`.

---

## 📘 Example — Ludus Deployment Snippet

```yaml
- vm_name: "{{ range_id }}-PARENT-DC1"
  hostname: "PARENT-DC1"
  template: win2019-server-x64-template
  vlan: 10
  ip_last_octet: 10
  domain:
    fqdn: "parent.local"
    role: "primary-dc"
  roles:
    - name: ludus_verify_dc_ready
      vars:
        ldap_timeout: 240  # Wait up to 4 minutes
```
# Then Downstream....
```yaml
- vm_name: "{{ range_id }}-CHILD-DC1"
  roles:
    - name: ludus_create_child_domain
      depends_on:
        - vm_name: "{{ range_id }}-PARENT-DC1"
          role: ludus_verify_dc_ready
```

# 🧪 Testing & Behavior
This role uses:
 - ansible.windows.win_wait_for
 - No domain joins, no reboots, no shell calls
 - Fast return once port 389 is ready
 - Compatible with check mode, dry runs, and all Ludus orchestration features

---

# 📎 License
 - MIT © H4cksty

---

## 💡 Pro Tip

Use this role liberally. It acts as a superlight safety harness between any roles that rely on a DC being online—especially in race-prone environments like nested domain joins, replication trusts, or FSMO ops.
