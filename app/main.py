from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.config import settings
from app.trace import list_recent_traces, record_trace

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(title="Soki Voice Demo", version="0.1.0")
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


class VoiceRequest(BaseModel):
    transcript: str
    mode: str = "browser"


class VoiceResponse(BaseModel):
    transcript: str
    reply: str
    trace_id: int | None = None


def build_reply(transcript: str) -> str:
    normalized = transcript.strip()
    if not normalized:
        return "I didn’t catch that. Please say your order number or ask about returns."

    lower = normalized.lower()
    if "order" in lower and ("status" in lower or "track" in lower):
        return "I can help with your order. Please give me the order number or the email used at checkout."
    if "return" in lower or "refund" in lower:
        return "Returns are handled after review. I can start a return request if you share the order number."
    if "rug" in lower or "product" in lower:
        return "Our handmade rugs are available in wool, cotton, and vintage styles. Tell me the room size or style you want."
    if "hello" in lower or "hi" in lower:
        return "Hi. I can help with order status, returns, and product questions."
    return "I heard you. I can help with order status, returns, product questions, or human escalation."


@app.get("/")
async def serve_index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "mode": "mock" if settings.voice_mock_mode else "configured"}


@app.get("/api/traces")
async def fetch_traces() -> list[dict[str, object]]:
    return list_recent_traces(limit=20)


@app.post("/api/voice/mock", response_model=VoiceResponse)
async def mock_voice_turn(payload: VoiceRequest) -> VoiceResponse:
    transcript = payload.transcript.strip()
    if not transcript:
        raise HTTPException(status_code=400, detail="A transcript is required.")

    reply = build_reply(transcript)
    trace = record_trace(
        source=payload.mode,
        status="ok",
        transcript=transcript,
        reply=reply,
        metadata={"mode": "mock", "provider": "local-demo"},
    )
    return VoiceResponse(transcript=transcript, reply=reply, trace_id=trace["id"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
