# Ludus Config Builder Script

An interactive command-line wizard for generating complex `ludus-config.yml` files.

## Overview

This Python script provides a guided, interactive experience for creating sophisticated `ludus-config.yml` files that leverage the `ludus_forest_build_roles` collection. It automates the most error-prone parts of the configuration process, ensuring that all custom roles are used correctly and that the resulting lab environment is robust and reliable.

## Key Features

* **Interactive Wizard:** Guides the user through every step of the lab design, from global defaults to individual VM configurations.
* **Dynamic Lookups:** Automatically fetches available Ludus templates and verifies that the required Ansible roles are installed on the system.
* **Automated Role Installation:** If required roles are missing, the script can find them within your home directory (assuming the project is cloned there) and install them automatically.
* **Intelligent Defaults:** Offers the option to use pre-configured, sensible defaults to speed up the configuration process.
* **Post-Generation Actions:** After creating the `ludus-config.yml` file, provides a menu to immediately set the config, deploy the range, and monitor its status.

## Prerequisites

1.  **Python 3.9+** installed on your system.
2.  The **PyYAML** library. You can install it via pip:
    ```bash
    pip install pyyaml
    ```
3.  The **Ludus CLI** must be installed and configured in your system's PATH.
4.  The `ludus_forest_build_roles` repository should be cloned to your home directory or the directory from which you run the script.

## How to Use

1.  Save the script as `build_ludus_config.py` on your machine.
2.  Open your terminal or command prompt, navigate to the directory where you saved the file, and make it executable:
    ```bash
    chmod +x build_ludus_config.py
    ```
3.  Run the script:
    ```bash
    ./build_ludus_config.py
    ```
4.  Follow the on-screen prompts. The script will ask for all necessary information, such as the output filename, your Ludus range ID, and details for each domain and virtual machine you wish to create.
5.  **Pro Tip:** For the fastest experience, accept the default values when prompted (by pressing Enter), especially for the "Global Default Settings." This will quickly generate a standard, functional configuration.
6.  Once the `generated-config.yml` (or your custom filename) is created, the script will present a menu with options to set the config, deploy the range, or exit.
