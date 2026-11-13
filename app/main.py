from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.brain import SupportBrain
from app.config import settings
from app.trace import list_recent_traces, record_trace

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
brain = SupportBrain()

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
    result = brain.respond(transcript)
    return result["reply"]


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

    response = brain.respond(transcript)
    reply = response["reply"]
    trace = record_trace(
        source=payload.mode,
        status="ok",
        transcript=transcript,
        reply=reply,
        metadata={"mode": "mock", "provider": "local-demo", "tool": response["tool"], "escalate_to_human": response["escalate_to_human"]},
    )
    return VoiceResponse(transcript=transcript, reply=reply, trace_id=trace["id"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
