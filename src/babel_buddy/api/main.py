from fastapi import FastAPI, WebSocket
from babel_buddy.api.routes import create_router
from babel_buddy.api.websocket import websocket_chat

def create_app(engine=None, session_store=None) -> FastAPI:
    app = FastAPI(title="BabelBuddy", version="0.1.0")
    router = create_router(engine, session_store)
    app.include_router(router)

    @app.websocket("/api/ws/chat")
    async def ws_chat(ws: WebSocket):
        await websocket_chat(ws, engine)

    return app
