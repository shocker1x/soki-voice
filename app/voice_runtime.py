from __future__ import annotations

from typing import Any

from app.brain import SupportBrain
from app.config import settings


class VoiceRuntime:
    """Wrap the support-brain logic with an env-gated runtime mode.

    The mock path remains the default for local development and smoke tests. When all
    LiveKit + provider credentials are present, the runtime advertises itself as
    "livekit" while still using the validated support-brain policy layer.
    """

    def __init__(self, brain: SupportBrain | None = None) -> None:
        self.brain = brain or SupportBrain()

    @property
    def livekit_ready(self) -> bool:
        return bool(settings.livekit_url and settings.livekit_api_key and settings.livekit_api_secret)

    @property
    def deepgram_ready(self) -> bool:
        return bool(settings.deepgram_api_key)

    @property
    def cartesia_ready(self) -> bool:
        return bool(settings.cartesia_api_key)

    @property
    def anthropic_ready(self) -> bool:
        return bool(settings.anthropic_api_key)

    @property
    def runtime_mode(self) -> str:
        if (
            not settings.voice_mock_mode
            and self.livekit_ready
            and self.deepgram_ready
            and self.cartesia_ready
            and self.anthropic_ready
        ):
            return "livekit"
        return "mock"

    @property
    def is_livekit_ready(self) -> bool:
        return self.runtime_mode == "livekit"

    def respond(self, transcript: str) -> dict[str, Any]:
        result = self.brain.respond(transcript)
        metadata = {
            **result.get("metadata", {}),
            "runtime_mode": self.runtime_mode,
            "livekit_ready": self.is_livekit_ready,
            "deepgram_ready": self.deepgram_ready,
            "cartesia_ready": self.cartesia_ready,
            "anthropic_ready": self.anthropic_ready,
        }
        return {
            "tool": result["tool"],
            "reply": result["reply"],
            "escalate_to_human": result["escalate_to_human"],
            "provider": "mock",
            "metadata": metadata,
        }

