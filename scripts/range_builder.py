#!/usr/bin/env python3
"""
range_builder.py

Interactive Ludus Range Builder with:
- Clone type (linked/full)
- Shared vs per-VM admin creds
- Optional GPO to disable Windows Defender
- Default attacker VLAN-99 VMs
- Dynamic template selection menu
- Interactive VLAN, IP, CPU, RAM prompts
- Dual YAML: open + segmented
- Final menu: save, set config, deploy & watch, or discard.
"""

import os
import sys
import argparse
import subprocess
import getpass
from jinja2 import Template

# --------------------------------------------------------------------------
# Templates
# --------------------------------------------------------------------------

OPEN_TEMPLATE = """
clone_type: "{{ clone_type }}"
disable_windows_defender_gpo: {{ disable_defender | lower }}

global_role_vars:
{% for k, v in global_role_vars.items() %}
  {{ k }}: "{{ v }}"
{% endfor %}

vms:
{% for vm in vms %}
  - vm_name: "{{ vm.vm_name }}"
    hostname: "{{ vm.hostname }}"
    template: "{{ vm.template }}"
    vlan: {{ vm.vlan }}
    ip_last_octet: {{ vm.ip_last_octet }}
    cpus: {{ vm.cpus }}
    ram: {{ vm.ram }}
{%   if vm.domain %}
    domain:
      fqdn: "{{ vm.domain.fqdn }}"
      role: "{{ vm.domain.role }}"
{%   endif %}
    roles:
{%   if vm.roles|length == 0 %}
      [] 
{%   else %}
{%     for role in vm.roles %}
      - name: {{ role.name }}
{%       if role.depends_on %}
        depends_on:
{%         for d in role.depends_on %}
          - vm_name: "{{ d.vm_name }}"
            role: {{ d.role }}
{%         endfor %}
{%       endif %}
{%       if role.vars %}
        vars:
{%         for key, val in role.vars.items() %}
          {{ key }}: "{{ val }}"
{%         endfor %}
{%       endif %}
{%     endfor %}
{%   endif %}
{% endfor %}
"""

SEGMENTED_TEMPLATE = """
# Segmented networking policies
network_policies:
  default_isolate_vlans: true
  allow:
    - src: non-DC
      dst: redirector
      ports: [80,443,53,8080,8443]
    - src: attacker
      dst: teamserver
      ports: [50050]
    - src: domain
      dst: domain
      trust: true

# VM definitions (same as open)
{{ open_yaml }}
"""

# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------

def run_cmd(cmd):
    """Run a shell command and return output stripped, or None if fails."""
    try:
        out = subprocess.check_output(cmd, shell=True, text=True)
        return [l.strip() for l in out.splitlines() if l.strip()]
    except subprocess.CalledProcessError:
        return []

def pick_from_list(prompt, items, default_idx=0):
    """Show numbered list, prompt user to pick an index."""
    for i, item in enumerate(items):
        print(f"  [{i+1}] {item}")
    while True:
        resp = input(f"{prompt} [default {default_idx+1}]: ").strip()
        if not resp:
            return items[default_idx]
        try:
            idx = int(resp) - 1
            if 0 <= idx < len(items):
                return items[idx]
        except ValueError:
            pass
        print(f"→ enter a number 1–{len(items)}")

def ask(prompt, default=None, cast=str):
    hint = f" [{default}]" if default is not None else ""
    resp = input(f"{prompt}{hint}: ").strip()
    return default if resp == "" else cast(resp)

def ask_yesno(prompt, default=True):
    yn = "Y/n" if default else "y/N"
    resp = input(f"{prompt} [{yn}]: ").strip().lower()
    return default if not resp else (resp in ("y","yes"))

def ask_int(prompt, default, min_val=None, max_val=None):
    while True:
        resp = input(f"{prompt} [{default}]: ").strip()
        val = default if resp == "" else None
        if resp:
            try:
                val = int(resp)
            except ValueError:
                print("→ enter an integer")
                continue
        if (min_val is not None and val < min_val) or (max_val is not None and val > max_val):
            print(f"→ must be between {min_val} and {max_val}")
            continue
        return val

