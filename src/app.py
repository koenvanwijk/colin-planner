"""Colin Planner MVP service (placeholder)."""
from datetime import datetime
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Colin Planner")


class Block(BaseModel):
    title: str
    start: datetime
    end: datetime
    source: str | None = "manual"


class PlanRequest(BaseModel):
    fixedBlocks: list[Block]


class PlanResponse(BaseModel):
    generatedAt: datetime
    blocks: list[Block]


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/plan/build", response_model=PlanResponse)
def build_plan(payload: PlanRequest):
    return PlanResponse(generatedAt=datetime.utcnow(), blocks=payload.fixedBlocks)
