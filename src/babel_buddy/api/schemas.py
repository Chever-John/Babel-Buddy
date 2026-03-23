from pydantic import BaseModel


class ChatRequest(BaseModel):
    text: str
    language: str = "en"


class ChatResponse(BaseModel):
    reply: str
    translation: str
    language: str


class SessionResponse(BaseModel):
    id: str
    started_at: str
    ended_at: str | None


class MessageResponse(BaseModel):
    id: str
    role: str
    content: str
    translation: str | None
    language: str
    created_at: str


class HealthResponse(BaseModel):
    status: str
    state: str
