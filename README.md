# Everything Is Context

Give your agent a knowledge base it can navigate itself.

EIC is a workspace you create and maintain — a standalone, version-controlled repo where you define what your AI agent knows. Your integrations, your workflows, your active tasks. Structured as composable modules any AI can read.

![EIC demo](demo/eic-claude-demo.gif)

```
my-workspace/
  modules-repo/
    stripe/            → API keys, webhooks, how to query invoices
    postgres/          → schema, migrations, connection details
    deploy-pipeline/   → step-by-step release to production
    bug-triage/        → how to investigate and classify issues
```

When you point your agent at the workspace, it reads the module index, navigates to what it needs, and operates with full context. No re-explaining, no pasting, no "let me remind you how our Stripe setup works."

## Install

```bash
curl -LsSf https://everythingiscontext.com/eic/install.sh | sh
```

<details>
<summary>Alternative methods</summary>

```bash
# Via uv
uv tool install everythingiscontext

# Via pip
pip install everythingiscontext
```
</details>

## Quick start

**1. Initialize your workspace**

```bash
$ eic init

context/
  llms.txt
  integrations/
  workflows/
  tasks/
```

**2. Add an integration**

```
$ claude → "Add a postgres integration"

Creating context/integrations/postgres/
  info.md        ← context about the integration
  llms.txt       ← navigation for the agent
  module.yaml    ← secrets: [PG_URL]
✓ Module created. Requires PG_URL to populate.
```

**3. Provide the secret it needs**

```bash
# Add PG_URL to your .env file
echo "PG_URL=postgres://..." >> .env
```

**4. The agent fills in the context**

```
$ claude → "Explore the postgres integration and add the info to postgres/info.md"

Connecting with PG_URL...
  Found 12 tables, 47 columns, 8 relationships
  Writing schema to info.md
✓ Module ready. Agent knows your database.
```

**5. Query your data, add context anytime**

```
$ claude → "How many users signed up this week?"

Reads info.md → already knows users table has created_at
47 users — Free: 31, Pro: 12, Enterprise: 4
```

Need more context? The agent can add new modules anytime.

## How it works

You version-control your code. You version-control your docs. Now version-control what your AI agent knows.

A workspace has two directories:

- **`modules-repo/`** — where your modules live. Each module is a folder with a few markdown files describing one thing your agent should know about.
- **`context/`** — the active workspace. When you load a module, it appears here along with a generated index the agent reads to navigate.

The agent reads `context/system.md` → follows `llms.txt` → navigates into the module it needs. That's it.

## Module kinds

| Kind | What it captures | Example |
|------|-----------------|---------|
| **Integration** | How to use an external service, API, or database | Stripe, Postgres, GitHub, Slack |
| **Workflow** | A repeatable procedure that improves over time | Deploy to prod, triage bugs, onboard a teammate |
| **Task** | A bounded piece of work with progress tracking | Fix billing bug, migrate auth, ship feature X |

## Commands

| Command | What it does |
|---------|-------------|
| `eic init` | Create a new workspace |
| `eic new <kind> <name>` | Scaffold a module |
| `eic load <name> [...]` | Activate modules in the workspace |
| `eic unload <name>` | Deactivate a module |
| `eic ls` | List all modules and their status |
| `eic env` | Check if required secrets are set |
| `eic validate [name]` | Verify module structure |

## Works with everything

EIC produces plain markdown files with a navigable index. Any AI that reads files can use it:

Claude Code, Cursor, Windsurf, Copilot, ChatGPT, Codex — if it reads files, it reads EIC.

## Secrets

Modules can declare required environment variables. Values go in `.env` (gitignored). Run `eic env` to check what's missing.

## EIC Cloud

For a web UI with built-in AI chat, visual module editor, secrets management, and more — see [EIC Cloud](https://everythingiscontext.com).

---

Built by [Bleak AI](https://bleakai.com) | [everythingiscontext.com](https://everythingiscontext.com)
