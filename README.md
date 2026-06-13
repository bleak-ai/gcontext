# Gcontext

**Context Magament System**

[![PyPI](https://img.shields.io/pypi/v/gcontext-ai)](https://pypi.org/project/gcontext-ai/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/pypi/pyversions/gcontext-ai)](https://pypi.org/project/gcontext-ai/)

The main concept is a tree of llms.txt that references either folders or files. The goal is to load in a conversation with an AI agent the right information at every time, and from this, be able to grow the context that the agent has access to and create a something analogous to a "Live Memory" or Live Record of things. 

### What is the difference from Claude Code Memory system? 

The problem is the same, but Gcontext is for users that want to treat the Context as a problem on it's own, while Memory handles everything behind the scenes, Gcontext allows the user to define how Context should be defined and be much more precise in which are the steps that an AI agent does.


![How an agent navigates a gcontext workspace: a root llms.txt routes to stripe, firestore and support modules, each with its own llms.txt, notes and keys; the support module expands into per-task runbooks and daily logs](demo/gcontext-tree.png)


## How to use it

**1. Install and create the workspace.**

```bash
curl -LsSf https://gcontext.ai/gcontext/install.sh | sh   # or: uv tool install gcontext-ai
gcontext init
```

**2. Ask your agent to build a module.** Open your agent in the workspace and name the integration you want:

```
Create a supabase integration module and load it.
```

The agent writes `info.md`, an `llms.txt` index, and a `module.yaml` that declares which secrets it needs by name only (the values never leave `.env`).

**3. Fill in the secrets it asks for.** The module tells you which variables to set; put them in `.env`:

```bash
SUPABASE_URL=https://....supabase.co
SUPABASE_SECRET_KEY=...
```

**4. Enrich the module with real data.** Now that the access is in place, ask the agent to explore the live service and write down what it finds:

```
Look in supabase and update the module information with real read requests.
```

From then on a fresh session can answer questions ("how many rows are in the members table?") by following the index to the module and calling the API with the key from `.env`.

![gcontext demo](demo/gcontext-real-demo.gif)

### Adding more integrations

Repeat step 2 for each new service, and a tree starts to form: a root `llms.txt` routing to one module per integration, each declaring its own keys. Just ask:

```
Create a stripe integration module and load it.
```

The more integrations you add, the more the workspace becomes a single place that coordinates access to all of them, which is exactly when gcontext pays off.

## When to use it

This is not for everyone. If you work in a project where the only external dependency is a database, it probably doesn't make sense to set all of this up just for this. But as more external dependencies and integrations you are using, it makes more sense to have a dedicated central place where to coordinate the access to all of these.

## Case study

This project has been developed at the startup [MAAT](https://maatapp.com), Management Software for Martial Arts Gyms, where the product is built on top of a payment System and a DB. As we got more gyms we had to spend more and more time resolving support tasks where all of these integrations were affected. We came up with the pattern that gcontext follows with the llms.txt to speed up our day to day.

### Our Journey solving Support Tasks
1. **Before AI.** We had some playbooks on how to resolve the Support Tasks and we used them to solve the tasks manually
2. **With AI - Mainly CLAUDE.md.** We explained in the Claude.md how our system works and which were the most common causes of problems, it gave us most of the times the right indications, but often we still had to do manual work and exploration for many tasks, still repetitive as we didn't had a place to store the runbooks.
3. **With AI + GContext** This allowed us to intertwine completely the AI in our processes. When we do now an exploration for a task, we can save this exploration in a md file, referenced by an llms.txt and the AI model will be able to find it later. 

You can browse an example of it here: [`case-studies/maat-support/`](case-studies/maat-support/). It is the tree from the diagram above: a root `llms.txt` router over the `stripe` and `firestore` integration modules, plus a `support` module with its runbooks and execution logs.

## Commands

Run these with the CLI:

| Command | What it does |
|---------|-------------|
| `gcontext init` | Create a new workspace |
| `gcontext load <name> [...]` | Activate modules in the workspace |
| `gcontext unload <name>` | Deactivate a module |
| `gcontext env` | Check required secrets are set |
| `gcontext validate [name]` | Verify module structure |

The rest the agent does for you from plain language, just ask:

| Just ask the agent | Equivalent CLI |
|---------|-------------|
| "Create a supabase integration module" | `gcontext new <kind> <name> [summary]` |
| "Which modules do we have?" | `gcontext ls` |

---

Built by [Bleak AI](https://bleakai.com) | [gcontext.ai](https://gcontext.ai)
