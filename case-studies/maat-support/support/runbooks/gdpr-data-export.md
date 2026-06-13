# GDPR Data Export

> Export all personal data associated with a user for GDPR Article 15 (Right of Access) compliance.

## When to Use

- A user requests a copy of all their personal data
- Keywords: "GDPR", "data export", "right of access", "personal data", "SAR", "subject access request"

## Prerequisites

- Account ID (the auth UID)
- User ID (the user profile ID)

## Steps

### 1. Extract account data

**Service:** Firestore (prod)
**Permission:** Read

Fetch `accounts/{accountId}` (email, phone, billing details, Stripe customer ID) and its subcollections (known gyms, payment methods, device tokens).

### 2. Extract the user profile

**Service:** Firestore (prod)
**Permission:** Read

Fetch `users/{userId}` (name, lastName, beltGrade). The `account` field references `accounts/{accountId}`.

### 3. For each gym, extract membership and billing

**Service:** Firestore (prod)
**Permission:** Read

For each gym the user belongs to:
- `gyms/{gymId}/members/{userId}` — membership status, join date, last attended date
- `gyms/{gymId}/members/{userId}/belts` — belt progress, classes attended
- `gyms/{gymId}/customers/{userId}/subscriptions` — plans, amounts, status

### 4. Extract attendance

**Service:** Firestore (prod)
**Permission:** Read

Fetch the user's attendance records from `gyms/{gymId}/members/{userId}/attendance`.

### 5. Compile and sanitize the export

Output a single JSON file `gdpr-export-{accountId}.json` grouped by category. Sanitization rules:
- Do not include internal storage paths or document references that expose the database structure.
- Remove any field that leaks another user's personal data (e.g. instructor emails on a class record).
- Keep fields that belong to the data subject.

### 6. Deliver the export

Share the JSON file with the requester through the appropriate channel.

## Categories Checklist

| Category | Source | Key Fields |
|---|---|---|
| Account Information | `accounts/{accountId}` | email, phone, billing |
| Known Gyms | account subcollection | gym names, membership status |
| Payment Methods | account subcollection | card brand, last4, expiry |
| User Profile | `users/{userId}` | name, belt grade |
| Gym Membership | `gyms/{gymId}/members/{userId}` | join date, status, plan |
| Belt Progress | member `belts` subcollection | belt, classes attended |
| Subscriptions | `gyms/{gymId}/customers/{userId}/subscriptions` | plan, amount, status |
| Attendance | member `attendance` subcollection | class history |

## Notes

- Always run against **prod**; this is real user data.
- The member document is keyed by `userId`, not `accountId`.
