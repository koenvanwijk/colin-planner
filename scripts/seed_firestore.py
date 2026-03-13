import os
from datetime import datetime, timezone
from google.cloud import firestore

PROJECT_ID = os.getenv("GCP_PROJECT_ID")


def main():
    db = firestore.Client(project=PROJECT_ID)
    now = datetime.now(timezone.utc).isoformat()

    user_id = "colin"
    user_ref = db.collection("users").document(user_id)
    user_ref.set(
        {
            "displayName": "Colin",
            "timezone": "Europe/Amsterdam",
            "whatsapp": "+31600000000",
            "createdAt": now,
        },
        merge=True,
    )

    fixed_blocks = user_ref.collection("fixed_blocks")
    fixed_blocks.document("work_thu_fri").set(
        {
            "title": "Werk",
            "start": "2026-03-19T18:00:00+01:00",
            "end": "2026-03-19T24:00:00+01:00",
            "rrule": "FREQ=WEEKLY;BYDAY=TH,FR",
            "source": "manual",
            "createdAt": now,
        },
        merge=True,
    )
    fixed_blocks.document("soccer_training").set(
        {
            "title": "Voetbal training",
            "start": "2026-03-17T19:00:00+01:00",
            "end": "2026-03-17T21:30:00+01:00",
            "rrule": "FREQ=WEEKLY;BYDAY=MO,WE",
            "source": "manual",
            "createdAt": now,
        },
        merge=True,
    )

    plans = user_ref.collection("plans")
    plans.document("sample_week").set(
        {
            "weekStart": "2026-03-17",
            "weekEnd": "2026-03-23",
            "generatedAt": now,
            "blocks": [
                {
                    "title": "Wiskunde leren",
                    "start": "2026-03-18T16:00:00+01:00",
                    "end": "2026-03-18T17:30:00+01:00",
                    "source": "planner",
                }
            ],
        },
        merge=True,
    )

    print("Seeded Firestore sample data")


if __name__ == "__main__":
    main()
