# Fix Plan Sync

> Fix Firestore membership data that is out of sync after a subscription change in Stripe.

## When to Use

- Ticket mentions "upgrade not reflected", "app shows old plan", "session limit wrong after upgrade"
- A member changed plans but Firestore still shows the old plan name or session limit
- Usually caused by a webhook sync failure during the plan change

## Prerequisites

- Gym name (to find the gym ID in Firestore)
- Member name(s) (to find the userId in Firestore)

## Steps

### 1. Find the gym in Firestore

**Service:** Firestore
**Permission:** Read

Query the `gyms` collection by name. Note the `gymId`.

### 2. Find affected members in Firestore

**Service:** Firestore
**Permission:** Read

For each member, search `gyms/{gymId}/members` joined with `users/{userId}` to match by name. Note `userId`, `membership.planName`, and any session-limit field.

### 3. Read Firestore subscription docs

**Service:** Firestore
**Permission:** Read

Read `gyms/{gymId}/customers/{userId}/subscriptions` for each member. Note `planName`, `sessionLimit`, `amount`, and the Stripe subscription ID.

### 4. Check the actual Stripe subscriptions

**Service:** Stripe
**Permission:** Read

For each member's subscription, retrieve it from Stripe. Get the product name, price amount, and any `sessionLimit` in price metadata (absent means unlimited).

### 5. Compare and identify mismatches

Present a comparison table:

| Member | Stripe Product/Price | Firestore Plan | Firestore Session Limit | Mismatch? |

Focus on mismatches where `sessionLimit` blocks booking incorrectly.

### 6. Update Firestore membership and subscription docs (write)

**Service:** Firestore
**Permission:** Write

For each mismatch:
- `gyms/{gymId}/members/{userId}` -> set `membership.planName` to match the Stripe product
- `gyms/{gymId}/customers/{userId}/subscriptions/{docId}` -> set `planName`, `sessionLimit` (null for unlimited), `amount`

### 7. Update Stripe subscription metadata (write)

**Service:** Stripe
**Permission:** Write

Update metadata to match:

```python
stripe.Subscription.modify(
    "{subscription_id}",
    metadata={"planName": "{new_plan_name}", "sessionLimit": ""},
)
```

### 8. Verify

**Service:** Firestore
**Permission:** Read

Re-read the updated documents and confirm all fields match the Stripe subscription.

## Common Variations

- **Partial sync:** if some fields synced and others did not, fix only the mismatched fields.
- **Cosmetic-only mismatch:** if the plan name and session limit are correct but `amount` is off, this is lower priority and may be deferred.

## Notes

- `sessionLimit` controls booking limits; it is the critical field to get right.
- Writes use the write key; reads use the read key.
