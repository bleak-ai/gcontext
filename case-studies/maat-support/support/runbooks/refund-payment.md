# Refund a Payment

> Issue a full or partial refund for a member or gym-owner payment via Stripe.

## When to Use

- A member was charged in error, or a gym owner requests a refund
- Keywords: "refund", "charge back", "overcharged", "cancel and refund"

## Prerequisites

- Who was charged and the member or customer name/email
- Full or partial refund, and the amount if partial

## Steps

### 1. Find the customer and charge (read)

**Service:** Stripe
**Permission:** Read

Look up the customer by email or name, then list their recent charges and identify the one to refund. Confirm the amount and date.

```python
import os
import stripe
from dotenv import load_dotenv

load_dotenv()
stripe.api_key = os.environ["STRIPE_API_KEY_RO"]

customer = stripe.Customer.list(email="owner@example.com", limit=1).data[0]
charge = stripe.Charge.list(customer=customer.id, limit=1).data[0]
print(f"Customer: {customer.name} ({customer.id})")
print(f"Last charge: {charge.id} - ${charge.amount/100:.2f}")
```

### 2. Present for approval

Show the human: **what** (who is refunded, how much), the **command**, and the **impact** (money returned to the original payment method).

### 3. Execute the refund (write)

**Service:** Stripe
**Permission:** Write

Full refund:

```bash
source .env && stripe refunds create \
  --charge {charge_id} \
  -d "metadata[created_by]=support-agent" \
  --api-key "$STRIPE_API_KEY_RW" \
  --live
```

Partial refund (amount in cents):

```bash
source .env && stripe refunds create \
  --charge {charge_id} \
  --amount 2500 \
  -d "metadata[created_by]=support-agent" \
  --api-key "$STRIPE_API_KEY_RW" \
  --live
```

### 4. Report

Confirm the refund ID and amount, and note it on the ticket.

## Common Variations

- **Partial refund:** pass `--amount` in cents (`2500` = $25.00).

## Notes

- Refunds go back to the original payment method; there is no way to redirect them.
- Tag every refund with `metadata[created_by]=support-agent` for the audit trail.
- A refund does not cancel a subscription; cancel separately if the ticket asks for it.
