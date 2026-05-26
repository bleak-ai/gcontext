# Everything Is Context

**Context engineering for AI agents.**

Build context like you build code: modular, version-controlled, composable.

---

## The problem

AI agents fail for the same reason large codebases fail: **implicit state.**

Prompts become undocumented architecture. Instructions drift between conversations. Context duplicates across files. Memory becomes unreliable. Every session starts with "let me remind you how our deploy works."

This isn't a model problem. It's an engineering problem.

Most teams solve it by writing longer prompts, pasting more docs, or hoping the agent remembers. That works until it doesn't, and it stops working fast.

**EIC treats context as infrastructure.**

---

## Before and after

**Without structured context:**
- Giant system prompts nobody maintains
- Copy-pasted docs that go stale
- "Remember, our Stripe webhook is at..." every session
- Agent hallucinates because it can't find what it needs
- Context bloat kills quality on long tasks
- Tribal knowledge lives in one person's prompt history

**With EIC:**

```
context/
  modules-repo/
    stripe/            → API keys, webhooks, how to query invoices
    postgres/          → schema, migrations, connection details
    deploy-pipeline/   → step-by-step release to production
    bug-triage/        → how to investigate and classify issues
```

Each module is a self-contained unit of context. Load what the task needs, unload what it doesn't. The agent navigates to what's relevant. Nothing else enters the window.

![EIC demo](demo/eic-claude-demo.gif)

---

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
47 users. Free: 31, Pro: 12, Enterprise: 4
```

Need more context? The agent can add new modules anytime.

---

## How it works: composable context

EIC introduces one core mechanic: **composable context**.

Modules are independent units of knowledge: an API integration, a deployment procedure, a bug investigation. Each contains plain markdown and a navigation index (`llms.txt`) the agent uses to find what it needs.

```
agent reads system.md
  └─ follows llms.txt index
       ├─ stripe/llms.txt    → "here's how Stripe works here"
       ├─ postgres/llms.txt  → "here's the database"
       └─ deploy/llms.txt    → "here's how to ship"
            └─ steps.md      → the actual procedure
```

**Navigation, not retrieval.** The agent walks a knowledge tree. It doesn't search a vector space. Deterministic, inspectable, reproducible.

You version-control your code. You version-control your docs. Now version-control what your AI agent knows.

## Module kinds

| Kind | What it captures | Lifecycle | Example |
|------|-----------------|-----------|---------|
| **Integration** | How to use an external service, API, or database | Permanent: lives as long as the service does | Stripe, Postgres, GitHub, Slack |
| **Workflow** | A repeatable procedure that improves over time | Long-lived: gets better with each run | Deploy to prod, triage bugs, onboard a teammate |
| **Task** | A bounded piece of work with progress tracking | Disposable: done when the work is done | Fix billing bug, migrate auth, ship feature X |

Different shapes for different lifecycles. They coexist and compose.

---

## Real workflows

**Software engineering team**

```
context/
  modules-repo/
    postgres/          → schema, connection, query patterns
    github/            → repo structure, PR conventions, CI
    deploy-pipeline/   → release steps, rollback procedures
    fix-billing-bug/   → task: reproduce, investigate, fix, verify
```

The agent reads the database schema, understands CI, follows the deploy playbook, and tracks progress on the billing fix, all from structured context.

**Support automation**

```
context/
  modules-repo/
    zendesk/           → API access, ticket categories, macros
    stripe/            → subscription lookup, refund procedures
    knowledge-base/    → product docs, known issues, FAQ
    escalation/        → workflow: when and how to escalate
```

An agent triaging tickets reads the Zendesk integration, checks Stripe for billing context, references the KB, and follows escalation rules, without a 10,000-token system prompt.

**Content pipeline**

```
context/
  modules-repo/
    cms/               → API, content models, publishing flow
    brand-voice/       → tone guidelines, examples, anti-patterns
    analytics/         → what performs, audience segments
    weekly-newsletter/ → task: this week's edition
```

**Claude Code / Cursor workflow**

```
context/
  modules-repo/
    codebase/          → architecture, conventions, key paths
    cloudflare/        → DNS, workers, deployment targets
    monitoring/        → Grafana dashboards, alert rules
    ship-v2-auth/      → task: migrate auth with progress tracking
```

Point your coding agent at the workspace. It navigates to the module it needs per task: your codebase conventions when writing code, your deploy integration when shipping, your monitoring setup when debugging production.

---

## What EIC is not

EIC is not:

- **A vector database.** No embeddings. The agent navigates a file tree, not a similarity search.
- **A memory model.** No implicit memory. Context is explicit, human-curated, version-controlled.
- **A replacement for RAG.** Complementary. EIC structures the knowledge RAG can retrieve from.
- **An autonomous agent framework.** No agent runtime. Works with the agent you already use.
- **Another orchestration layer.** No workflow engine. Just structured, navigable knowledge.

**EIC is a context engineering toolkit.** It gives your agent a composable knowledge base it can navigate itself.

---

## Why the filesystem

> "Why not just use a vector database / memory layer?"

| | Filesystem (EIC) | Vector DB / Memory |
|---|---|---|
| **Version control** | `git diff`, `git blame`, full history | Requires custom versioning |
| **Inspectability** | Open a folder, read the files | Query an API, decode embeddings |
| **Determinism** | Same files = same context, every time | Similarity search varies |
| **Human readability** | It's markdown | It's vectors |
| **Composability** | Load/unload modules like imports | Rebuild index on every change |
| **Tooling** | Works with every editor, CI, linter | Needs specialized tooling |
| **Portability** | Copy the folder | Export, migrate, re-index |

The filesystem is the most universal, inspectable, composable storage layer that exists. Your agent's context should be as maintainable as the code it operates on.

---

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

Claude Code, Cursor, Windsurf, Copilot, ChatGPT, Codex. If it reads files, it reads EIC.

## Secrets

Modules can declare required environment variables. Values go in `.env` (gitignored). Run `eic env` to check what's missing.

## EIC Cloud

For a web UI with built-in AI chat, visual module editor, secrets management, and more, see [EIC Cloud](https://everythingiscontext.com).

---

Built by [Bleak AI](https://bleakai.com) | [everythingiscontext.com](https://everythingiscontext.com)
