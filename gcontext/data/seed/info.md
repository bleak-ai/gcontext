# seed

## Purpose
A starter module seeded into a fresh workspace. It is not a real integration; it exists to show the structure of a context module so you have a reference when creating your own. Replace or delete it once you have real modules.

## Where it lives
This module exists locally in your workspace, under `modules-repo/seed/`.

## Auth & access
No authentication needed: this is a documentation-only module.

## Key entities
- **Modules**: folders with a `module.yaml` and `llms.txt`
- **Kinds**: integration, task, or workflow

## Operations
- Read this module's files to understand the structure
- Create your own module with `gcontext new integration <name>`

## Examples
```bash
# Create a new integration module
gcontext new integration stripe

# Load it into the workspace
gcontext load stripe

# Check module structure
gcontext validate stripe
```
