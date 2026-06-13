# Update Belt Requirements

> Update the number of classes required per belt in a gym's belt system.

## When to Use

A gym asks to change how many classes are required for belt promotions. Values are usually given **per stripe** (per sub-grade), but Firestore stores the total **per belt**.

## Key Concept

`belt_system` stores `classesRequired` as the **total classes for the whole belt**. Gyms usually communicate a value **per stripe**. Multiply:

```
classesRequired = classes_per_stripe x stripesPerBelt
```

BJJ adult belts typically have **5 stripes** (4 stripes + the belt itself). Confirm with the gym or ticket before calculating.

## Steps

1. **Find the gym** — query the `gyms` collection by name to get the gym ID.
2. **Read the belt system** — read all documents in `gyms/{gymId}/belt_system`.
3. **Identify affected belts** — match the ticket values to belt documents (white, blue, purple, brown, etc.).
4. **Calculate totals** — multiply per-stripe values by `stripesPerBelt`. Confirm the stripe count with the requester.
5. **Present the update** — show a table of current vs new values and the exact Firestore writes.
6. **Execute after approval (write)** — update `classesRequired` on each affected belt document.
7. **Verify** — re-read the belt system to confirm the values.

## Firestore Path

```
gyms/{gymId}/belt_system/{beltName}
```

## Fields Updated

| Field | Description |
|-------|-------------|
| `classesRequired` | Total classes required to complete this belt |
| `stripesPerBelt` | Number of stripes per belt (only change if the gym is changing the stripe count) |

## Common Variations

- **Kids + adults:** some gyms have both adult belts and a longer kids belt ladder. Confirm whether the change applies to one or both groups.
- **Uniform vs per-belt values:** some gyms want the same total across all belts, others want different values per belt. Confirm with the ticket.

## Example (fictional)

**Iron Lotus BJJ** asks for: White=50, Blue=70, Purple=60, Brown=40 (per stripe, 5 stripes each).

| Belt | Per stripe | x stripes | classesRequired |
|------|-----------|-----------|-----------------|
| White | 50 | x 5 | 250 |
| Blue | 70 | x 5 | 350 |
| Purple | 60 | x 5 | 300 |
| Brown | 40 | x 5 | 200 |
