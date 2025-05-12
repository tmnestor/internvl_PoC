# Shared Conda Environments Guide

This guide explains how to create and manage shared Conda environments in multi-user systems, JupyterHub environments using the Amazon EFS network file system.

## Conda Environment Locations

To check where Conda looks for environments, use:

```bash
conda config --show envs_dirs
```

Typical locations include:
- Personal environments: `/home/jovyan/.conda/envs/`
- Shared environments: `/efs/shared/.conda/envs/` 

## Creating a Shared Environment

### 1. Specify the Prefix in YAML

In your environment YAML file (e.g., `internvl_env.yml`), add a prefix pointing to the shared location:

```yaml
name: internvl_env
channels:
  # - /
  # - https://artifactory.ctz.atocnet.gov.au/artifactory/api/conda/sdpaapds-conda-develop-local
  - defaults
dependencies:
  - python=3.11
  # ... other dependencies
prefix: /efs/shared/.conda/envs/internvl_env
```

For JupyterHub environments where everyone shares the "jovyan" username, this approach becomes particularly important. The prefix path should point to a location that:

1. Has appropriate permissions for all intended users
2. Is mounted consistently across all user instances
3. Persists between JupyterHub restarts

### 2. Create the Environment

```bash
# This may not work if command line options override the YAML prefix
conda env create -f internvl_env.yml

# If the environment is still created in ~/.conda/envs, use this explicit approach:
conda env create -f internvl_env.yml -p /efs/shared/.conda/envs/internvl_env
```

**Note about prefix issues:** If your environment is still being created in `~/.conda/envs/internvl_env` despite having set `prefix:` in the YAML:

1. Command line options (`-n` or `--name`) override the YAML prefix
2. Some versions of conda may prioritize the name over the prefix in the YAML
3. Your conda config might have settings that override the prefix

Always use the `-p` or `--prefix` flag directly when creating a shared environment to ensure the correct location:

## Setting Proper Permissions

For true sharing, correct directory permissions are essential.

### Understanding Unix Permissions

The permission string "drwxrws---" represents:
- **d**: Directory
- **rwx**: Owner has read, write, and execute permissions
- **rw-**: Group has read and write permissions
- **s**: SGID (Set Group ID) bit is set
- **---**: Others have no permissions

### Setting SGID for Shared Directories

The SGID bit ensures all new files created in the directory inherit the directory's group ownership:

```bash
# Set permissions with SGID (2770)
chmod 2770 /efs/shared/.conda/envs/internvl_env
```

### Group Ownership

Make sure the directory is owned by the correct group:

```bash
# Check your group
id -gn  # Returns your current group, e.g., "users"

# Set group ownership
chgrp users /efs/shared/.conda/envs/internvl_env
```

### Recursive Permissions

For existing environments that need to be shared:

```bash
# Set permissions recursively
chmod -R 2770 /efs/shared/.conda/envs/internvl_env
chgrp -R users /efs/shared/.conda/envs/internvl_env
```

## Activating Shared Environments

Users can activate the shared environment using its full path:

```bash
conda activate /efs/shared/.conda/envs/internvl_env
```

Or add the shared directory to their conda config:

```bash
conda config --append envs_dirs /efs/shared/.conda/envs
```

Then activate by name:

```bash
conda activate internvl_env
```

### Creating an Activation Alias (Recommended)

For convenience, users can add an alias to their .bashrc file:

```bash
echo 'alias activate_internvl="conda activate /efs/shared/.conda/envs/internvl_env"' >> ~/.bashrc && source ~/.bashrc
```

After running this command, users can simply type `activate_internvl` to activate the shared environment. This is especially useful in JupyterHub environments where typing the full path repeatedly can be tedious.

## Checking Group Membership

To see who's in your group:

```bash
# Show your current group
id -gn

# List members of your group
getent group $(id -gn)

# Show all groups you belong to
groups
```

## Managing Shared Packages

When multiple users can modify a shared environment:

1. **Designate an administrator** responsible for major updates
2. **Use environment files** for version control of dependencies
3. **Communicate changes** to other users before making them
4. **Consider setting up a staging environment** for testing changes

## Updating the Shared Environment

As the designated administrator for the shared environment, follow these steps to update it:

### 1. Update the Environment YAML File

First, update the `internvl_env.yml` file with any new dependencies or version changes:

```yaml
name: internvl_env
# ... other settings
dependencies:
  - python=3.11
  - new_package=1.2.3
  # ... other dependencies
prefix: /efs/shared/.conda/envs/internvl_env
```

### 2. Notify Users Before Making Changes

Send a notification to all users with:
- Planned update time
- Expected downtime
- List of changes being made
- Any required actions on their part

### 3. Update the Environment

```bash
# Update the environment using the YAML file
conda env update -f internvl_env.yml -p /efs/shared/.conda/envs/internvl_env --prune

# The --prune flag removes dependencies that are no longer listed in the YAML
```

### 4. Fix Permissions After Update

```bash
# Ensure proper permissions after update
chmod -R 2770 /efs/shared/.conda/envs/internvl_env
chgrp -R users /efs/shared/.conda/envs/internvl_env
```

### 5. Test the Updated Environment

```bash
# Activate the environment
conda activate /efs/shared/.conda/envs/internvl_env

# Run verification tests
python -c "import new_package; print(new_package.__version__)"
python verify_env.py  # If you have a verification script
```

### 6. Document the Changes

Keep a record of all updates in a changelog, including:
- Date of update
- Packages added/removed/updated
- Any breaking changes
- Compatibility notes

### 7. Notify Users of Completed Update

Send a confirmation message that the update is complete with:
- Summary of changes made
- Any new usage instructions
- Contact point for reporting issues

## Troubleshooting

### Permission Denied Errors

If users get "permission denied" when trying to install packages:

```bash
# Check file ownership
ls -la /efs/shared/.conda/envs/internvl_env

# Fix permissions if needed
chmod -R g+w /efs/shared/.conda/envs/internvl_env
```

In JupyterHub environments with shared "jovyan" username:

```bash
# See which JupyterHub user you're logged in as (at the application level)
# This is often shown in the JupyterHub interface or URL

# Check if you can access the shared environment
conda env list | grep /efs/shared

# If issues persist, your JupyterHub instance may have mount permission issues
# Contact your JupyterHub administrator
```

### Conflicts Between Users

If users need different packages:

1. Consider creating a base shared environment with common packages
2. Use pip's `--user` flag for personal installations
3. Use Conda environments that build upon the shared base

## Python Virtual Environments Alternative

For scenarios where Conda isn't ideal, Python virtual environments can be shared:

```bash
# Create a shared venv
python -m venv /efs/shared/venvs/internvl_env

# Set permissions
chmod -R 2770 /efs/shared/venvs/internvl_env
chgrp -R users /efs/shared/venvs/internvl_env

# Activate
source /efs/shared/venvs/internvl_env/bin/activate
```

Then install packages as normal with pip.

## Best Practices

1. **Document the environment** for all users
2. **Version control** your environment files
3. **Regularly update** the environment and clean up unused packages
4. **Consider package compatibility** before adding new dependencies
5. **Test changes** in a separate environment before updating the shared one


### Forcing Environment Location

If you're having trouble creating environments in the shared location:

```bash
# First, ensure the target directory exists with proper permissions
mkdir -p /efs/shared/.conda/envs
chmod 2775 /efs/shared/.conda/envs

# Then create the environment with explicit prefix
conda env create -f internvl_env.yml -p /efs/shared/.conda/envs/internvl_env --force

# Or use conda create directly (instead of from YAML)
conda create -p /efs/shared/.conda/envs/internvl_env python=3.11 pytorch torchvision -c pytorch
```

This approach ensures the environment goes exactly where you want it, regardless of YAML settings or conda defaults.