def ask_global_creds():
    print("\nEnter GLOBAL domain admin credentials:")
    admin = ask("  Admin UPN", default="Administrator@parent.local")
    pwd   = getpass.getpass("  Admin password: ")
    dsrcm = getpass.getpass("  Safe-Mode (DSRM) password: ")
    userp = getpass.getpass("  Domain user password: ")
    return {
        "ad_domain_admin": admin,
        "ad_domain_admin_password": pwd,
        "ad_domain_safe_mode_password": dsrcm,
        "ad_domain_user_password": userp
    }

def ask_vm_resources(vm_name):
    print(f"\nResources for {vm_name}:")
    cpus = ask_int("  CPUs", default=2, min_val=1)
    ram  = ask_int("  RAM (GB)", default=2, min_val=1)
    return cpus, ram

def select_template():
    print("\nFetching available templates…")
    templates = run_cmd("ludus templates list | grep TRUE | awk '{print $2}'")
    if not templates:
        print("⚠ Unable to fetch templates—fallback to manual entry.")
        return ask("Template name", default="win2019-server-x64-template")
    return pick_from_list("Select template", templates)

# --------------------------------------------------------------------------
# VM Class
# --------------------------------------------------------------------------

class VM:
    def __init__(self, vm_name, hostname, template, vlan, ip_last_octet,
                 cpus, ram, domain=None, roles=None):
        self.vm_name = vm_name
        self.hostname = hostname
        self.template = template
        self.vlan = vlan
        self.ip_last_octet = ip_last_octet
        self.cpus = cpus
        self.ram = ram
        self.domain = domain
        self.roles = roles or []

# --------------------------------------------------------------------------
# Builders
# --------------------------------------------------------------------------

def build_default_attackers(range_id):
    vlan = 99
    vms = []
    # Kali
    tpl = select_template()
    cpus, ram = ask_vm_resources("KALI-ATTACK")
    vms.append(VM("KALI-ATTACK","KALI-ATTACK",tpl,vlan,10,cpus,ram))
    # Win-Attack
    tpl = select_template()
    cpus, ram = ask_vm_resources("WIN-ATTACK")
    vms.append(VM("WIN-ATTACK","WIN-ATTACK",tpl,vlan,20,cpus,ram))
    # TeamServers
    for i in range(1, ask_int("How many TeamServers?", 1, 1, 2)+1):
        tpl = select_template()
        cpus, ram = ask_vm_resources(f"TEAMSERVER{i}")
        vms.append(VM(f"TEAMSERVER{i}",f"TEAMSERVER{i}",tpl,vlan,100*i,cpus,ram))
    # Redirectors
    domains  = ["jonesphotography.com","militarydiscounts.com"]
    for i in range(1, ask_int("How many Redirectors?", 1, 1, 2)+1):
        tpl = select_template()
        cpus, ram = ask_vm_resources(f"REDIRECTOR{i}")
        vms.append(VM(f"REDIRECTOR{i}",f"REDIRECTOR{i}",tpl,vlan,10+i,cpus,ram,
                      domain={"fqdn": domains[i-1], "role": "redirector"}))
    return vms

def add_custom_vms(vms, use_global_creds):
    while ask_yesno("Add a custom VM?", default=False):
        name  = ask("VM name", default=f"VM{len(vms)+1}")
        host  = ask("Hostname", default=name)
        tpl   = select_template()
        vlan  = ask_int("VLAN", default=10, min_val=1)
        ip    = ask_int("IP last octet", default=10, min_val=1, max_val=254)
        cpus, ram = ask_vm_resources(name)
        domain = None
        if ask_yesno("  Domain-joined?", default=False):
            fqdn = ask("    Domain FQDN", default="child.example.local")
            role= ask("    Domain role", default="member")
            domain={"fqdn": fqdn, "role": role}
        vm = VM(name, host, tpl, vlan, ip, cpus, ram, domain)

        # Roles
        vm.roles = []
        for r in range(ask_int("  How many Ludus roles?", 1, 0)):
            rname = ask(f"    Role {r+1} name", default="")
            role  = {"name": rname, "depends_on": [], "vars": {}}
            if ask_yesno("      Add depends_on?", default=False):
                for _ in range(ask_int("        count",1,1)):
                    dvn = ask("          Dep VM name", default="")
                    drn = ask("          Dep role name", default="")
                    role["depends_on"].append({"vm_name": dvn, "role": drn})
            if ask_yesno("      Add vars?", default=False):
                for _ in range(ask_int("        count",1,1)):
                    k = ask("          Var name", default="")
                    v = ask("          Var value", default="")
                    role["vars"][k] = v
            vm
