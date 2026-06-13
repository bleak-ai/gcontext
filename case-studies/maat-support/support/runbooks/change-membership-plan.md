# Change Membership Plan

> Change a gym member's subscription plan (e.g. from a weekly plan to Unlimited).

## When to Use

- Ticket mentions "change plan", "upgrade", "downgrade", "switch to Unlimited"
- A specific member needs their plan changed to a different product/price

## Prerequisites

- Gym name (to find the gym ID in Firestore)
- Member name (to find the userId in Firestore)
- Target plan name (e.g. "Unlimited")

## Steps

### 1. Find the gym in Firestore

**Service:** Firestore
**Permission:** Read

Query the `gyms` collection by name. Note the gym ID.

### 2. Find the member in Firestore

**Service:** Firestore
**Permission:** Read

Search `gyms/{gymId}/members` and join with `users/{userId}` to match by name. Note the `userId` and current `membership.planName`.

### 3. Find the Stripe customer and subscription

**Service:** Firestore
**Permission:** Read

Read `gyms/{gymId}/customers/{userId}/subscriptions` to get the Stripe subscription ID. Use the `memberId` in subscription metadata to confirm which subscription belongs to this member (important for parent accounts with several children).

### 4. Find the target price in Stripe

**Service:** Stripe
**Permission:** Read

List active products/prices in Stripe. Find the target plan's price ID.

### 5. Update the Stripe subscription

**Service:** Stripe
**Permission:** Write

Update the subscription item to the new price:

```bash
source .env && stripe subscriptions update {subscription_id} \
  -d "items[0][id]={item_id}" \
  -d "items[0][price]={new_price_id}" \
  -d "metadata[planName]={new_plan_name}" \
  -d "metadata[sessionLimit]=" \
  -d "metadata[created_by]=support-agent" \
  --api-key "$STRIPE_API_KEY_RW" \
  --live
```

### 6. Verify Firestore sync

**Service:** Firestore
**Permission:** Read

Check that the webhook updated:
- `gyms/{gymId}/members/{userId}` -> `membership.planName` reflects the new plan
- `gyms/{gymId}/customers/{userId}/subscriptions/{docId}` -> `planName`, `amount`, `sessionLimit` reflect the new plan

If Firestore did not auto-sync (webhook delay or failure), correct it manually with a Firestore write.

## Common Variations

- **Parent account with several children:** use `memberId` in the Stripe subscription metadata to target the right subscription. Do not touch sibling subscriptions.
- **Upgrade vs downgrade:** same process. Stripe handles the proration.

## Notes

- Writes use the write key; reads use the read key.
- `sessionLimit` is empty/null for unlimited plans.
- Always verify Firestore sync after the Stripe update; the webhook should handle it, but confirm.
