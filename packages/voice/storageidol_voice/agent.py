"""
LiveKit Agents voice pipeline for StorageIdol.

Architecture:
  LiveKit room (SIP inbound/outbound)
    → Silero VAD (voice activity detection)
    → Deepgram STT (streaming transcription)
    → bridge.py (feeds transcript into shared LangGraph graph)
    → ElevenLabs TTS (streams synthesized audio back to caller)

The LangGraph graph (identical to WhatsApp) does ALL reasoning.
This file only wires the audio I/O around it.

Configuration (from environment):
    LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET
    DEEPGRAM_API_KEY
    ELEVENLABS_API_KEY
    CLIENT_ID (set by Docker environment per client)
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field

from livekit.agents import (
    AutoSubscribe,
    JobContext,
    WorkerOptions,
    cli,
    llm as agents_llm,
)
from livekit.agents.pipeline import VoicePipelineAgent
from livekit.plugins import deepgram, elevenlabs, silero

logger = logging.getLogger(__name__)


@dataclass
class VoiceAgentConfig:
    """Per-client voice configuration (loaded from clients/<id>/config.yaml)."""

    client_id: str
    elevenlabs_voice_id: str
    stt_provider: str = "deepgram"        # deepgram | assemblyai
    language: str = "es-ES"
    speed: float = 1.0
    inbound_transfer_number: str | None = None


class _GraphLLMAdapter(agents_llm.LLM):
    """
    Adapts the shared StorageIdol LangGraph to the LiveKit LLM interface.

    LiveKit's VoicePipelineAgent expects an LLM that accepts a chat context and
    returns a streamed response. This adapter:
      1. Serialises the LiveKit ChatContext into the AgentState format.
      2. Invokes the client's compiled LangGraph graph synchronously (run_until_complete).
      3. Streams the text output back to LiveKit's TTS plugin.

    The graph is compiled once on startup and cached — identical to how the
    WhatsApp path runs it (via core/agents/tasks.py).
    """

    def __init__(self, client_id: str, graph_config: object) -> None:
        super().__init__()
        self._client_id = client_id
        self._graph_config = graph_config
        self._compiled_graph: object | None = None

    def _load_graph(self) -> object:
        if self._compiled_graph is None:
            from core.agents.graphs.registry import load_graph  # type: ignore[import]
            self._compiled_graph = load_graph(self._client_id, self._graph_config)
        return self._compiled_graph

    def chat(  # type: ignore[override]
        self,
        chat_ctx: agents_llm.ChatContext,
        **kwargs: object,
    ) -> agents_llm.LLMStream:
        """Called by LiveKit for each turn. Returns a stream adapter."""
        return _GraphLLMStream(
            llm=self,
            chat_ctx=chat_ctx,
            client_id=self._client_id,
            graph=self._load_graph(),
        )


class _GraphLLMStream(agents_llm.LLMStream):
    """Wraps a LangGraph invocation as a LiveKit LLMStream."""

    def __init__(
        self,
        llm: _GraphLLMAdapter,
        chat_ctx: agents_llm.ChatContext,
        client_id: str,
        graph: object,
    ) -> None:
        super().__init__(llm=llm, chat_ctx=chat_ctx, fnc_ctx=None)
        self._client_id = client_id
        self._graph = graph

    async def _run(self) -> None:
        """
        Invoke the LangGraph and emit text chunks to LiveKit.

        LangGraph runs synchronously inside an asyncio thread to avoid blocking.
        """
        import asyncio

        from storageidol_agents.state import AgentState, Channel  # type: ignore[import]

        # Build input state from chat context
        messages = [
            {"role": m.role.value, "content": m.content}
            for m in self._chat_ctx.messages
            if m.content
        ]
        state = AgentState(
            client_id=self._client_id,
            channel=Channel.VOICE,
            messages=messages,
        )

        try:
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self._graph.invoke(state),  # type: ignore[union-attr]
            )
            reply = result.get("reply", "")
        except Exception:
            logger.exception("Graph invocation failed during voice call")
            reply = "Lo siento, ha ocurrido un error. ¿Puede repetir su pregunta?"

        # Emit reply as a single chunk (LiveKit will handle chunking for TTS)
        self._event_ch.send_nowait(
            agents_llm.ChatChunk(
                request_id="voice",
                choices=[
                    agents_llm.Choice(
                        delta=agents_llm.ChoiceDelta(role="assistant", content=reply),
                        index=0,
                    )
                ],
            )
        )


class VoiceAgent:
    """
    Wraps VoicePipelineAgent with per-client config.

    Instantiated once per LiveKit room (= one inbound/outbound call).
    """

    def __init__(self, config: VoiceAgentConfig, graph_config: object) -> None:
        self._config = config
        self._graph_llm = _GraphLLMAdapter(
            client_id=config.client_id,
            graph_config=graph_config,
        )

    def _build_pipeline(self) -> VoicePipelineAgent:
        stt = deepgram.STT(language=self._config.language)
        tts = elevenlabs.TTS(
            voice_id=self._config.elevenlabs_voice_id,
            model="eleven_multilingual_v2",
        )
        vad = silero.VAD.load()

        return VoicePipelineAgent(
            vad=vad,
            stt=stt,
            llm=self._graph_llm,
            tts=tts,
            allow_interruptions=True,
        )

    async def run(self, ctx: JobContext) -> None:
        """Entry point called by the LiveKit Worker for each new room."""
        await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
        agent = self._build_pipeline()
        agent.start(ctx.room)
        logger.info(
            "Voice agent started for client=%s room=%s",
            self._config.client_id,
            ctx.room.name,
        )
        await agent.say(
            "Hola, soy el asistente virtual. ¿En qué puedo ayudarle?",
            allow_interruptions=True,
        )


async def entrypoint(ctx: JobContext) -> None:
    """
    LiveKit worker entrypoint — called once per incoming job (call).

    Reads CLIENT_ID from the environment (set by Docker per client).
    Loads the client config and compiles the graph on first call.
    """
    client_id = os.environ.get("CLIENT_ID", "unknown")

    # Load client config from config.yaml
    import yaml  # type: ignore[import]
    config_path = f"/app/clients/{client_id}/config.yaml"
    try:
        with open(config_path) as f:
            raw = yaml.safe_load(f)
    except FileNotFoundError:
        logger.error("config.yaml not found for client %s at %s", client_id, config_path)
        return

    voice_cfg = raw.get("voice", {})
    config = VoiceAgentConfig(
        client_id=client_id,
        elevenlabs_voice_id=voice_cfg.get("elevenlabs_voice_id", ""),
        stt_provider=voice_cfg.get("stt_provider", "deepgram"),
        language=voice_cfg.get("language", "es-ES"),
        speed=voice_cfg.get("speed", 1.0),
        inbound_transfer_number=voice_cfg.get("inbound_transfer_number"),
    )

    # graph_config is a lightweight object holding runtime-injected config values.
    # The heavy compile() happens lazily in _GraphLLMAdapter._load_graph().
    from storageidol_agents.state import ClientConfig  # type: ignore[import]
    graph_config = ClientConfig.from_dict(raw)

    agent = VoiceAgent(config=config, graph_config=graph_config)
    await agent.run(ctx)


def run_voice_worker(client_id: str | None = None) -> None:
    """
    Start the LiveKit Agent worker process.

    In production this is the CMD of the `voice` Docker container.
    In dev, call: python -m storageidol_voice
    """
    if client_id:
        os.environ.setdefault("CLIENT_ID", client_id)

    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
        )
    )
