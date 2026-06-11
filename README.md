# gcontext

**Version-controlled context modules your AI agent navigates itself.**

[![PyPI](https://img.shields.io/pypi/v/gcontext-ai)](https://pypi.org/project/gcontext-ai/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/pypi/pyversions/gcontext-ai)](https://pypi.org/project/gcontext-ai/)

Your agent's knowledge and its working state as plain markdown in git: modular, reviewable, loaded per task. No embeddings, no memory layer, no new runtime. Works with Claude Code, Cursor, Codex — anything that reads files.

Modules don't just *describe* your stack — they carry the credentials and the know-how for the agent to **act** on it: query the database, hit the Stripe API, run the deploy.

And work in flight survives the session: start a migration today, get blocked waiting on an email, come back Thursday and say "continue". The agent kept track of where things stand, so you don't have to.

![gcontext demo](demo/gcontext-real-demo.gif)

*A real session, replayed: one prompt builds a Supabase integration, then a fresh session answers "how many users do we have?" with the live number. [Unedited transcript](https://gcontext.ai/first-session.html) · [Do it yourself in three copy-pastes](examples/first-integration.md)*

---

## The problem

AI agents fail for the same reason large codebases fail: **implicit state.**

Prompts become undocumented architecture. Instructions drift between conversations. Context duplicates across files. Every session starts with "let me remind you how our deploy works."

And the most implicit state of all is the work in flight. The migration you started Monday, the blocker you're waiting on, the decision you made last week: none of it survives the session. The agent forgets, so you keep track, and every conversation starts with a re-briefing.

This isn't a model problem. It's an engineering problem.

Most teams solve it by writing longer prompts, pasting more docs, or hoping the agent remembers. That works until it doesn't, and it stops working fast.

**gcontext treats context as infrastructure.**

---

## Before and after

**Without structured context:**

- Giant system prompts nobody maintains
- Copy-pasted docs that go stale
- "Remember, our Stripe webhook is at..." every session
- You're the project manager for your agent: re-briefing it on where every piece of work stands, every session
- Agent hallucinates because it can't find what it needs
- Context bloat kills quality on long tasks
- Tribal knowledge lives in one person's prompt history

**With gcontext:**

```
modules-repo/
  stripe/            → API keys, webhooks, how to query invoices
  postgres/          → schema, migrations, connection details
  deploy-pipeline/   → step-by-step release to production
  migrate-to-paddle/ → task: where it stands, what's blocked, what's next
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

That's the whole footprint: no account, no server, no vector database. Your keys stay in your local `.env`; modules are just files in your repo.

## Quick start

`gcontext init` is the only command you have to run. After that, your agent operates the workspace itself — it can create modules, fill them in, and load them, because the workspace tells it how.

**1. Initialize**

```bash
$ gcontext init

Created modules-repo/
Created context/

Now open your agent (Claude Code, Cursor, ...) and say:

    Set up gcontext for this project.

It will ask what you keep re-explaining and what you're working on,
then create and load your first modules.
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

**2. Say the setup prompt**

On a fresh workspace, "Set up gcontext for this project" makes the agent interview you — *what do you re-explain every session? what does it always get wrong? what are you in the middle of right now?* — and turn your answers into your first modules: usually an integration for the stack and a task for the work in flight. You never pick a module kind or learn the taxonomy first; the agent handles that and shows you the diff.

You can also just ask for what you need directly: "Add a supabase integration, the keys are in .env." The exact prompt we test against a real model is in the [first-integration walkthrough](examples/first-integration.md); the agent creates the module (`info.md` with the API know-how, `llms.txt` as the index, `module.yaml` declaring the secret by name only) and loads it.

**3. Provide the secret it needs**

```bash
echo "PG_URL=postgres://..." >> .env    # gitignored; only the *name* is in the module
```

Use read-only credentials where you can, and review what the agent writes into a module before committing — it documents what it sees.

**4. Ask it to do real work — it queries production itself**

Open a fresh session, one that has never seen your project, and ask: "How many users do we have?" In [the recorded session](https://gcontext.ai/first-session.html) the agent follows the index to the integration module, calls the API with the key from `.env`, and answers with the live row count, which the test then verifies against the database independently. No MCP server, no tool definitions; the module was enough.

**5. Hand it the work in flight**

```
$ claude → "We're migrating auth to OAuth. Track it as a task."

Creating modules-repo/oauth-migration/
  brief.md       ← the goal and the plan
  status.md      ← progress, blockers, what's next
```

From now on the task survives the session. Days later, in a fresh conversation, "continue the oauth migration" is all the briefing the agent needs.

**See it run, for real.** The GIF at the top is a replay of a recorded session, and [the full unedited transcript](https://gcontext.ai/first-session.html) is public: every tool call, the module files the agent wrote, and the final answer verified against the live API. The walkthrough prompt is extracted from [examples/first-integration.md](examples/first-integration.md) and run against a real model before releases; if the quick start stops working, the release does not ship.

Prefer doing things by hand? Every step is also a deterministic command — `gcontext new`, `gcontext load`, `gcontext ls`, `gcontext validate`. See [Commands](#commands). The agent uses the same files either way.

---

## Your agent doesn't just know your stack. It operates it.

An integration module is three things: what the service is (`info.md`), how to navigate it (`llms.txt`), and which secret it needs (`module.yaml`, name only). That turns out to be everything an agent needs to make real calls — no MCP server, no tool definitions, no plugin to install.

```
$ claude → "Refund the duplicate charge for customer@acme.com"

Reads stripe/info.md → knows refunds need the charge id, not the intent
Looks up the customer, finds two charges 41s apart
Refunds ch_3Oa2... ($49.00) — refund re_3Oa2... succeeded
```

MCP gives agents tools; for most of your stack, a markdown file plus an env var does the same job — and you can `git diff` it. The same module that explains your Stripe setup is the one that lets the agent act on it, and what it learns doing the work gets written back into the module. (The exchange above is illustrative; for a real one, unedited, see [the recorded session](https://gcontext.ai/first-session.html).)

---

## Walk away mid-task. Come back days later.

The other half of the problem isn't knowledge, it's state. Real work gets interrupted: you wait on an email, a review, another team. Without gcontext, you re-brief the agent from scratch every time, and you keep the real status in your head. With a task module, the agent writes down where things stand as it works.

```
Monday    $ claude → "Start the Stripe-to-Paddle migration"

          Creates modules-repo/paddle-migration/ (a task module)
          Maps price ids, exports products... blocked: Paddle support
          must enable the sandbox. Writes the blocker to status.md.

Thursday  $ claude → "Any movement on the migration?"

          Reads paddle-migration/status.md
          "Blocked on Paddle support since Monday (ticket #4821).
           Price mapping is done. Next: webhook rewrite, once
           sandbox access lands."
```

No re-briefing, no scrolling back through old chats, and the status was never in your head to begin with. The task module is the state: what's done, what's blocked, what's next. When the work ships, the task is done with its job: delete it, or keep it as the record of what happened.

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

You won't need `unload` for a while: with fewer than ~10 modules, keep everything loaded — the resident index costs about one line per module. Load/unload starts paying off when modules outnumber what fits comfortably.

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

Two kinds carry a workspace: what your agent **knows**, and what it's **working on**.

| Kind | What it captures | Lifecycle | Example |
|------|-----------------|-----------|---------|
| **Integration** | How to use an external service, API, or database | Permanent: lives as long as the service does | Stripe, Postgres, GitHub, Slack |
| **Task** | A bounded piece of work and where it stands | Disposable: done when the work is done | Fix billing bug, migrate auth, ship feature X |

Different shapes for different lifecycles. They coexist and compose. You never have to pick one — the agent chooses a kind when it creates a module; this table is for reading what it made.

---

## What a workspace looks like

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
  escalation/        → when and how to escalate
```

An agent triaging tickets reads the Zendesk integration, checks Stripe for billing context, references the KB, and follows escalation rules — without a 10,000-token system prompt.

**Claude Code / Cursor setup**

```
modules-repo/
  codebase/          → architecture, conventions, key paths
  cloudflare/        → DNS, workers, deployment targets
  monitoring/        → Grafana dashboards, alert rules
  ship-v2-auth/      → task: migrate auth with progress tracking
```

Point your coding agent at the workspace. It navigates to the module it needs per task: your conventions when writing code, your deploy integration when shipping, your monitoring setup when debugging production.

---

## Onboarding your team

A colleague joining an existing workspace is the easiest path into gcontext — there is nothing to set up and nothing to learn:

```bash
git clone <your-repo> && cd <your-repo>
cp .env.example .env    # if present — fill in your own credentials (gcontext env shows what's missing)
claude                  # or cursor, codex — the workspace tells the agent the rest
```

Their agent reads the same modules yours does: the schema notes, the deploy runbook, the gotchas your team already paid to learn. Your new hire's agent knows the codebase before they do.

Nobody hand-maintains this. The agent updates modules as a side effect of doing work — it fixed a deploy quirk, it writes the quirk down — and the humans review the diffs in PRs like any other change. If a module goes stale, `git blame` tells you when and why.

---

## FAQ

**Isn't this just AGENTS.md / CLAUDE.md with extra steps?**

A flat instructions file — including Claude Code's `@imports`, which inline everything at session start — puts the whole thing in the window every session, and quality degrades as it grows. gcontext keeps the always-loaded part tiny (one line per module) and everything else behind links the agent follows on demand. The honest answer to "couldn't I hand-roll this with a docs/ folder?" is: yes, partially — gcontext is that convention made consistent and cheap. The tooling adds what a convention can't enforce: load/unload per task, the regenerated index, module kinds with different lifecycles, secrets declared by name and checked with `gcontext env`, and `gcontext validate` to catch broken links and missing files. And because it's a shared convention rather than your house style, the same workspace works identically across Claude Code, Cursor, and Codex.

**Is this the llms.txt web standard?**

Same filename, different job. The web proposal puts an index on public websites for crawlers. gcontext uses the same index *shape* inside your private repo, purely for your own agent at inference time. Nothing is published or exposed.

**Don't agents just ignore context files anyway?**

Instructions buried in a long monolithic prompt do decay — that's an argument *against* flat files, not against structure. You can't force a model to read anything; what you can do is keep the always-loaded part small and make the relevant file one link away, so it's read fresh at the moment the task touches it instead of sitting 50k tokens behind.

**Isn't maintaining a folder of markdown a chore? Wikis die this way.**

Wikis die because humans must maintain them on the side. Here the agent maintains the modules as a side effect of doing work — when a session surfaces a gotcha or a changed endpoint, it updates the module then and there — and the human's job shrinks to reviewing diffs. That review step is the point: it's the same control you already have over code the agent writes.

**What does this cost in tokens?**

The index is a few hundred tokens. Module detail enters the window only when navigated to. Unloaded modules: zero.

**Won't better models make this unnecessary?**

Better models still won't know your schema, your conventions, or the runbook you wrote last week. That knowledge has to live somewhere. gcontext's position is that it should live in git, where you can diff it, review it, and blame it.

## What gcontext is not

- **A vector database.** No embeddings. The agent navigates a file tree, not a similarity search.
- **A memory model.** No implicit memory. Context is explicit, human-curated, version-controlled.
- **A replacement for RAG.** Complementary. gcontext structures the knowledge RAG can retrieve from.
- **An agent framework.** No runtime. Works with the agent you already use.
- **Another orchestration layer.** No pipelines, no runtime. Just structured, navigable knowledge.

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
