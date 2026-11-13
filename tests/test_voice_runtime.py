from app.voice_runtime import VoiceRuntime
from types import SimpleNamespace

import app.voice_runtime as voice_runtime_module


def test_voice_runtime_defaults_to_mock_when_unconfigured() -> None:
    runtime = VoiceRuntime()

    assert runtime.runtime_mode == "mock"
    assert runtime.is_livekit_ready is False

    response = runtime.respond("my order status please")
    assert response["provider"] == "mock"
    assert response["tool"] == "lookup_order"
    assert "order" in response["reply"].lower()


def test_livekit_mode_requires_all_credentials_and_mock_mode_disabled(monkeypatch) -> None:
    monkeypatch.setattr(
        voice_runtime_module,
        "settings",
        SimpleNamespace(
            voice_mock_mode=False,
            livekit_url="wss://example.livekit.cloud",
            livekit_api_key="key",
            livekit_api_secret="secret",
            deepgram_api_key="deepgram-key",
            cartesia_api_key="cartesia-key",
            anthropic_api_key="anthropic-key",
        ),
    )

    runtime = VoiceRuntime()

    assert runtime.runtime_mode == "livekit"
    assert runtime.is_livekit_ready is True
    assert runtime.respond("order status")["provider"] == "mock"

    monkeypatch.setattr(
        voice_runtime_module,
        "settings",
        SimpleNamespace(
            voice_mock_mode=True,
            livekit_url="wss://example.livekit.cloud",
            livekit_api_key="key",
            livekit_api_secret="secret",
            deepgram_api_key="deepgram-key",
            cartesia_api_key="cartesia-key",
            anthropic_api_key="anthropic-key",
        ),
    )
    assert runtime.runtime_mode == "mock"
