# Shared Conda Environments Guide

This guide explains how to create and manage shared Conda environments in multi-user systems, particularly for JupyterHub environments using network file systems like Amazon EFS.

## JupyterHub-Specific Considerations

In JupyterHub environments, you'll typically notice:

```bash
# Check your username
whoami    # Returns "jovyan"
echo $USER    # Returns "jovyan"
id -un    # Returns "jovyan"
```

The username "jovyan" is the default in JupyterHub deployments (named after Jovian/Jupiter). Important notes:

1. **Shared Username**: All users often share the same system username "jovyan"
2. **User Separation**: JupyterHub differentiates users at the application level, not the Unix level
3. **File Ownership**: Files you create will show owner "jovyan" regardless of which JupyterHub user you are
4. **Security Implications**: Permissions and group memberships become critically important

For this reason, JupyterHub deployments typically use one of these approaches:
- **User Volumes**: Each user gets a separate persistent volume mounted at a unique location
- **Unix Groups**: All users share the "jovyan" username but belong to different groups
- **Shared Environments**: Carefully controlled shared spaces like `/efs/shared/`

## Conda Environment Locations

To check where Conda looks for environments, use:

```bash
conda config --show envs_dirs
```

Typical locations include:
- Personal environments: `/home/username/.conda/envs/`
- Shared environments: `/efs/shared/.conda/envs/` 

## Creating a Shared Environment

### 1. Specify the Prefix in YAML

In your environment YAML file (e.g., `internvl_env.yml`), add a prefix pointing to the shared location:

```yaml
name: internvl_env
channels:
  - pytorch
  - conda-forge
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

## JupyterHub Environment Management

For JupyterHub administrators and users:

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

### Multiple Users with Same System Username

Since all users appear as "jovyan" at the system level:

```bash
# Create a command to identify which JupyterHub user you are
echo "export JUPYTERHUB_USER=\$(echo \$JUPYTERHUB_API_URL | cut -d'/' -f4)" >> ~/.bashrc
source ~/.bashrc
echo "JupyterHub user: $JUPYTERHUB_USER"
```

### User-Specific Environment Tricks

You can create user-specific environment locations even with shared "jovyan" username:

```bash
# Use JupyterHub username in environment path
export MY_JUPYTER_USER=$(echo $JUPYTERHUB_API_URL | cut -d'/' -f4)
conda env create -f environment.yml --prefix /efs/shared/.conda/envs/${MY_JUPYTER_USER}_internvl_env
```

This creates separate environments for each JupyterHub user while maintaining shared access when desired.