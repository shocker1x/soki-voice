from __future__ import annotations

from dotenv import load_dotenv
from livekit import agents
from livekit.agents import Agent, AgentSession, AgentServer, RunContext, function_tool
from livekit.plugins import anthropic, cartesia, deepgram

from app.brain import SupportBrain
from app.config import settings
from app.trace import record_trace

load_dotenv()
brain = SupportBrain()
server = AgentServer()


class SokiSupportAgent(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=(
                "You are Soki, a concise and helpful rug-store support voice agent. "
                "For every customer support request, call resolve_support_request and "
                "use its result as the source of truth. Do not invent order, return, "
                "or product details."
            ),
        )

    @function_tool
    async def resolve_support_request(self, context: RunContext, request: str) -> str:
        """Resolve an order, return, product, or escalation request using store policy."""
        result = brain.respond(request)
        record_trace(
            source="livekit",
            status="ok",
            transcript=request,
            reply=result["reply"],
            metadata={
                "mode": "livekit",
                "provider": "livekit",
                "llm": "anthropic",
                "stt": "deepgram",
                "tts": "cartesia",
                "tool": result["tool"],
                "escalate_to_human": result["escalate_to_human"],
                **result.get("metadata", {}),
            },
        )
        return result["reply"]


@server.rtc_session(agent_name="soki-support")
async def soki_support(ctx: agents.JobContext) -> None:
    session = AgentSession(
        stt=deepgram.STT(
            model="nova-3",
            language="en",
            api_key=settings.deepgram_api_key,
        ),
        llm=anthropic.LLM(
            model="claude-3-5-haiku-latest",
            api_key=settings.anthropic_api_key,
        ),
        tts=cartesia.TTS(
            model="sonic-3",
            voice="f786b574-daa5-4673-aa0c-cbe3e8534c02",
            api_key=settings.cartesia_api_key,
        ),
    )
    await session.start(room=ctx.room, agent=SokiSupportAgent())
    await session.generate_reply(
        instructions="Greet the customer and ask how you can help with their rug order."
    )


if __name__ == "__main__":
    agents.cli.run_app(server)
