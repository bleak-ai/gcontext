# gcontext

**Version-controlled context modules your AI agent navigates itself.**

[![PyPI](https://img.shields.io/pypi/v/gcontext-ai)](https://pypi.org/project/gcontext-ai/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/pypi/pyversions/gcontext-ai)](https://pypi.org/project/gcontext-ai/)

Your agent's knowledge as plain markdown in git: modular, reviewable, loaded per task. No embeddings, no memory layer, no new runtime. Works with Claude Code, Cursor, Codex — anything that reads files.

![gcontext demo](demo/gcontext-claude-demo.gif)

---

## The problem

AI agents fail for the same reason large codebases fail: **implicit state.**

Prompts become undocumented architecture. Instructions drift between conversations. Context duplicates across files. Every session starts with "let me remind you how our deploy works."

This isn't a model problem. It's an engineering problem.

Most teams solve it by writing longer prompts, pasting more docs, or hoping the agent remembers. That works until it doesn't, and it stops working fast.

**gcontext treats context as infrastructure.**

---

## Before and after

**Without structured context:**

- Giant system prompts nobody maintains
- Copy-pasted docs that go stale
- "Remember, our Stripe webhook is at..." every session
- Agent hallucinates because it can't find what it needs
- Context bloat kills quality on long tasks
- Tribal knowledge lives in one person's prompt history

**With gcontext:**

```
modules-repo/
  stripe/            → API keys, webhooks, how to query invoices
  postgres/          → schema, migrations, connection details
  deploy-pipeline/   → step-by-step release to production
  bug-triage/        → how to investigate and classify issues
```

Each module is a self-contained unit of context. Load what the task needs, unload what it doesn't. The agent navigates to what's relevant. Nothing else enters the window.

---

## Install

```bash
curl -LsSf https://gcontext.ai/gcontext/install.sh | sh
# or
uv tool install gcontext-ai   # PyPI name is gcontext-ai; the command is `gcontext`
# or
pip install gcontext-ai
```

## Quick start

`gcontext init` is the only command you have to run. After that, your agent operates the workspace itself — it can create modules, fill them in, and load them, because the workspace tells it how.

**1. Initialize**

```bash
$ gcontext init

Created modules-repo/
Created context/
Ready. Open your agent and ask it to create a module — or run: gcontext new integration <name>
```

This gives you:

```
AGENTS.md            # auto-loaded by your agent; points it at context/system.md
CLAUDE.md            # one line: @AGENTS.md (Claude Code reads this file)
context/             # what the agent reads: generated llms.txt index + symlinks to loaded modules
modules-repo/        # source of truth: your modules (seeded with an example/)
.gitignore           # ignores .env
```

Re-running `gcontext init` in an existing workspace errors out — it never overwrites your files.

**2. Open your agent and ask for a module** *(condensed session — your output will differ)*

```
$ claude → "Add a postgres integration"

Creating modules-repo/postgres/
  info.md        ← context about the integration
  llms.txt       ← navigation index for this module
  module.yaml    ← declares it needs a PG_URL secret (name only, no value)
```

**3. Provide the secret it needs**

```bash
echo "PG_URL=postgres://..." >> .env    # gitignored; only the *name* is in the module
```

Use read-only credentials where you can, and review what the agent writes into a module before committing — it documents what it sees.

**4. Let the agent fill in the context**

```
$ claude → "Explore the postgres integration and document it in modules-repo/postgres/info.md"

Connecting with PG_URL...
  Found 12 tables, 31 columns, 8 relationships
  Writing schema to info.md
```

**5. Use it — in this session or any future one**

```
$ claude → "How many users signed up this week?"

Reads postgres/info.md → already knows users has created_at
47 users. Free: 31, Pro: 12, Enterprise: 4
```

Prefer doing things by hand? Every step is also a deterministic command — `gcontext new`, `gcontext load`, `gcontext ls`, `gcontext validate`. See [Commands](#commands). The agent uses the same files either way.

---

## How it works: navigation, not retrieval

Modules are independent units of knowledge: an API integration, a deployment procedure, a bounded piece of work. Each contains plain markdown and a navigation index (`llms.txt`) the agent uses to find what it needs.

```
agent reads system.md
  └─ follows the llms.txt index
       ├─ stripe/llms.txt    → "here's how Stripe works here"
       ├─ postgres/llms.txt  → "here's the database"
       └─ deploy/llms.txt    → "here's how to ship"
            └─ steps.md      → the actual procedure
```

Only the index — one line per module — is always in context. Detail enters the window when the agent follows a link, fresh at the moment the task needs it. Unloaded modules cost zero tokens.

The mechanics are deliberately boring: `gcontext load postgres` creates a symlink `context/postgres → modules-repo/postgres` and regenerates the one-line-per-module index in `context/llms.txt`. `unload` removes the link. No copies, no database, no daemon — `modules-repo/` is the only place content lives, and you can inspect every byte the agent could read by opening a folder.

What's actually on disk after `init` — the seeded example module's `llms.txt`:

```
# example

> A sample module demonstrating the context module structure

- [info.md](info.md): What this module contains and how to use it
- [module.yaml](module.yaml): Module configuration
```

That's the whole trick: an index file per module, one root index over the loaded set, and an `AGENTS.md` that tells the agent to start there.

The agent walks a knowledge tree; it doesn't search a vector space. You can't force a model to read anything — but you can make the relevant file one link away instead of buried at token 50,000, and you can see exactly what was available to it. You version-control your code and your docs — this is version control for what your agent knows.

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
modules-repo/
  postgres/          → schema, connection, query patterns
  github/            → repo structure, PR conventions, CI
  deploy-pipeline/   → release steps, rollback procedures
  fix-billing-bug/   → task: reproduce, investigate, fix, verify
```

The agent reads the database schema, understands CI, follows the deploy playbook, and tracks progress on the billing fix — all from structured context.

**Support automation**

```
modules-repo/
  zendesk/           → API access, ticket categories, macros
  stripe/            → subscription lookup, refund procedures
  knowledge-base/    → product docs, known issues, FAQ
  escalation/        → workflow: when and how to escalate
```

An agent triaging tickets reads the Zendesk integration, checks Stripe for billing context, references the KB, and follows escalation rules — without a 10,000-token system prompt.

**Claude Code / Cursor workflow**

```
modules-repo/
  codebase/          → architecture, conventions, key paths
  cloudflare/        → DNS, workers, deployment targets
  monitoring/        → Grafana dashboards, alert rules
  ship-v2-auth/      → task: migrate auth with progress tracking
```

Point your coding agent at the workspace. It navigates to the module it needs per task: your conventions when writing code, your deploy integration when shipping, your monitoring setup when debugging production.

---

## FAQ

**Isn't this just AGENTS.md / CLAUDE.md with extra steps?**

A flat instructions file — including Claude Code's `@imports`, which inline everything at session start — puts the whole thing in the window every session, and quality degrades as it grows. gcontext keeps the always-loaded part tiny (one line per module) and everything else behind links the agent follows on demand. The honest answer to "couldn't I hand-roll this with a docs/ folder?" is: yes, partially — gcontext is that convention made consistent and cheap. The tooling adds what a convention can't enforce: load/unload per task, the regenerated index, module kinds with different lifecycles, secrets declared by name and checked with `gcontext env`, and `gcontext validate` to catch broken links and missing files. And because it's a shared convention rather than your house style, the same workspace works identically across Claude Code, Cursor, and Codex.

**Is this the llms.txt web standard?**

Same filename, different job. The web proposal puts an index on public websites for crawlers. gcontext uses the same index *shape* inside your private repo, purely for your own agent at inference time. Nothing is published or exposed.

**Don't agents just ignore context files anyway?**

Instructions buried in a long monolithic prompt do decay — that's an argument *against* flat files, not against structure. You can't force a model to read anything; what you can do is keep the always-loaded part small and make the relevant file one link away, so it's read fresh at the moment the task touches it instead of sitting 50k tokens behind.

**What does this cost in tokens?**

The index is a few hundred tokens. Module detail enters the window only when navigated to. Unloaded modules: zero.

**Won't better models make this unnecessary?**

Better models still won't know your schema, your conventions, or the runbook you wrote last week. That knowledge has to live somewhere. gcontext's position is that it should live in git, where you can diff it, review it, and blame it.

## What gcontext is not

- **A vector database.** No embeddings. The agent navigates a file tree, not a similarity search.
- **A memory model.** No implicit memory. Context is explicit, human-curated, version-controlled.
- **A replacement for RAG.** Complementary. gcontext structures the knowledge RAG can retrieve from.
- **An agent framework.** No runtime. Works with the agent you already use.
- **Another orchestration layer.** No workflow engine. Just structured, navigable knowledge.

## Why the filesystem

> "Why not just use a vector database / memory layer?"

| | Filesystem (gcontext) | Vector DB / Memory |
|---|---|---|
| **Version control** | `git diff`, `git blame`, full history | Requires custom versioning |
| **Inspectability** | Open a folder, read the files | Query an API, decode embeddings |
| **Determinism** | Same files = same available context | Similarity search varies |
| **Human readability** | It's markdown | It's vectors |
| **Composability** | Load/unload modules like imports | Rebuild index on every change |
| **Tooling** | Works with every editor, CI, linter | Needs specialized tooling |
| **Portability** | Copy the folder | Export, migrate, re-index |

The filesystem is the most universal, inspectable, composable storage layer that exists. Your agent's context should be as maintainable as the code it operates on.

---

## Commands

| Command | What it does |
|---------|-------------|
| `gcontext init` | Create a new workspace (errors if one already exists) |
| `gcontext new <kind> <name> [summary]` | Scaffold a module |
| `gcontext load <name> [...]` | Activate modules in the workspace |
| `gcontext unload <name>` | Deactivate a module |
| `gcontext ls` | List all modules and their status |
| `gcontext env` | Check if required secrets are set |
| `gcontext validate [name]` | Verify module structure |

## Works with

gcontext produces plain markdown with a navigable index — any agent that reads files can use it. We use it daily with:

- **Claude Code** (via the generated `CLAUDE.md` → `AGENTS.md`)
- **Cursor**
- **Codex**
- **pi.dev**

## Secrets

Modules can declare required environment variables. Values go in `.env` (gitignored). Run `gcontext env` to check what's missing.

## Status

Current release: **v0.2.2** — early, small, and functional. The CLI surface (init, new, load/unload, ls, env, validate) is complete and covered by tests; the module format may still evolve before 1.0. The CLI is MIT and standalone. An optional hosted version with a web UI and built-in chat ([gcontext Cloud](https://gcontext.ai/how-it-works)) is in the works — the CLI does not depend on it.

---

Built by [Bleak AI](https://bleakai.com) | [gcontext.ai](https://gcontext.ai)
