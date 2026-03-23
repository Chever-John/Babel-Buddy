import asyncio
import sys
from pathlib import Path


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "serve":
        _serve()
    else:
        from babel_buddy.terminal.voice_terminal import main as terminal_main
        asyncio.run(terminal_main())


def _serve():
    import uvicorn
    from babel_buddy.config import load_settings

    settings = load_settings(Path("config/settings.yaml"))

    # Build app with engine wired up
    from babel_buddy.api.main import create_app
    from babel_buddy.data.session_store import SessionStore
    from babel_buddy.llm.ollama_client import OllamaClient
    from babel_buddy.core.engine import BabelEngine
    from unittest.mock import AsyncMock, MagicMock

    store = SessionStore(settings.storage.database)
    llm = OllamaClient(
        host=settings.models.llm.ollama_host,
        model=settings.models.llm.name,
    )
    # Text-only mode: mock ASR/TTS/VAD for now
    asr = AsyncMock()
    tts = AsyncMock()
    tts.synthesize.return_value = b""
    vad = MagicMock()

    engine = BabelEngine(asr=asr, llm=llm, tts=tts, vad=vad, session_store=store)

    app = create_app(engine=engine, session_store=store)

    # Initialize store on startup
    @app.on_event("startup")
    async def startup():
        await store.initialize()

    @app.on_event("shutdown")
    async def shutdown():
        await store.close()

    uvicorn.run(
        app,
        host=settings.server.host,
        port=settings.server.port,
    )


if __name__ == "__main__":
    main()
