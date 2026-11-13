from app.pipeline import MockPipeline


def test_pipeline_emits_stage_times_and_reply():
    pipeline = MockPipeline()
    result = pipeline.run("my order status please")

    assert result["reply"]
    assert set(["stt", "llm", "tts", "total_latency_ms"]) <= set(result.keys())
    assert result["total_latency_ms"] > 0
    assert result["stt"]["duration_ms"] > 0
