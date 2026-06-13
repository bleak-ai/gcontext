# stripe

## Purpose
Stripe handles payment processing for MAAT: member subscriptions and gym-owner billing. The agent reads subscriptions, customers, invoices, and charges to diagnose support tickets, and (with human approval) issues refunds and subscription changes.

> Identifiers like `cus_…` and `sub_…` in this case study are fictional examples, not real MAAT data.

## Where it lives
Stripe, accessed through the official `stripe` Python SDK (reads) and the Stripe CLI (writes).

## Auth & access
<!-- The Stripe keys are declared by name in module.yaml and loaded from the gitignored .env; not repeated here. -->
The keys live in the gitignored `.env` and are declared by name in `module.yaml`: a read key for queries and a write key for changes. Reads always use the read key; writes always go through the CLI with the write key, so a generated read script can never perform a write even if the code is wrong.

## Key entities
- **Customer**: a gym member or gym owner. Member subscriptions carry a `memberId` in metadata linking back to the MAAT member.
- **Subscription**: a member's active plan.
- **Charge / Invoice / Refund**: payment records and reversals.

## Operations

Read (auto-allowed, via PTC): list/get subscriptions, customers, invoices, charges, payment methods, products/prices; get balance.

Write (requires human confirmation, via the CLI): create refund, update subscription, cancel subscription, create a manual invoice.

Blocked (never): deleting customers or subscription data, modifying API keys or webhooks, transferring funds.

For every write the agent follows a human-in-the-loop flow: gather context with reads, construct the exact CLI command, present **what** changes / the **command** / the **impact**, wait for explicit approval, then execute and report.

## Examples

Read: count active subscribers.

```python
import os
import stripe
from dotenv import load_dotenv

load_dotenv()
stripe.api_key = os.environ["STRIPE_API_KEY_RO"]

count = 0
for sub in stripe.Subscription.list(status="active").auto_paging_iter():
    count += 1

print(f"Active subscribers: {count}")
```

Write: refund a charge (after approval).

```bash
source .env && stripe refunds create \
  --charge ch_DemoCharge001 \
  -d "metadata[created_by]=support-agent" \
  --api-key "$STRIPE_API_KEY_RW" \
  --live
```

Notes:
- Handle pagination with `auto_paging_iter()` on list operations; never assume the first page is complete.
- Financial amounts are in cents (`5900` is $59.00); divide by 100 for display.
- Always pass `--live` on writes (the CLI defaults to test mode) and tag writes with `metadata[created_by]` for an audit trail.
