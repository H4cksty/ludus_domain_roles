#!/usr/bin/python3

import yaml
import sys
import subprocess
import os
import re

# --- Helper Functions for System Interaction ---

def run_command(command, use_shell=False):
    """Runs a shell command and returns its output."""
    try:
        if use_shell:
            # Use shell=True for commands with pipes
            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True, encoding='utf-8')
        else:
            # Use a list of command arguments for safety
            result = subprocess.run(command.split(), check=True, capture_output=True, text=True, encoding='utf-8')
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {command}", file=sys.stderr)
        print(f"Stderr: {e.stderr}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print(f"Error: The command '{command.split()[0]}' was not found.", file=sys.stderr)
        print("Please ensure Ludus is installed and in your system's PATH.", file=sys.stderr)
        sys.exit(1)

def find_role_path(role_name):
    """Searches for a role directory in common locations."""
    search_paths = [os.path.expanduser("~"), '.']
    for path in search_paths:
        for root, dirs, files in os.walk(path):
            if role_name in dirs:
                if ".ansible" in root or "galaxy_storage" in root:
                    continue
                return os.path.join(root, role_name)
    return None

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

def get_int_input(prompt, default=None, min_val=None, max_val=None):
    """Gets integer input from the user, with validation."""
    while True:
        try:
            value_str = get_input(prompt, default)
            if value_str is None:
                print("This field is required.", file=sys.stderr)
                continue
            value = int(value_str)
            if min_val is not None and value < min_val:
                print(f"Value must be at least {min_val}.", file=sys.stderr)
                continue
            if max_val is not None and value > max_val:
                print(f"Value must be at most {max_val}.", file=sys.stderr)
                continue
            return value
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

def select_template(available_templates):
    """Displays a list of templates and gets user selection."""
    print("\nPlease select a VM template:")
    for i, t in enumerate(available_templates, 1):
        print(f"  {i}) {t}")

    choice = get_int_input("Enter template number", default=1, min_val=1, max_val=len(available_templates))
    return available_templates[choice - 1]

# --- Core Logic Functions ---

def get_available_templates():
    """Dynamically gets available Ludus templates."""
    print("Fetching available Ludus templates...")
    command_to_run = "ludus templates list | grep TRUE | awk '{print $2}'"
    output = run_command(command_to_run, use_shell=True)

    templates = [line for line in output.strip().split('\n') if line]

    if not templates:
        print("Could not find any built templates from 'ludus templates list'.", file=sys.stderr)
        print("Please ensure you have at least one built template.", file=sys.stderr)
        sys.exit(1)
    print("Templates successfully fetched.")
    return templates

def verify_and_install_roles():
    """Checks for required roles and installs them if missing."""
    print_header("Verifying Ansible Roles")
    required_roles = [
        "ludus_verify_dc_ready",
        "ludus_create_child_domain",
        "ludus_secondary_child_dc",
        "ludus_join_child_domain"
    ]

    print("Checking for installed roles...")
    # CORRECTED: Use the robust bash pipeline provided by the user.
    command_to_run = "ludus ansible role list | grep ludus_ | awk '{print $2}'"
    installed_output = run_command(command_to_run, use_shell=True)
    installed_roles = [role.strip() for role in installed_output.strip().split('\n') if role]

    missing_roles = [role for role in required_roles if role not in installed_roles]

    if not missing_roles:
        print("All required roles are already installed.")
        return

    print(f"Missing roles found: {', '.join(missing_roles)}")
    if get_yes_no("Attempt to find and install them?", 'y'):
        for role in missing_roles:
            print(f"Searching for role '{role}'...")
            role_path = find_role_path(role)
            if role_path:
                print(f"Found at '{role_path}'. Installing...")
                run_command(f"ludus ansible role add -d {role_path}")
                print(f"Successfully installed '{role}'.")
            else:
                print(f"Error: Could not find directory for role '{role}'.", file=sys.stderr)
                print("Please ensure the ludus_forest_build_roles repository is cloned in your home directory or the current directory.", file=sys.stderr)
                sys.exit(1)
    else:
        print("Cannot proceed without required roles. Exiting.", file=sys.stderr)
        sys.exit(1)

def get_default_settings():
    """Gathers the global default settings for the range."""
    print_header("Global Default Settings")

    if get_yes_no("Use default values for all settings?", 'y'):
        return {
            'ad_domain_admin': "domainadmin",
            'ad_domain_admin_password': "password",
            'ad_domain_user': "domainuser",
            'ad_domain_user_password': "password",
            'ad_domain_safe_mode_password': "YourComplexPassword!1",
            'timezone': "America/Chicago",
            'ad_domain_functional_level': "Win2012R2",
            'ad_forest_functional_level': "Win2012R2",
            'snapshot_with_RAM': True,
            'stale_hours': 0,
            'enable_dynamic_wallpaper': True
        }

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

def define_parent_domain(range_id, use_full_clones, templates):
    """Gathers details for the parent domain and its machines."""
    print_header("Parent Domain Configuration")
    vms = []

    fqdn = get_input("Parent Domain FQDN (e.g., ershon.local)", "ershon.local")
    netbios = get_input("Parent Domain NETBIOS Name (e.g., ERSHON)", fqdn.split('.')[0].upper())
    vlan = get_int_input("Parent Domain VLAN", 10)

    # Primary DC
    print("\n--- Parent Primary DC ---")
    pdc_hostname = get_input("Primary DC Hostname", f"{netbios}-DC1")
    pdc_ip_octet = get_int_input("Primary DC IP Last Octet", 10)
    pdc_vm = {
        'vm_name': f"{{{{ range_id }}}}-{pdc_hostname}",
        'hostname': pdc_hostname,
        'template': select_template(templates),
        'vlan': vlan,
        'ip_last_octet': pdc_ip_octet,
        'ram_gb': get_int_input("RAM (GB)", 4),
        'cpus': get_int_input("CPUs", 4),
        'full_clone': use_full_clones,
        'domain': {'fqdn': fqdn, 'role': 'primary-dc'},
        'windows': {'sysprep': True, 'gpos': ['disable_defender']},
        'roles': ['ludus_verify_dc_ready']
    }
    vms.append(pdc_vm)

    # Optional Secondary DCs
    num_secondary_dcs = get_int_input("How many secondary DCs for the parent domain?", 0)
    for i in range(num_secondary_dcs):
        print(f"\n--- Parent Secondary DC #{i+1} ---")
        sdc_hostname = get_input("Secondary DC Hostname", f"{netbios}-DC{i+2}")
        sdc_ip_octet = get_int_input("Secondary DC IP Last Octet", 11 + i)
        sdc_vm = {
            'vm_name': f"{{{{ range_id }}}}-{sdc_hostname}",
            'hostname': sdc_hostname,
            'template': select_template(templates),
            'vlan': vlan,
            'ip_last_octet': sdc_ip_octet,
            'ram_gb': get_int_input("RAM (GB)", 4),
            'cpus': get_int_input("CPUs", 2),
            'full_clone': use_full_clones,
            'windows': {'sysprep': True},
            'domain': {'fqdn': fqdn, 'role': 'alt-dc'}
        }
        vms.append(sdc_vm)

    return vms, fqdn, netbios, {'vlan': vlan, 'octet': pdc_ip_octet, 'hostname': pdc_hostname}

def define_child_domain(range_id, parent_fqdn, parent_netbios, parent_dc_info, use_full_clones, templates):
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
    pdc_hostname = get_input("Primary DC Hostname", f"{child_netbios}-DC1")
    pdc_ip_octet = get_int_input("Primary DC IP Last Octet", 10)

    pdc_vm = {
        'vm_name': f"{{{{ range_id }}}}-{pdc_hostname}",
        'hostname': pdc_hostname,
        'template': select_template(templates),
        'vlan': child_vlan,
        'ip_last_octet': pdc_ip_octet,
        'ram_gb': get_int_input("RAM (GB)", 4),
        'cpus': get_int_input("CPUs", 4),
        'full_clone': use_full_clones,
        'windows': {'sysprep': True},
        'roles': [{'name': 'ludus_create_child_domain', 'depends_on': [{'vm_name': f"{{{{ range_id }}}}-{parent_dc_info['hostname']}", 'role': 'ludus_verify_dc_ready'}]}],
        'role_vars': {'dns_domain_name': child_fqdn, 'parent_domain_netbios_name': parent_netbios, 'parent_dc_ip': f"10.2.{parent_dc_info['vlan']}.{parent_dc_info['octet']}"}
    }
    vms.append(pdc_vm)

    # Optional Secondary DC
    num_secondary_dcs = get_int_input(f"How many secondary DCs for {child_netbios}?", 0)
    for i in range(num_secondary_dcs):
        print(f"\n--- {child_netbios} Secondary DC #{i+1} ---")
        sdc_hostname = get_input("Secondary DC Hostname", f"{child_netbios}-DC{i+2}")
        sdc_ip_octet = get_int_input("Secondary DC IP Last Octet", 11 + i)
        sdc_vm = {
            'vm_name': f"{{{{ range_id }}}}-{sdc_hostname}",
            'hostname': sdc_hostname,
            'template': select_template(templates),
            'vlan': child_vlan,
            'ip_last_octet': sdc_ip_octet,
            'ram_gb': get_int_input("RAM (GB)", 4),
            'cpus': get_int_input("CPUs", 2),
            'full_clone': use_full_clones,
            'windows': {'sysprep': True},
            'roles': [{'name': 'ludus_secondary_child_dc', 'depends_on': [{'vm_name': pdc_vm['vm_name'], 'role': 'ludus_create_child_domain'}]}],
            'role_vars': {'dns_domain_name': child_fqdn, 'parent_domain_netbios_name': parent_netbios, 'existing_dc_ip': f"10.2.{child_vlan}.{pdc_ip_octet}"}
        }
        vms.append(sdc_vm)

    # Child Members
    num_members = get_int_input(f"How many member workstations/servers for {child_netbios}?", 0)
    for i in range(num_members):
        print(f"\n--- {child_netbios} Member #{i+1} ---")
        mem_hostname = get_input("Member Hostname", f"{child_netbios}-WKS{i+1}")
        mem_ip_octet = get_int_input("Member IP Last Octet", 100 + i)

        mem_vm = {
            'vm_name': f"{{{{ range_id }}}}-{mem_hostname}",
            'hostname': mem_hostname,
            'template': select_template(templates),
            'vlan': child_vlan,
            'ip_last_octet': mem_ip_octet,
            'ram_gb': get_int_input("RAM (GB)", 4),
            'cpus': get_int_input("CPUs", 2),
            'full_clone': use_full_clones,
            'windows': {'sysprep': True},
            'roles': [{'name': 'ludus_join_child_domain', 'depends_on': [{'vm_name': pdc_vm['vm_name'], 'role': 'ludus_create_child_domain'}]}],
            'role_vars': {'dc_ip': f"10.2.{child_vlan}.{pdc_ip_octet}", 'dns_domain_name': child_fqdn, 'child_domain_netbios_name': child_netbios}
        }
        vms.append(mem_vm)

    return vms

def define_standalone_vms(range_id, use_full_clones, templates):
    """Gathers details for non-domain-joined machines."""
    vms = []
    num_standalone = get_int_input("\nHow many non-domain-joined machines?", 0)
    for i in range(num_standalone):
        print_header(f"Standalone VM #{i+1}")
        hostname = get_input("Hostname")
        vlan = get_int_input("VLAN")
        ip_octet = get_int_input("IP Last Octet")
        template = select_template(templates)
        is_linux = 'linux' in template or 'ubuntu' in template or 'kali' in template

        vm = {
            'vm_name': f"{{{{ range_id }}}}-{hostname}",
            'hostname': hostname,
            'template': template,
            'vlan': vlan,
            'ip_last_octet': ip_octet,
            'ram_gb': get_int_input("RAM (GB)", 2),
            'cpus': get_int_input("CPUs", 1),
            'full_clone': use_full_clones
        }
        if is_linux:
            vm['linux'] = True
        else:
            vm['windows'] = {'sysprep': True}
        vms.append(vm)
    return vms

# --- Main Execution ---

def main():
    """Main function to drive the configuration script."""
    print_header("Ludus Forest Build Roles Config Generator")
    print("This script will guide you through creating a ludus-config.yml file.")

    output_filename = get_input("Enter output filename", "generated-config.yml")
    range_id = get_input("Enter your Ludus Range ID (e.g., MH)", "MH")
    use_full_clones = get_yes_no("Use full clones instead of linked clones? (slower but independent)", 'n')

    available_templates = get_available_templates()
    verify_and_install_roles()

    config = {
        'defaults': get_default_settings(),
        'network': {
            'inter_vlan_default': 'ACCEPT',
            'external_default': 'ACCEPT'
        },
        'ludus': []
    }

    # Parent Domain
    parent_vms, parent_fqdn, parent_netbios, parent_dc_info = define_parent_domain(range_id, use_full_clones, available_templates)
    config['ludus'].extend(parent_vms)

    # Child Domains
    num_child_domains = get_int_input("\nHow many child domains do you want to create?", 0)
    for i in range(num_child_domains):
        print_header(f"Child Domain #{i+1}")
        child_vms = define_child_domain(range_id, parent_fqdn, parent_netbios, parent_dc_info, use_full_clones, available_templates)
        config['ludus'].extend(child_vms)

    # Standalone Machines
    standalone_vms = define_standalone_vms(range_id, use_full_clones, available_templates)
    config['ludus'].extend(standalone_vms)

    # Save the configuration to a YAML file
    with open(output_filename, 'w') as f:
        def str_presenter(dumper, data):
            if '{{' in data:
                return dumper.represent_scalar('tag:yaml.org,2002:str', data, style="'")
            return dumper.represent_scalar('tag:yaml.org,2002:str', data)

        yaml.add_representer(str, str_presenter)
        yaml.dump(config, f, default_flow_style=False, sort_keys=False, indent=2)

    print("\n" + "="*60)
    print(f"Success! Configuration written to {output_filename}".center(60))
    print("="*60)

    # Post-creation actions
    while True:
        print("\nWhat would you like to do next?")
        print("  1) Set the config for the current range")
        print("  2) Set and DEPLOY the config for the current range")
        print("  3) Exit")
        choice = get_int_input("Enter your choice", 3)

        if choice == 1:
            print(f"Running: ludus range config set -f {output_filename}")
            run_command(f"ludus range config set -f {output_filename}")
            print("Configuration set successfully.")
            break
        elif choice == 2:
            print(f"Running: ludus range config set -f {output_filename}")
            run_command(f"ludus range config set -f {output_filename}")
            print("Configuration set. Starting deployment...")
            # Using os.system for interactive commands like deploy and watch
            os.system("ludus range deploy")
            print("\nDeployment command finished. Starting status watch...")
            print("Press Ctrl+C to exit watch.")
            os.system(f"watch -c 'ludus range list'")
            break
        elif choice == 3:
            print("Exiting.")
            break
        else:
            print("Invalid choice.", file=sys.stderr)


if __name__ == "__main__":
    main()
