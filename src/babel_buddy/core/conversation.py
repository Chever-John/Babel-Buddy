from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from babel_buddy.models import Message
from uuid import uuid4

class ConversationState(Enum):
    IDLE = "idle"
    LISTENING = "listening"
    PROCESSING = "processing"
    SPEAKING = "speaking"

VALID_TRANSITIONS = {
    ConversationState.IDLE: {ConversationState.LISTENING},
    ConversationState.LISTENING: {ConversationState.PROCESSING, ConversationState.IDLE},
    ConversationState.PROCESSING: {ConversationState.SPEAKING, ConversationState.IDLE},
    ConversationState.SPEAKING: {ConversationState.LISTENING, ConversationState.IDLE},
}

EXIT_PHRASES = {"bye babel", "goodbye babel", "see you babel"}

class ConversationManager:
    def __init__(self, max_turns: int = 20):
        self._state = ConversationState.IDLE
        self._max_turns = max_turns
        self._history: list[Message] = []
        self.session_id: str | None = None
        self._last_language: str = "en"

    @property
    def state(self) -> ConversationState:
        return self._state

    @property
    def history(self) -> list[Message]:
        return self._history

    @property
    def last_language(self) -> str:
        return self._last_language

    def _transition(self, new_state: ConversationState) -> None:
        if new_state not in VALID_TRANSITIONS[self._state]:
            raise ValueError(
                f"Invalid transition: {self._state.value} -> {new_state.value}"
            )
        self._state = new_state

    def activate(self) -> None:
        self._transition(ConversationState.LISTENING)
        self.session_id = str(uuid4())

    def deactivate(self) -> None:
        self._state = ConversationState.IDLE
        self.session_id = None

    def speech_received(self) -> None:
        self._transition(ConversationState.PROCESSING)

    def response_ready(self) -> None:
        self._transition(ConversationState.SPEAKING)

    def done_speaking(self) -> None:
        self._transition(ConversationState.LISTENING)

    def add_turn(self, role: str, content: str, language: str,
                 translation: str | None = None, confidence: float | None = None) -> None:
        msg = Message(
            id=str(uuid4()),
            session_id=self.session_id or "",
            role=role, content=content, translation=translation,
            language=language, confidence=confidence,
            audio_path=None, created_at=datetime.now(),
        )
        self._history.append(msg)
        self._last_language = language
        if len(self._history) > self._max_turns:
            self._history = self._history[-self._max_turns:]

    @staticmethod
    def is_exit_phrase(text: str) -> bool:
        normalized = text.strip().lower().rstrip("!.,?")
        return normalized in EXIT_PHRASES
