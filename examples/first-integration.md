# Your first integration: from `gcontext init` to your agent answering real questions

This walkthrough is three copy-pastes: one command, two lines in `.env`, and one prompt. At the end you have a Supabase integration module your agent built itself, and a fresh session that answers "how many users do we have?" with the real number from your database. You need nothing but Python, the gcontext CLI, and a key in `.env`: no account, no vector database, no MCP server.

Supabase is the worked example; the pattern is the same for any service with an HTTP API.

## Step 1: initialize the workspace

```bash
gcontext init
```

This is the only command you have to run; after it, your agent operates the workspace itself. It creates:

```
AGENTS.md            # auto-loaded by your agent; points it at context/system.md
CLAUDE.md            # one line: @AGENTS.md (Claude Code reads this file)
context/             # what the agent reads: generated llms.txt index + symlinks to loaded modules
modules-repo/        # source of truth: your modules (seeded with an example/)
.gitignore           # ignores .env
```

Re-running `gcontext init` in an existing workspace errors out; it never overwrites your files.

## Step 2: put your keys in .env

From your Supabase project settings, grab the project URL and a secret API key, and add them to `.env` in the workspace:

```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SECRET_KEY=sb_secret_...
```

Only the *names* `SUPABASE_URL` and `SUPABASE_SECRET_KEY` will ever appear in module files; the values stay in the gitignored `.env`. Where a service offers scoped or read-only credentials, prefer those: give the agent the least privilege the job needs.

## Step 3: say the prompt

Open your agent (Claude Code, Cursor, Codex) in the workspace and paste this:

<!-- tested-prompt: create-integration -->
```
Create a supabase integration module for our Supabase project and load it
into the workspace. The project URL and a secret API key are already in
.env as SUPABASE_URL and SUPABASE_SECRET_KEY. Declare both by name in
module.yaml and NEVER copy their values into any module file. In info.md,
document how to call the Supabase REST API (PostgREST) with those
variables: base path /rest/v1/, the apikey and Authorization headers, and
an example table query.
```

The agent does the rest: it creates `modules-repo/supabase/` with the three files an integration is made of (`info.md` with the API know-how, `llms.txt` as the navigation index, `module.yaml` declaring the two secret names), and loads the module so it shows up in `context/`.

## Step 4: how you know it worked

Don't take the agent's word for it. Every check is a deterministic command:

- `gcontext ls` lists `supabase` as loaded.
- `gcontext validate supabase` passes.
- `gcontext env` shows `SUPABASE_URL` and `SUPABASE_SECRET_KEY` as set.
- `modules-repo/supabase/module.yaml` declares the secret *names* only, no values.
- Search the module folder for your actual key value: you find nothing.

If any of these fail, tell the agent which one; the workspace conventions it read are enough for it to fix its own work.

## Step 5: use it

Open a fresh session (new conversation, empty context) and ask a real question:

```
How many users do we have?
```

The fresh agent has never seen your project. It follows the index to `supabase/info.md`, calls the REST API with the key from `.env`, and answers with the real row count. That's the point of an integration module: it carries enough know-how that any future session can act on your stack, not just talk about it.

## Any service works like this

The pattern doesn't care which API sits behind the key. One line in `.env` (say `LINEAR_API_KEY`), the same prompt shape ("create a linear integration module, the key is in .env as LINEAR_API_KEY, document the GraphQL endpoint in info.md"), and your agent queries Linear issues the same way.

## This walkthrough is tested

The prompt in step 3 is not aspirational: our test suite extracts it from this exact file, runs it against a real model in a fresh workspace before releases, and then verifies the module and the final answer deterministically (validate passes, secrets declared by name, no key value leaked, the user count matches an independent API call). If the prompt stops working, the release fails.

Want to see it run? [A real, unedited session](../demo/first-session.html) shows the full transcript, and a terminal recording of the same flow lives in [demo/](../demo/).
