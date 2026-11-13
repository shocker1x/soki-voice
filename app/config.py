from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class AppConfig:
    app_env: str = os.getenv("APP_ENV", "development")
    data_dir: Path = Path(os.getenv("APP_DATA_DIR", "./data"))
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./data/voice_traces.db")
    voice_mock_mode: bool = os.getenv("VOICE_MOCK_MODE", "true").lower() == "true"
    livekit_url: str = os.getenv("LIVEKIT_URL", "")
    livekit_api_key: str = os.getenv("LIVEKIT_API_KEY", "")
    livekit_api_secret: str = os.getenv("LIVEKIT_API_SECRET", "")
    deepgram_api_key: str = os.getenv("DEEPGRAM_API_KEY", "")
    cartesia_api_key: str = os.getenv("CARTESIA_API_KEY", "")
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    public_base_url: str = os.getenv("PUBLIC_BASE_URL", "http://127.0.0.1:8000")


settings = AppConfig()
