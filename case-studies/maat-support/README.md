# Case study: MAAT support

This is the gcontext workspace behind the "Why we built it" story in the main [README](../../README.md). We run [MAAT](https://maatapp.com), membership software for martial arts gyms, on Stripe and Firestore. As we grew, support work piled up: subscription problems, membership edits, data exports. This workspace is how the agent handles it.

It is the same tree shown in the diagram on the main README: a root `llms.txt` routes to the right module, and each module carries the notes and keys for one domain.

```
maat-support/
  llms.txt            root router, points at the three modules
  stripe/             llms.txt, info.md, module.yaml (keys named in module.yaml)
  firestore/          llms.txt, info.md, module.yaml
  support/            llms.txt, info.md
    runbooks/         one file per recurring support task
    logs/             one file per month of resolved tasks
```

## How to read it

1. Start at [llms.txt](llms.txt). It routes to `stripe`, `firestore`, and `support`.
2. The two integrations ([stripe](stripe/info.md), [firestore](firestore/info.md)) each hold the business context, auth (secret names only), operations, and code patterns for one service. The values stay in a gitignored `.env`; only the variable names appear in the files.
3. [support](support/info.md) is the operation built on top. Its `info.md` describes the six-phase workflow for resolving a ticket. It expands into:
   - [runbooks/](support/runbooks/llms.txt): the reusable procedures the agent consults before acting, and writes after solving a new kind of task.
   - [logs/](support/logs/llms.txt): the record of every resolved task, what changed, for which gym, and why.

The point of the tree is that the agent is steered one link at a time to exactly the right place: the integration descriptor for how to call the API, the runbook for the steps, the logs for what was done before. Every write is gated behind a human approval.

> This is a read-only, anonymized case study, not a runnable workspace. The gyms, members, IDs, and the Firestore schema are fictional examples; what is real is the shape of how MAAT uses gcontext to run support. No keys, real customer data, or production internals are included.
