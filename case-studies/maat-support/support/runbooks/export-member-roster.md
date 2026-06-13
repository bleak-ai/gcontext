# Export Member Roster

> Export all member names from a gym as a CSV for the gym owner to fill in data (e.g. class counts).

## When to Use

- A gym owner needs a list of all members to fill in information
- Ticket mentions "export", "member list", "roster", "template", or prep for adding class credits

## Prerequisites

- Gym name or ID

## Steps

### 1. Find the gym ID

**Service:** Firestore
**Permission:** Read

Query the `gyms` collection by name to find the gym document ID.

### 2. Export members with profiles

**Service:** Firestore
**Permission:** Read

- Query all docs from `gyms/{gymId}/members`
- For each member, join with `users/{userId}` to get `name` and `lastName`
- Filter out test accounts (names containing "test")
- Deduplicate by exact name + lastName match

### 3. Generate the CSV

**Service:** Local
**Permission:** N/A

Create a CSV with columns:
- `User ID` (the user document ID, needed for any follow-up import)
- `Name`
- `Last Name`
- `{Data Column}` (a blank column for the owner to fill in, e.g. "Classes to Add")

Sort alphabetically by last name.

## Common Variations

- The column to fill may vary: "Classes to Add", "Belt", etc.
- Some gyms have duplicate profiles; always deduplicate.

## Notes

- The User ID is essential for any follow-up import (e.g. the add-attendance-credits runbook).
- Always remove test accounts before exporting.
