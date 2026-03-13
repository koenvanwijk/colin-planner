"""Colin Planner MVP service (placeholder)."""
from datetime import datetime, timezone, date
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, Query, Response
from pydantic import BaseModel

app = FastAPI(title="Colin Planner")


class Block(BaseModel):
    title: str
    start: datetime
    end: datetime
    source: Optional[str] = "manual"


class HealthResponse(BaseModel):
    ok: bool


class MagisterOptions(BaseModel):
    enabled: Optional[bool] = True
    dateFrom: Optional[date] = None
    dateTill: Optional[date] = None


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


class MagisterRoosterResponse(BaseModel):
    source: str
    dateFrom: date
    dateTill: date
    items: List[Dict[str, Any]]
    note: Optional[str] = None


class VoetbalEventsResponse(BaseModel):
    source: str
    items: List[Dict[str, Any]]
    note: Optional[str] = None


class WhatsAppMessage(BaseModel):
    to: str
    body: str


class WhatsAppResponse(BaseModel):
    sent: bool


@app.get("/health", response_model=HealthResponse)
def health():
    return {"ok": True}


@app.get("/sources/magister/rooster", response_model=MagisterRoosterResponse)
def magister_rooster(
    dateFrom: date = Query(..., description="YYYY-MM-DD"),
    dateTill: date = Query(..., description="YYYY-MM-DD"),
) -> MagisterRoosterResponse:
    return MagisterRoosterResponse(
        source="magister",
        dateFrom=dateFrom,
        dateTill=dateTill,
        items=[],
        note="placeholder response; integration not yet wired",
    )


@app.get("/sources/voetbal/events", response_model=VoetbalEventsResponse)
def voetbal_events() -> VoetbalEventsResponse:
    return VoetbalEventsResponse(
        source="voetbal.nl",
        items=[],
        note="placeholder response; integration not yet wired",
    )


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


@app.post("/notifications/whatsapp", response_model=WhatsAppResponse)
def send_whatsapp(payload: WhatsAppMessage):
    # Placeholder: integrate Twilio/MessageBird here.
    return {"sent": True}
