# support

## Purpose
This module runs MAAT's day-to-day support operations: subscription problems, membership edits, data exports, and graduation fixes. It is the operational heart of the case study. Tickets come in from the team tracker (a `SUP-xx` queue in Linear), the agent consults a runbook, executes the fix through the [stripe](../stripe/llms.txt) and [firestore](../firestore/llms.txt) integrations, logs what it did, and turns any novel task into a new runbook.

Two child folders carry the reusable knowledge:

- [runbooks/](runbooks/llms.txt): one file per recurring task type. The agent reads the matching runbook before acting, and writes a new one after resolving a task it has not seen before.
- [logs/](logs/llms.txt): a record of every resolved task, organized by month. What changed, for which gym, when, and why.

## How a ticket gets resolved
A six-phase workflow keeps the agent steered and every write gated behind a human.

1. **Intake.** Read the ticket (id, title, description, priority, labels). Identify the gym (search Firestore to resolve it if needed) and the task type, then summarize it back for confirmation.
2. **Plan.** Read [runbooks/llms.txt](runbooks/llms.txt) and look for a matching runbook by task type. Read it fully and present its steps as the proposed plan. If no runbook matches, propose a step-by-step plan instead, naming the integration and read/write nature of each step. Read the integration descriptors ([stripe](../stripe/info.md), [firestore](../firestore/info.md)) to know the available operations. Wait for confirmation.
3. **Execute.** Run the plan step by step. Reads run immediately via the integration's PTC pattern. Writes follow the human-in-the-loop flow defined in the integration descriptor: gather context, construct the exact command/script, present what / command / impact, wait for approval, execute, report. Manual steps are described for the human and their result recorded.
4. **Log.** Write an execution log under [logs/](logs/llms.txt) capturing the gym, the operations performed, any human steps, and the outcome.
5. **Learn.** If the task type was new, create a runbook in [runbooks/](runbooks/llms.txt) with gym-specific values replaced by placeholders. If a runbook already existed, update it with any new variation or gotcha discovered.
6. **Close.** Add a user-facing resolution summary to the ticket and move it to Done. Both are writes, so present them for approval first.

## Integrations used
- [stripe](../stripe/llms.txt): subscriptions, refunds, and plan changes
- [firestore](../firestore/llms.txt): gyms, members, belt progress, subscriptions, attendance records

## Conventions
- Real gym data lives in **prod** (`maat-app-prod`). Treat every write as production unless a ticket says otherwise.
- Every write is presented for approval before running. Reads are auto-allowed.
- Generalize runbooks: replace gym IDs, emails, and amounts with `{placeholders}` so the next ticket of the same type reuses them.
