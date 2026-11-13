from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

from app.brain import SupportBrain


@dataclass(frozen=True)
class StageTiming:
    duration_ms: int
    start_ms: int
    end_ms: int


class MockPipeline:
    """A mock end-to-end voice pipeline with timestamped stages for latency testing."""

    def __init__(self) -> None:
        self.brain = SupportBrain()

    def run(self, transcript: str) -> dict[str, Any]:
        start = time.perf_counter_ns()

        stt_start = time.perf_counter_ns()
        stt_duration = 120 + (len(transcript) % 80)
        stt_end = stt_start + stt_duration * 1_000

        llm_start = stt_end
        response = self.brain.respond(transcript)
        llm_duration = 240 + (len(transcript) % 50)
        llm_end = llm_start + llm_duration * 1_000

        tts_start = llm_end
        tts_duration = 180 + (len(response["reply"]) % 90)
        tts_end = tts_start + tts_duration * 1_000

        total_ms = (time.perf_counter_ns() - start) // 1_000_000
        return {
            "transcript": transcript,
            "reply": response["reply"],
            "stt": {
                "start_ms": stt_start // 1_000_000,
                "end_ms": stt_end // 1_000_000,
                "duration_ms": stt_duration,
            },
            "llm": {
                "start_ms": llm_start // 1_000_000,
                "end_ms": llm_end // 1_000_000,
                "duration_ms": llm_duration,
            },
            "tts": {
                "start_ms": tts_start // 1_000_000,
                "end_ms": tts_end // 1_000_000,
                "duration_ms": tts_duration,
            },
            "total_latency_ms": max(total_ms, stt_duration + llm_duration + tts_duration),
            "tool": response["tool"],
            "escalate_to_human": response["escalate_to_human"],
        }
