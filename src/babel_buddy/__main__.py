# src/babel_buddy/__main__.py
import asyncio
import sys
from pathlib import Path

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "serve":
        import uvicorn
        from babel_buddy.config import load_settings
        settings = load_settings(Path("config/settings.yaml"))
        uvicorn.run(
            "babel_buddy.api.main:create_app",
            host=settings.server.host,
            port=settings.server.port,
            factory=True,
        )
    else:
        from babel_buddy.terminal.voice_terminal import main as terminal_main
        asyncio.run(terminal_main())

if __name__ == "__main__":
    main()
