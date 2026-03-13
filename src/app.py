"""Colin Planner MVP service (placeholder)."""
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, Query, Response
from pydantic import BaseModel

app = FastAPI(title="Colin Planner")


class Block(BaseModel):
    title: str
    start: datetime
    end: datetime
    source: Optional[str] = "manual"


class MagisterOptions(BaseModel):
    enabled: Optional[bool] = True
    dateFrom: Optional[str] = None
    dateTill: Optional[str] = None


class VoetbalOptions(BaseModel):
    enabled: Optional[bool] = True


class Preferences(BaseModel):
    sleepStart: Optional[str] = None
    sleepEnd: Optional[str] = None
    maxStudyBlocksPerDay: Optional[int] = None


class PlanRequest(BaseModel):
    fixedBlocks: List[Block]
    magister: Optional[MagisterOptions] = None
    voetbal: Optional[VoetbalOptions] = None
    preferences: Optional[Preferences] = None


class PlanResponse(BaseModel):
    generatedAt: datetime
    blocks: List[Block]


class WhatsAppMessage(BaseModel):
    to: str
    body: str


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/sources/magister/rooster")
def magister_rooster(
    dateFrom: str = Query(..., description="YYYY-MM-DD"),
    dateTill: str = Query(..., description="YYYY-MM-DD"),
) -> Dict[str, Any]:
    return {
        "source": "magister",
        "dateFrom": dateFrom,
        "dateTill": dateTill,
        "items": [],
        "note": "placeholder response; integration not yet wired",
    }


@app.get("/sources/voetbal/events")
def voetbal_events() -> Dict[str, Any]:
    return {
        "source": "voetbal.nl",
        "items": [],
        "note": "placeholder response; integration not yet wired",
    }


@app.post("/plan/build", response_model=PlanResponse)
def build_plan(payload: PlanRequest):
    return PlanResponse(generatedAt=datetime.now(timezone.utc), blocks=payload.fixedBlocks)


@app.post("/plan/export/ical")
def export_ical(payload: PlanResponse):
    ical = "\n".join(
        [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "PRODID:-//Colin Planner//EN",
            "BEGIN:VEVENT",
            f"DTSTAMP:{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}",
            "SUMMARY:Sample Plan",
            "END:VEVENT",
            "END:VCALENDAR",
        ]
    )
    return Response(content=ical, media_type="text/calendar")


@app.post("/notifications/whatsapp")
def send_whatsapp(payload: WhatsAppMessage):
    # Placeholder: integrate Twilio/MessageBird here.
    return {"sent": True, "to": payload.to}
