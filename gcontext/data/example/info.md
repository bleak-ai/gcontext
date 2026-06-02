# example

## Purpose
This is a sample module showing the structure of a context module. Use it as a reference when creating your own modules.

## Where it lives
This module exists locally in your workspace.

## Auth & access
No authentication needed — this is a documentation-only module.

## Key entities
- **Modules** — folders with a `module.yaml` and `llms.txt`
- **Kinds** — integration, task, or workflow

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
