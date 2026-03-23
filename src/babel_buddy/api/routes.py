from fastapi import APIRouter, HTTPException
from babel_buddy.api.schemas import (
    ChatRequest, ChatResponse, SessionResponse, MessageResponse, HealthResponse,
)


def create_router(engine, session_store) -> APIRouter:
    router = APIRouter(prefix="/api")

    @router.get("/health", response_model=HealthResponse)
    async def health():
        return HealthResponse(status="ok", state=engine.conversation.state.value)

    @router.get("/sessions", response_model=list[SessionResponse])
    async def list_sessions():
        sessions = await session_store.list_sessions()
        return [
            SessionResponse(id=s.id, started_at=s.started_at.isoformat(),
                          ended_at=s.ended_at.isoformat() if s.ended_at else None)
            for s in sessions
        ]

    @router.get("/sessions/{session_id}")
    async def get_session(session_id: str):
        session = await session_store.get_session(session_id)
        if session is None:
            raise HTTPException(status_code=404, detail="Session not found")
        messages = await session_store.get_messages(session_id)
        return {
            "session": SessionResponse(id=session.id, started_at=session.started_at.isoformat(),
                                      ended_at=session.ended_at.isoformat() if session.ended_at else None),
            "messages": [
                MessageResponse(id=m.id, role=m.role, content=m.content,
                              translation=m.translation, language=m.language,
                              created_at=m.created_at.isoformat())
                for m in messages
            ],
        }

    @router.post("/chat", response_model=ChatResponse)
    async def chat(req: ChatRequest):
        result = await engine.process_text(req.text, req.language)
        return ChatResponse(reply=result.reply, translation=result.translation, language=result.language)

    return router
