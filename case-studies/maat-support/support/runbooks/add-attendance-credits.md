# Add Attendance Credits

> Add attendance credits to multiple members by creating attendance records.

## When to Use

- A gym owner provides a list of members with class counts to add
- Ticket mentions "add classes", "attendance credits", "bulk" attendance

## Prerequisites

- Gym ID
- A list of members with userIds and the number of classes to add (typically from an export CSV the gym owner filled in)

## Critical Rule

**Never write the belt counter directly.** Each member's belt progress (`gyms/{gymId}/members/{userId}/belts/{belt}.classesAttended`) is derived from their attendance records. Always add attendance records and let the count follow; writing the counter directly causes the classes to be missing from the member's attendance history and risks double-counting later.

## Steps

### 1. Match members to profiles

**Service:** Firestore
**Permission:** Read

If the input is a name list (not userIds), match names against `gyms/{gymId}/members` joined with `users/{userId}`. Use accent-insensitive, case-insensitive matching. Report any unmatched names.

### 2. Read current belt progress

**Service:** Firestore
**Permission:** Read

For each member, read their current belt from `users/{userId}.beltGrade` and `classesAttended` from `gyms/{gymId}/members/{userId}/belts/{belt}`. Present a dry-run table: Name, Belt, Current, To Add, New Total. Flag members without a belt configured.

### 3. Create attendance records

**Service:** Firestore
**Permission:** Write

For each member, create N attendance records under:

```
gyms/{gymId}/members/{userId}/attendance/{recordId}
```

Each record carries the class date, class name, and the member's belt at the time. Batch writes in groups of 500 (the Firestore limit). The member's `classesAttended` updates from these records.

### 4. Verify

**Service:** Firestore
**Permission:** Read

Re-read each member's belt progress and confirm `classesAttended >= expected`.

## Common Variations

- Input may arrive as a filled CSV (from the export-member-roster runbook) or as a plain list in the ticket.
- Some members may have no belt configured yet; create the attendance records anyway and set up the belt document if needed.
- If a previous attempt wrote the counter directly, reconcile first so the totals are not double-counted.

## Notes

- Always present a dry-run summary before executing the write.
- Batch writes are atomic (Firestore limit: 500 operations per batch).
- Plan batch sizes from the total: sum of all members' class counts.
