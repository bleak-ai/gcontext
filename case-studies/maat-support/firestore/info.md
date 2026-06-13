# firestore

## Purpose
Firestore is MAAT's primary database. It stores all gym, member, class, and operational data across dev and prod. The agent reads it to resolve gyms and members for a ticket, and (with human approval) writes membership, belt-progress, and subscription corrections.

> The collections and fields below are an illustrative model for this case study, not MAAT's production schema.

## Where it lives
GCP Cloud Firestore, accessed through the `google-cloud-firestore` Python SDK with an explicit service account.

- **Dev (default):** project `maat-app-dev`, staging/test data, safe for experimentation
- **Prod:** project `maat-app-prod`, live gym data, use with caution

## Auth & access
<!-- The project ID and service account JSON are declared by name in module.yaml and loaded from the gitignored .env; not repeated here. -->
Two values live in the gitignored `.env` and are declared by name in `module.yaml`: the GCP project ID (dev or prod) and a service account JSON credential. The service account JSON is held as a string secret and parsed inline, never written to disk.

## Key entities
- **Root collections:** `gyms`, `accounts`, `users`, `events`
- **Gym subcollections:** `members`, `class_templates`, `class_sessions`, `belt_system`, `gym_config`
- **Member belt progress:** `gyms/{gymId}/members/{userId}/belts/{belt}`

Member lookup pattern: `gyms/{gymId}/members/{userId}` holds membership info (`joinDate`, `membership`, `lastAttendedDate`), while the profile data (`name`, `lastName`, `beltGrade`) lives in `users/{userId}`. Join the two when listing members with details. The real email and phone live on the linked account: `users/{userId}.account` is a reference to `accounts/{accountId}`, which holds `primaryEmail` and `primaryPhone`.

## Operations

Read (auto-allowed, via PTC): get document, list/query/count a collection, read subcollections, list subcollection names.

Write (requires human confirmation): set, update, add, and batch writes.

Blocked (never): deleting documents, collections, or fields; modifying security rules or indexes; any administrative operation.

For every write the agent follows a human-in-the-loop flow: gather context with reads, build the script with all parameters, present **what** changes / the **script** / the **impact**, wait for explicit approval, then execute and report.

## Examples

Read: list all gyms.

```python
import json
import os
from google.cloud import firestore
from google.oauth2 import service_account
from dotenv import load_dotenv

load_dotenv()

creds = service_account.Credentials.from_service_account_info(
    json.loads(os.environ["FS_SECRET"])
)
db = firestore.Client(
    project=os.environ["FS_KEY"],
    credentials=creds,
)

count = 0
for doc in db.collection("gyms").stream():
    data = doc.to_dict()
    print(f"Gym: {data.get('name', 'N/A')} (ID: {doc.id})")
    count += 1

print(f"\nTotal gyms: {count}")
```

Notes:
- Never hardcode credentials. Always parse the service account JSON with `json.loads` and pass the project ID from the environment.
- Use `stream()` for listing and `.limit()` for large collections.
- Document references use path format `collection/doc_id/subcollection/doc_id`.
- Print human-readable output, not raw JSON, unless asked.
