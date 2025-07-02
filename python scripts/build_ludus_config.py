#!/usr/bin/python3

import yaml         # requires python pip3 install pyyaml (likely already installed)
import sys

# --- Helper Functions for User Input ---

def print_header(title):
    """Prints a styled header to the console."""
    print("\n" + "="*60)
    print(f" {title.upper()} ".center(60, "="))
    print("="*60)

def get_input(prompt, default=None):
    """Gets user input with an optional default value."""
    if default is not None:
        prompt_text = f"{prompt} [{default}]: "
    else:
        prompt_text = f"{prompt}: "
    
    user_input = input(prompt_text).strip()
    return user_input if user_input else default

def get_int_input(prompt, default=None):
    """Gets integer input from the user, with validation."""
    while True:
        try:
            value = get_input(prompt, default)
            if value is None:
                print("This field is required.", file=sys.stderr)
                continue
            return int(value)
        except ValueError:
            print("Invalid input. Please enter a number.", file=sys.stderr)

def get_yes_no(prompt, default='n'):
    """Gets a yes/no answer from the user."""
    while True:
        answer = get_input(prompt + " (y/n)", default).lower()
        if answer in ['y', 'yes']:
            return True
        if answer in ['n', 'no']:
            return False
        print("Invalid input. Please enter 'y' or 'n'.", file=sys.stderr)

# --- Core Logic Functions ---

def get_default_settings():
    """Gathers the global default settings for the range."""
    print_header("Global Default Settings")
    defaults = {}
    defaults['ad_domain_admin'] = get_input("Default Domain Admin Username", "domainadmin")
    defaults['ad_domain_admin_password'] = get_input("Default Domain Admin Password", "password")
    defaults['ad_domain_user'] = get_input("Default Domain User Username", "domainuser")
    defaults['ad_domain_user_password'] = get_input("Default Domain User Password", "password")
    print("\nIMPORTANT: The Safe Mode password MUST meet complexity requirements for secondary DCs.")
    defaults['ad_domain_safe_mode_password'] = get_input("Default Safe Mode Admin Password", "YourComplexPassword!1")
    defaults['timezone'] = get_input("Timezone", "America/Chicago")
    defaults['ad_domain_functional_level'] = "Win2012R2"
    defaults['ad_forest_functional_level'] = "Win2012R2"
    defaults['snapshot_with_RAM'] = True
    defaults['stale_hours'] = 0
    defaults['enable_dynamic_wallpaper'] = True
    return defaults

def define_parent_domain(range_id):
    """Gathers details for the parent domain and its machines."""
    print_header("Parent Domain Configuration")
    vms = []
    
    fqdn = get_input("Parent Domain FQDN (e.g., ershon.local)", "ershon.local")
    netbios = get_input("Parent Domain NETBIOS Name (e.g., ERSHON)", "ERSHON")
    vlan = get_int_input("Parent Domain VLAN", 10)
    
    # Primary DC
    print("\n--- Parent Primary DC ---")
    pdc_hostname = get_input("Primary DC Hostname", f"{netbios}-DC1")
    pdc_ip_octet = get_int_input("Primary DC IP Last Octet", 10)
    pdc_vm = {
        'vm_name': f"{{{{ range_id }}}}-{pdc_hostname}",
        'hostname': pdc_hostname,
        'template': get_input("Template", "win2019-server-x64-template"),
        'vlan': vlan,
        'ip_last_octet': pdc_ip_octet,
        'ram_gb': get_int_input("RAM (GB)", 4),
        'cpus': get_int_input("CPUs", 4),
        'domain': {'fqdn': fqdn, 'role': 'primary-dc'},
        'windows': {'sysprep': True, 'gpos': ['disable_defender']},
        'roles': ['ludus_verify_dc_ready']
    }
    vms.append(pdc_vm)

    # Optional Secondary DC
    if get_yes_no("Add a secondary DC to the parent domain?"):
        print("\n--- Parent Secondary DC ---")
        sdc_hostname = get_input("Secondary DC Hostname", f"{netbios}-DC2")
        sdc_ip_octet = get_int_input("Secondary DC IP Last Octet", 11)
        sdc_vm = {
            'vm_name': f"{{{{ range_id }}}}-{sdc_hostname}",
            'hostname': sdc_hostname,
            'template': get_input("Template", "win2019-server-x64-template"),
            'vlan': vlan,
            'ip_last_octet': sdc_ip_octet,
            'ram_gb': get_int_input("RAM (GB)", 4),
            'cpus': get_int_input("CPUs", 2),
            'windows': {'sysprep': True},
            'domain': {'fqdn': fqdn, 'role': 'alt-dc'}
        }
        vms.append(sdc_vm)

    return vms, fqdn, netbios, vlan, pdc_ip_octet

