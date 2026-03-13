# Firestore Schema (v0)

Collections (top-level):

## users/{userId}
```json
{
  "displayName": "Colin",
  "timezone": "Europe/Amsterdam",
  "whatsapp": "+31612345678",
  "createdAt": "2026-03-13T15:00:00Z"
}
```

### users/{userId}/fixed_blocks/{blockId}
```json
{
  "title": "Voetbal training",
  "start": "2026-03-17T19:00:00+01:00",
  "end": "2026-03-17T21:30:00+01:00",
  "rrule": "FREQ=WEEKLY;BYDAY=MO,WE",
  "source": "manual",
  "createdAt": "2026-03-13T15:00:00Z"
}
```

### users/{userId}/plans/{planId}
```json
{
  "weekStart": "2026-03-17",
  "weekEnd": "2026-03-23",
  "generatedAt": "2026-03-13T16:00:00Z",
  "blocks": [
    {
      "title": "Wiskunde leren",
      "start": "2026-03-18T16:00:00+01:00",
      "end": "2026-03-18T17:30:00+01:00",
      "source": "planner"
    }
  ]
}
```

### users/{userId}/sources/{sourceId}
```json
{
  "type": "magister",
  "enabled": true,
  "lastSyncAt": "2026-03-13T16:05:00Z"
}
```

## events/{eventId}
(Optioneel voor shared events/imports)
```json
{
  "title": "Wedstrijd",
  "start": "2026-03-22T10:00:00+01:00",
  "end": "2026-03-22T12:00:00+01:00",
  "source": "voetbal.nl",
  "userId": "colin"
}
```

Notes:
- Store timestamps as ISO8601 strings or Firestore Timestamps.
- Use subcollections under `users` for privacy + easy queries.
- Add indexes later for range queries (date windows).
