# Soki Voice Agent

This repo is the first deliverable for Phase 1 of the voice-agent roadmap. It includes a minimal browser-based voice demo and a SQLite-backed trace layer so each turn gets recorded and can be inspected later.

## What is included

- FastAPI backend for local serving
- Browser voice demo using the microphone and speech synthesis
- Mock support-agent responses for order status, returns, and product questions
- SQLite table for trace persistence (`data/voice_traces.db`)
- `.env.example` for provider and environment configuration

## Run locally

1. Activate the virtual environment:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```
2. Install dependencies:
   ```powershell
   python -m pip install -r requirements.txt
   ```
3. Start the app:
   ```powershell
   python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
   ```
4. Open the browser at `http://127.0.0.1:8000/`

## Notes

- The current demo is intentionally in mock mode so the project works without API keys.
- Real STT/TTS providers are configured via environment variables in `.env.example` and are ready for Phase 2.
- Every turn writes a trace entry to SQLite with the transcript and reply.

## Phase 1 acceptance criteria

- Browser voice call loop is available.
- Trace rows are created for each user request.
- Project is ready for the next phase: support-brain tooling and real pipeline wiring.
