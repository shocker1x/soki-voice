from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.brain import SupportBrain
from app.trace import list_recent_traces, record_trace
from app.voice_runtime import VoiceRuntime

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
brain = SupportBrain()
voice_runtime = VoiceRuntime(brain=brain)

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
    result = voice_runtime.respond(transcript)
    return result["reply"]


@app.get("/")
async def serve_index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
async def health() -> dict[str, object]:
    return {
        "status": "ok",
        "mode": "mock",
        "livekit_ready": voice_runtime.is_livekit_ready,
        "deepgram_ready": voice_runtime.deepgram_ready,
        "cartesia_ready": voice_runtime.cartesia_ready,
        "anthropic_ready": voice_runtime.anthropic_ready,
    }


@app.get("/api/runtime/status")
async def runtime_status() -> dict[str, object]:
    return {
        "browser_mode": "mock",
        "worker_mode": voice_runtime.runtime_mode,
        "livekit_ready": voice_runtime.is_livekit_ready,
        "deepgram_ready": voice_runtime.deepgram_ready,
        "cartesia_ready": voice_runtime.cartesia_ready,
        "anthropic_ready": voice_runtime.anthropic_ready,
        "worker_command": "python -m app.livekit_worker dev",
    }


@app.get("/api/traces")
async def fetch_traces() -> list[dict[str, object]]:
    return list_recent_traces(limit=20)


async def _handle_turn(payload: VoiceRequest, mode: str) -> VoiceResponse:
    transcript = payload.transcript.strip()
    if not transcript:
        raise HTTPException(status_code=400, detail="A transcript is required.")

    response = voice_runtime.respond(transcript)
    trace = record_trace(
        source=payload.mode,
        status="ok",
        transcript=transcript,
        reply=response["reply"],
        metadata={
            "mode": mode,
            "provider": response["provider"],
            "tool": response["tool"],
            "escalate_to_human": response["escalate_to_human"],
            **response["metadata"],
        },
    )
    return VoiceResponse(transcript=transcript, reply=response["reply"], trace_id=trace["id"])


@app.post("/api/voice/mock", response_model=VoiceResponse)
async def mock_voice_turn(payload: VoiceRequest) -> VoiceResponse:
    return await _handle_turn(payload, mode="mock")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
