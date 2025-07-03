#!/usr/bin/env python3
"""
range_builder.py

Interactive Ludus Range Builder:
- Default attacker VLAN (99) with Kali, Windows attack, TeamServers, Redirectors
- Dual YAML generation: open + segmented
- Final menu: save, load into Ludus, deploy & watch, or discard.
"""

import os
import sys
import argparse
import subprocess
import yaml
from jinja2 import Template

# --------------------------------------------------------------------------
# Templates
# --------------------------------------------------------------------------

OPEN_TEMPLATE = """
global_role_vars:
  # (add your own global creds/anchors here…)

vms:
{% for vm in vms %}
  - vm_name: "{{ vm.vm_name }}"
    hostname: "{{ vm.hostname }}"
    template: "{{ vm.template }}"
    vlan: {{ vm.vlan }}
    ip_last_octet: {{ vm.ip_last_octet }}
{%   if vm.domain %}
    domain:
      fqdn: "{{ vm.domain.fqdn }}"
      role: "{{ vm.domain.role }}"
{%   endif %}
    roles:
{%   for role in vm.roles %}
      - name: {{ role.name }}
{%     if role.depends_on %}
        depends_on:
{%       for d in role.depends_on %}
          - vm_name: "{{ d.vm_name }}"
            role: {{ d.role }}
{%       endfor %}
{%     endif %}
        {% if role.vars %}vars:{% for k,v in role.vars.items() %}
          {{ k }}: {{ v }}{% endfor %}{% endif %}
{%   endfor %}
{% endfor %}
"""

SEGMENTED_TEMPLATE = """
# Segmented networking policies
network_policies:
  default_isolate_vlans: true
  allow:
    # All non-DCs → redirectors on specific ports
    - src: non-DC
      dst: redirector
      ports: [80,443,53,8080,8443]
    # Attack hosts → teamservers on port 50050
    - src: attacker
      dst: teamserver
      ports: [50050]
    # Domains only talk to each other if explicit trust
    - src: domain
      dst: domain
      trust: true

# VM definitions (same as open)
{{ open_yaml }}
"""

# --------------------------------------------------------------------------
# Data structures
# --------------------------------------------------------------------------

class VM:
    def __init__(self, vm_name, hostname, template, vlan, ip_last_octet,
                 domain=None, roles=None):
        self.vm_name = vm_name
        self.hostname = hostname
        self.template = template
        self.vlan = vlan
        self.ip_last_octet = ip_last_octet
        self.domain = domain  # dict with fqdn, role
        self.roles = roles or []  # list of dicts

# --------------------------------------------------------------------------
# Builders
# --------------------------------------------------------------------------

def ask_yesno(prompt, default=True):
    yes = 'Y/n' if default else 'y/N'
    resp = input(f"{prompt} [{yes}]: ").strip().lower()
    if not resp:
        return default
    return resp in ('y','yes')

def prompt_int(prompt, default=None, choices=None):
    while True:
        resp = input(f"{prompt}{' ['+str(default)+']' if default else ''}: ").strip()
        if not resp and default is not None:
            return default
        try:
            val = int(resp)
            if choices and val not in choices:
                print(f"– must be one of {choices}")
                continue
            return val
        except ValueError:
            print("– please enter an integer")

def build_default_attackers(range_id):
    """
    Returns a list of attacker VM objects for VLAN 99.
    """
    vlan = 99
    vms = []
    # Kali
    vms.append(VM(
        vm_name=f"KALI-ATTACK",
        hostname="KALI-ATTACK",
        template="kali-x64-meta-template",
        vlan=vlan,
        ip_last_octet=int(f"{range_id}99") * 1 + 10,  # 10
    ))
    # Windows attack
    vms.append(VM(
        vm_name="WIN-ATTACK",
        hostname="WIN-ATTACK",
        template="win10-22h2-x64-enterprise-template",
        vlan=vlan,
        ip_last_octet=20,
    ))
    # Teamservers
    count_ts = prompt_int("Number of TeamServer VMs to include", default=1, choices=[1,2])
    for i in range(1, count_ts+1):
        vms.append(VM(
            vm_name=f"TEAMSERVER{i}",
            hostname=f"TEAMSERVER{i}",
            template="ubuntu-22.04-x64-server-template",
            vlan=vlan,
            ip_last_octet=100 * i,
        ))
    # Redirectors
    count_rd = prompt_int("Number of Redirector VMs to include", default=1, choices=[1,2])
    domains = ["jonesphotography.com", "militarydiscounts.com"]
    for i in range(1, count_rd+1):
        vms.append(VM(
            vm_name=f"REDIRECTOR{i}",
            hostname=f"REDIRECTOR{i}",
            template="ubuntu-22.04-x64-server-template",
            vlan=vlan,
            ip_last_octet=10 + i,
            roles=[],
            domain={"fqdn": domains[i-1], "role": "redirector"}
        ))
    return vms

def render_open_yaml(vms):
    tpl = Template(OPEN_TEMPLATE)
    return tpl.render(vms=vms)

def render_segmented_yaml(open_yaml):
    tpl = Template(SEGMENTED_TEMPLATE)
    return tpl.render(open_yaml=open_yaml)

# --------------------------------------------------------------------------
# I/O & Menus
# --------------------------------------------------------------------------

def write_file(path, content):
    with open(path, 'w') as f:
        f.write(content)
    print(f"✔ Wrote: {path}")

def final_menu(out_base):
    print("\nRange YAML Generated:")
    print(f" 1) {out_base}_build.yml   (open networking)")
    print(f" 2) {out_base}_segmented.yml (segmented networking)\n")
    print("What would you like to do next?")
    print("[1] Save YAML and exit (default)")
    print("[2] Save + load into Ludus")
    print("[3] Save + load + deploy + watch")
    print("[4] Discard and exit")
    choice = input("Choose [1-4]: ").strip() or "1"
    return choice

def ludus_cmd(cmd):
    print(f"→ running: {cmd}")
    r = subprocess.run(cmd, shell=True)
    if r.returncode != 0:
        print(f"⚠ Command failed: {cmd}")
        sys.exit(r.returncode)

# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--range-id", type=int, help="Numeric Range ID", required=True)
    parser.add_argument("--out", default="range", help="Output base filename")
    args = parser.parse_args()

    range_id = args.range_id
    vms = []

    if ask_yesno("Include default attacker VLAN 99 setup?"):
        vms.extend(build_default_attackers(range_id))

    # TODO: interactive addition of domain VMs (primary DC, child DC, etc.)
    print("\nNOTE: Domain VMs can be added manually to the output YAML.\n")

    # Render YAML
    open_yaml = render_open_yaml(vms)
    segmented_yaml = render_segmented_yaml(open_yaml)

    # Menu
    choice = final_menu(args.out)
    if choice == "4":
        print("Discarding and exiting.")
        sys.exit(0)

    # Write files
    write_file(f"{args.out}_build.yml", open_yaml)
    write_file(f"{args.out}_segmented.yml", segmented_yaml)

    if choice in ("2","3"):
        ludus_cmd(f"ludus range load {args.out}_build.yml")
    if choice == "3":
        ludus_cmd("ludus range deploy")
        ludus_cmd('watch -c "ludus range list"')

    print("Done.")

if __name__ == "__main__":
    main()
