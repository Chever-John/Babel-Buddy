from dataclasses import dataclass, field
from datetime import datetime
from typing import AsyncIterator, Protocol
from uuid import uuid4

# --- Data classes ---

@dataclass
class ASRResult:
    text: str
    language: str  # "zh" | "en"
    confidence: float

@dataclass
class LLMResponse:
    reply: str
    translation: str
    language: str

@dataclass
class Message:
    id: str
    session_id: str
    role: str  # "user" | "assistant"
    content: str
    translation: str | None
    language: str
    confidence: float | None
    audio_path: str | None
    created_at: datetime

@dataclass
class Session:
    id: str
    started_at: datetime
    ended_at: datetime | None = None

# --- Provider protocols ---

class ASRProvider(Protocol):
    async def transcribe(self, audio: bytes) -> ASRResult: ...

class LLMProvider(Protocol):
    async def chat(self, messages: list[dict]) -> LLMResponse: ...
    async def chat_stream(self, messages: list[dict]) -> AsyncIterator[str]: ...

class TTSProvider(Protocol):
    async def synthesize(self, text: str, language: str) -> bytes: ...

class VADProvider(Protocol):
    def is_speech(self, audio_chunk: bytes) -> bool: ...

class WakeWordProvider(Protocol):
    def detect(self, audio_chunk: bytes) -> bool: ...

class AudioSource(Protocol):
    async def read_audio(self) -> bytes: ...
    async def play_audio(self, audio: bytes) -> None: ...
    async def display(self, text: str, translation: str) -> None: ...
