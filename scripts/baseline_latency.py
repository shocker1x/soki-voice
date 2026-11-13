from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.pipeline import MockPipeline


def run_sample_batch() -> None:
    pipeline = MockPipeline()
    sample_transcripts = [
        "my order status please",
        "I need a return for order 4821",
        "Do you have any wool rugs under 2000?",
        "Hi, I need help with my order",
    ]

    results = [pipeline.run(text) for text in sample_transcripts]

    for idx, result in enumerate(results, start=1):
        print(f"Run {idx}: total={result['total_latency_ms']}ms | tool={result['tool']} | reply={result['reply']}")

    stage_names = ["stt", "llm", "tts"]
    print("\nStage summary:")
    for stage_name in stage_names:
        values = [result[stage_name]["duration_ms"] for result in results]
        avg = sum(values) / len(values)
        print(f"{stage_name}: avg={avg:.1f}ms min={min(values)}ms max={max(values)}ms")


if __name__ == "__main__":
    run_sample_batch()
