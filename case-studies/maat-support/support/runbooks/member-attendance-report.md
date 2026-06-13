# Member Attendance Report

> Export a full report of attended classes for a specific member as a CSV.

## When to Use

- A gym owner or staff member requests attendance history for a specific member
- Keywords: "attended classes", "attendance report", "class history"

## Prerequisites

- Gym name or ID
- Member name

## Steps

### 1. Find the gym

**Service:** Firestore
**Permission:** Read

Query the `gyms` collection to find the gym by name.

### 2. Find the member

**Service:** Firestore
**Permission:** Read

Query `gyms/{gymId}/members` and join with `users/{userId}` to find the member by name.

### 3. Get attendance data

**Service:** Firestore
**Permission:** Read

Read the member's attendance records from `gyms/{gymId}/members/{userId}/attendance`. Each record contains:
- `date`, `weekDay`, `className`, `timeStart`, `timeEnd`
- `classType` (e.g. "striking", "grappling")
- `beltAtTime`

### 4. Export as CSV

Generate a CSV with columns: Date, Day, Class Name, Time Start, Time End, Type. Sort by date ascending.

### 5. Share with the requester

Send the CSV by email or post it as a ticket comment, depending on the request.

## Common Variations

- May need to filter by date range if only a specific period is requested.

## Notes

- The member document also carries `lastAttendedDate` for a quick reference, which may differ slightly from the latest attendance record.
