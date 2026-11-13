# Soki Voice Agent

This repo is the first deliverable for Phase 1 of the voice-agent roadmap. It includes a minimal browser-based voice demo and a SQLite-backed trace layer so each turn gets recorded and can be inspected later.

## What is included

- FastAPI backend for local serving
- Browser voice demo using the microphone and speech synthesis
- Mock support-agent responses for order status, returns, and product questions
- Separate support-brain policy layer with deterministic routing logic
- Mock latency pipeline that timestamps STT, LLM and TTS stages for a baseline
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

## Latency pipeline smoke test

The mock pipeline exposes per-stage timings so the project is ready for the real latency work in later phases.

```powershell
.
\.venv\Scripts\Activate.ps1
python scripts\baseline_latency.py
```

This prints a basic stage summary for STT, LLM, and TTS, with a total latency value for each sample turn.

## Phase 1 and 2 acceptance criteria

- Browser voice call loop is available.
- Trace rows are created for each user request.
- Support brain handles order, return, product, and escalation intents.
- The pipeline exposes stage-level timing data for a baseline latency table.
