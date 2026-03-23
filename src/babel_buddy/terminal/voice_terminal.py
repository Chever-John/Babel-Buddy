import asyncio
from pathlib import Path
from babel_buddy.config import load_settings
from babel_buddy.data.session_store import SessionStore
from babel_buddy.llm.ollama_client import OllamaClient
from babel_buddy.core.engine import BabelEngine


class TextTerminal:
    """Text-only terminal for development/testing without audio hardware."""

    def __init__(self, engine: BabelEngine):
        self._engine = engine

    async def run(self) -> None:
        print("BabelBuddy Text Terminal")
        print("Press Enter to start a session. Type 'quit' to exit.\n")

        while True:
            cmd = await asyncio.get_event_loop().run_in_executor(None, input, "> ")
            if cmd.strip().lower() == "quit":
                break

            if self._engine.conversation.state.value == "idle":
                await self._engine.start_session()
                print("Session started! Type your message.\n")
                continue

            result = await self._engine.process_text(cmd.strip(), "auto")
            print(f"\n[{result.language}] {result.reply}")
            if result.translation:
                print(f"[Translation] {result.translation}")
            print()

            if result.is_exit:
                print("Session ended.\n")


async def main():
    config_path = Path("config/settings.yaml")
    settings = load_settings(config_path)

    store = SessionStore(settings.storage.database)
    await store.initialize()

    llm = OllamaClient(
        host=settings.models.llm.ollama_host,
        model=settings.models.llm.name,
    )

    # Use mock ASR/TTS/VAD for text-only mode
    from unittest.mock import AsyncMock, MagicMock
    asr = AsyncMock()
    tts = AsyncMock()
    tts.synthesize.return_value = b""
    vad = MagicMock()

    engine = BabelEngine(asr=asr, llm=llm, tts=tts, vad=vad, session_store=store)

    terminal = TextTerminal(engine)
    await terminal.run()
    await store.close()


if __name__ == "__main__":
    asyncio.run(main())