def define_child_domain(range_id, parent_fqdn, parent_netbios, parent_dc_ip):
    """Gathers details for a single child domain and its machines."""
    vms = []
    
    print("\n--- New Child Domain ---")
    child_name = get_input("Child Domain Name (e.g., springfield)")
    if not child_name:
        return []
        
    child_fqdn = f"{child_name.lower()}.{parent_fqdn}"
    child_netbios = get_input("Child Domain NETBIOS Name", child_name.upper())
    child_vlan = get_int_input(f"VLAN for {child_fqdn}", 20)

    # Child Primary DC
    print(f"\n--- {child_netbios} Primary DC ---")
    pdc_hostname = get_input("Primary DC Hostname", f"{child_netbios.upper()}-DC1")
    pdc_ip_octet = get_int_input("Primary DC IP Last Octet", 10)
    
    pdc_vm = {
        'vm_name': f"{{{{ range_id }}}}-{pdc_hostname}",
        'hostname': pdc_hostname,
        'template': get_input("Template", "win2019-server-x64-template"),
        'vlan': child_vlan,
        'ip_last_octet': pdc_ip_octet,
        'ram_gb': get_int_input("RAM (GB)", 4),
        'cpus': get_int_input("CPUs", 4),
        'windows': {'sysprep': True},
        'roles': [{
            'name': 'ludus_create_child_domain',
            'depends_on': [{'vm_name': f"{{{{ range_id }}}}-{parent_netbios}-DC1", 'role': 'ludus_verify_dc_ready'}]
        }],
        'role_vars': {
            'dns_domain_name': child_fqdn,
            'parent_domain_netbios_name': parent_netbios,
            'parent_dc_ip': f"10.2.{parent_dc_ip['vlan']}.{parent_dc_ip['octet']}"
        }
    }
    vms.append(pdc_vm)

    # Optional Secondary DC
    if get_yes_no(f"Add a secondary DC to the {child_netbios} domain?"):
        print(f"\n--- {child_netbios} Secondary DC ---")
        sdc_hostname = get_input("Secondary DC Hostname", f"{child_netbios.upper()}-DC2")
        sdc_ip_octet = get_int_input("Secondary DC IP Last Octet", 11)
        sdc_vm = {
            'vm_name': f"{{{{ range_id }}}}-{sdc_hostname}",
            'hostname': sdc_hostname,
            'template': get_input("Template", "win2022-server-x64-template"),
            'vlan': child_vlan,
            'ip_last_octet': sdc_ip_octet,
            'ram_gb': get_int_input("RAM (GB)", 4),
            'cpus': get_int_input("CPUs", 2),
            'windows': {'sysprep': True},
            'roles': [{
                'name': 'ludus_secondary_child_dc',
                'depends_on': [{'vm_name': pdc_vm['vm_name'], 'role': 'ludus_create_child_domain'}]
            }],
            'role_vars': {
                'dns_domain_name': child_fqdn,
                'parent_domain_netbios_name': parent_netbios,
                'existing_dc_ip': f"10.2.{child_vlan}.{pdc_ip_octet}"
            }
        }
        vms.append(sdc_vm)

    # Child Members
    num_members = get_int_input(f"How many member workstations/servers for {child_netbios}?", 0)
    for i in range(num_members):
        print(f"\n--- {child_netbios} Member #{i+1} ---")
        mem_hostname = get_input("Member Hostname", f"{child_netbios}-WKS{i+1}")
        mem_ip_octet = get_int_input("Member IP Last Octet", 100 + i)
        is_server = get_yes_no("Is this a server (vs. a workstation)?")
        
        mem_vm = {
            'vm_name': f"{{{{ range_id }}}}-{mem_hostname}",
            'hostname': mem_hostname,
            'template': "win2022-server-x64-template" if is_server else "win10-22h2-x64-enterprise-template",
            'vlan': child_vlan,
            'ip_last_octet': mem_ip_octet,
            'ram_gb': get_int_input("RAM (GB)", 4),
            'cpus': get_int_input("CPUs", 2),
            'windows': {'sysprep': True},
            'roles': [{
                'name': 'ludus_join_child_domain',
                'depends_on': [{'vm_name': pdc_vm['vm_name'], 'role': 'ludus_create_child_domain'}]
            }],
            'role_vars': {
                'dc_ip': f"10.2.{child_vlan}.{pdc_ip_octet}",
                'dns_domain_name': child_fqdn,
                'child_domain_netbios_name': child_netbios
            }
        }
        vms.append(mem_vm)
        
    return vms

# --- Main Execution ---

def main():
    """Main function to drive the configuration script."""
    print("Welcome to the Ludus Forest Build Roles Config Generator!")
    print("This script will guide you through creating a ludus-config.yml file.")
    
    range_id = get_input("Enter your Ludus Range ID (e.g., MH)", "MH")
    
    config = {
        'defaults': get_default_settings(),
        'network': {
            'inter_vlan_default': 'ACCEPT',
            'external_default': 'ACCEPT'
        },
        'ludus': []
    }

    parent_vms, parent_fqdn, parent_netbios, parent_vlan, parent_octet = define_parent_domain(range_id)
    config['ludus'].extend(parent_vms)
    
    parent_dc_ip_info = {'vlan': parent_vlan, 'octet': parent_octet}

    while get_yes_no("Add a child domain?"):
        child_vms = define_child_domain(range_id, parent_fqdn, parent_netbios, parent_dc_ip_info)
        config['ludus'].extend(child_vms)

    # Save the configuration to a YAML file
    output_filename = "generated-config.yml"
    with open(output_filename, 'w') as f:
        # Use a custom representer to handle the templated strings correctly
        def str_presenter(dumper, data):
            if '{{' in data:
                return dumper.represent_scalar('tag:yaml.org,2002:str', data, style="'")
            return dumper.represent_scalar('tag:yaml.org,2002:str', data)
        
        yaml.add_representer(str, str_presenter)
        yaml.dump(config, f, default_flow_style=False, sort_keys=False, indent=2)

    print("\n" + "="*60)
    print(f"Success! Configuration written to {output_filename}".center(60))
    print("="*60)

if __name__ == "__main__":
    main()
