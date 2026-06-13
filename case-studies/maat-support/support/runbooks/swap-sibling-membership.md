# Swap Sibling Membership

> Transfer an active subscription from one sibling to another under the same parent account.

## When to Use

A gym asks that one sibling's active membership be moved to another sibling. Both children share the same parent account and Stripe customer.

## Key Concepts

- Siblings share a parent `account` document in Firestore, which holds a single `stripeCustomerId`.
- Stripe subscriptions carry a `memberId` in metadata that links to the correct MAAT member.
- Swapping the `memberId` on the subscription is enough: the backend picks up the change and updates the new member's Firestore membership automatically.

## Steps

1. **Find the gym** — query the `gyms` collection by name to get the gym ID.
2. **Find both siblings** — search `gyms/{gymId}/members` and join with `users/{userId}` to find both by name.
3. **Identify the parent account** — follow the `account` reference on either user document to get the `stripeCustomerId`.
4. **Find the subscription in Stripe** — look up the customer's subscriptions. Match by `memberId` in metadata to identify which subscription belongs to which sibling.
5. **Swap memberId in Stripe (write)** — update the subscription metadata `memberId` from the old sibling to the new sibling's userId.
6. **Update Firestore membership (write)** — set the old sibling's `membership.status` to `canceled` in `gyms/{gymId}/members/{userId}`.
7. **Verify** — the new sibling's Firestore membership should update to active automatically. Confirm both profiles show the correct status.

## Firestore Paths

| Data | Path |
|------|------|
| Gym | `gyms/{gymId}` |
| Member | `gyms/{gymId}/members/{userId}` |
| User profile | `users/{userId}` |
| Parent account | `accounts/{accountId}` (via the user's `account` reference) |

## Worked Example (fictional)

Gym **Northgate Martial Arts** (`northgate_martial_arts`), parent account for **Sarah Carter** (`sarah.carter@example.com`), Stripe customer `cus_DemoNorthgate01`.

- **Leo Carter** (`member_leo_carter`) is inactive.
- **Mia Carter** (`member_mia_carter`) has the active "Kids Once Weekly" subscription `sub_DemoNorthgate01`.

To move the membership to Leo: update `sub_DemoNorthgate01` metadata `memberId` from `member_mia_carter` to `member_leo_carter`, then set Mia's Firestore membership to canceled.

## Notes

- The parent email in the ticket may not match exactly; always verify via Firestore.
- Identify children by name, not email (child profiles use their userId as the email key).
- Changing `memberId` in Stripe updates the new sibling's Firestore membership automatically, but the old sibling's membership must be canceled manually.
