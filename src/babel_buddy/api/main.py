from fastapi import FastAPI
from babel_buddy.api.routes import create_router


def create_app(engine=None, session_store=None) -> FastAPI:
    app = FastAPI(title="BabelBuddy", version="0.1.0")
    router = create_router(engine, session_store)
    app.include_router(router)
    return app
