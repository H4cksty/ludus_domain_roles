#!/bin/bash

# This script clones the ludus_forest_build_roles repository and automatically
# finds and installs all Ansible roles contained within it for the current Ludus user.

# Exit immediately if a command exits with a non-zero status.
set -e

# Define the repository URL
REPO_URL="https://github.com/H4cksty/ludus_forest_build_roles.git"
REPO_DIR="ludus_forest_build_roles"

# Clone the repository
echo "Cloning repository..."
git clone "$REPO_URL"

# Navigate into the repository directory
cd "$REPO_DIR"

# Find all directories prefixed with "ludus_" and add them as roles
echo "Adding Ansible roles to Ludus..."
for d in ludus_*; do
  if [ -d "$d" ]; then
    echo "Adding role: $d"
    ludus ansible role add -d "./$d"
  fi
done

echo "All roles have been successfully installed."
