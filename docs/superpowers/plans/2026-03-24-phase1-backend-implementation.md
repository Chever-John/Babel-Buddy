# BabelBuddy Phase 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the full BabelBuddy Phase 1 backend and CLI terminal for bilingual (Chinese-English) AI conversation with voice support.

**Architecture:** Python 3.12+ FastAPI backend with Protocol-based provider interfaces. Each AI module (ASR/TTS/LLM/VAD/WakeWord) implements a Protocol for independent swapping. BabelEngine orchestrates the pipeline: WakeWord → VAD → ASR → LLM → TTS.

**Tech Stack:** Python 3.12+, uv, FastAPI, aiosqlite, httpx, pytest, Whisper, CosyVoice, Silero VAD, Ollama

---

## Context

BabelBuddy is a greenfield project — no source code exists yet. The design spec at `docs/superpowers/specs/2026-03-24-phase1-cn-en-conversation-design.md` defines a bilingual AI assistant (Chinese + English) with voice-first interaction. This plan implements the full backend + CLI terminal. Web frontend (React) will be a separate plan.

## Scope

This plan covers **backend + CLI** only:
- Project scaffolding & config
- Data models & Protocol interfaces
- SQLite session store
- AI providers (LLM, ASR, TTS, VAD, Wake Word)
- Core engine (Conversation Manager + BabelEngine)
- FastAPI server (REST + WebSocket)
- CLI voice terminal

**Out of scope:** React web frontend (separate plan after backend is working).

## Architecture

Python 3.12+, FastAPI backend, Protocol-based provider interfaces. Each AI module (ASR/TTS/LLM/VAD/WakeWord) implements a Protocol so it can be swapped independently. BabelEngine orchestrates the pipeline: WakeWord → VAD → ASR → LLM → TTS. SQLite for persistence, YAML for config.

## Tech Stack

- Python 3.12+, uv (package manager)
- FastAPI + uvicorn (API server)
- SQLite + aiosqlite (async DB)
- PyAudio (microphone/speakers)
- pyyaml (config)
- pytest + pytest-asyncio (testing)
- httpx (async HTTP client for Ollama/CosyVoice)

## File Structure

```
BabelBuddy/
├── pyproject.toml
├── config/
│   └── settings.yaml
├── src/
│   └── babel_buddy/
│       ├── __init__.py
│       ├── config.py                 # Settings loader
│       ├── models.py                 # Dataclasses + Protocol interfaces
│       ├── data/
│       │   ├── __init__.py
│       │   └── session_store.py      # SQLite async store
│       ├── llm/
│       │   ├── __init__.py
│       │   ├── ollama_client.py      # Ollama HTTP client
│       │   └── prompt.py             # Prompt template builder
│       ├── speech/
│       │   ├── __init__.py
│       │   ├── asr.py                # Whisper ASR provider
│       │   ├── tts.py                # CosyVoice TTS provider
│       │   ├── vad.py                # Silero VAD provider
│       │   └── wake_word.py          # Wake word provider
│       ├── core/
│       │   ├── __init__.py
│       │   ├── conversation.py       # Conversation manager + state machine
│       │   └── engine.py             # BabelEngine orchestrator
│       ├── api/
│       │   ├── __init__.py
│       │   ├── main.py               # FastAPI app factory
│       │   ├── routes.py             # REST routes
│       │   ├── websocket.py          # WebSocket handler
│       │   └── schemas.py            # Pydantic request/response models
│       └── terminal/
│           ├── __init__.py
│           └── voice_terminal.py     # CLI voice interaction
├── tests/
│   ├── conftest.py                   # Shared fixtures
│   ├── test_config.py
│   ├── test_models.py
│   ├── data/
│   │   └── test_session_store.py
│   ├── llm/
│   │   ├── test_ollama_client.py
│   │   └── test_prompt.py
│   ├── speech/
│   │   ├── test_asr.py
│   │   ├── test_tts.py
│   │   ├── test_vad.py
│   │   └── test_wake_word.py
│   ├── core/
│   │   ├── test_conversation.py
│   │   └── test_engine.py
│   └── api/
│       ├── test_routes.py
│       └── test_websocket.py
```

---

## Task 1: Project Scaffolding

**Files:**
- Create: `pyproject.toml`
- Create: `src/babel_buddy/__init__.py`
- Create: `config/settings.yaml`
- Create: `src/babel_buddy/config.py`
- Test: `tests/test_config.py`

### Steps

- [ ] **1.1: Create pyproject.toml**

```toml
[project]
name = "babel-buddy"
version = "0.1.0"
description = "Personal bilingual AI language buddy"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn>=0.34.0",
    "aiosqlite>=0.21.0",
    "pyyaml>=6.0",
    "httpx>=0.28.0",
]

[project.optional-dependencies]
speech = [
    "openai-whisper>=20240930",
    "silero-vad>=5.1",
    "pyaudio>=0.2.14",
]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.25.0",
    "pytest-httpx>=0.35.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

- [ ] **1.2: Create default settings.yaml**

```yaml
models:
  llm:
    name: "qwen2.5:32b"
    ollama_host: "http://localhost:11434"
    context_window: 20
  asr:
    model: "large-v3"
    device: "cpu"
  tts:
    host: "http://localhost:9880"
    voice_zh: "default_zh"
    voice_en: "default_en"

audio:
  sample_rate: 16000
  channels: 1
  chunk_size: 4096
  silence_timeout: 30

wake_word:
  engine: "porcupine"
  keyword: "hello_babel"

server:
  host: "0.0.0.0"
  port: 8000

storage:
  database: "data/sessions.db"
  audio_dir: "data/audio"
  audio_retention_days: 30
```

- [ ] **1.3: Write failing test for config loader**

```python
# tests/test_config.py
import pytest
from pathlib import Path
from babel_buddy.config import Settings, load_settings

def test_load_settings_from_yaml(tmp_path):
    yaml_content = """
models:
  llm:
    name: "qwen2.5:32b"
    ollama_host: "http://localhost:11434"
    context_window: 20
  asr:
    model: "large-v3"
    device: "cpu"
  tts:
    host: "http://localhost:9880"
    voice_zh: "default_zh"
    voice_en: "default_en"
audio:
  sample_rate: 16000
  channels: 1
  chunk_size: 4096
  silence_timeout: 30
server:
  host: "0.0.0.0"
  port: 8000
storage:
  database: "data/sessions.db"
  audio_dir: "data/audio"
  audio_retention_days: 30
"""
    config_file = tmp_path / "settings.yaml"
    config_file.write_text(yaml_content)
    settings = load_settings(config_file)
    assert settings.models.llm.name == "qwen2.5:32b"
    assert settings.audio.sample_rate == 16000
    assert settings.server.port == 8000

def test_load_settings_file_not_found():
    with pytest.raises(FileNotFoundError):
        load_settings(Path("/nonexistent/settings.yaml"))
```

- [ ] **1.4: Run test to verify it fails**

Run: `cd /Users/minimax/Workspace/github.com/Chever-John/Babel-Buddy && uv run pytest tests/test_config.py -v`
Expected: FAIL (module not found)

- [ ] **1.5: Implement config loader**

```python
# src/babel_buddy/config.py
from dataclasses import dataclass
from pathlib import Path
import yaml

@dataclass
class LLMConfig:
    name: str
    ollama_host: str
    context_window: int

@dataclass
class ASRConfig:
    model: str
    device: str

@dataclass
class TTSConfig:
    host: str
    voice_zh: str
    voice_en: str

@dataclass
class ModelsConfig:
    llm: LLMConfig
    asr: ASRConfig
    tts: TTSConfig

@dataclass
class AudioConfig:
    sample_rate: int
    channels: int
    chunk_size: int
    silence_timeout: int

@dataclass
class WakeWordConfig:
    engine: str
    keyword: str

@dataclass
class ServerConfig:
    host: str
    port: int

@dataclass
class StorageConfig:
    database: str
    audio_dir: str
    audio_retention_days: int

@dataclass
class Settings:
    models: ModelsConfig
    audio: AudioConfig
    wake_word: WakeWordConfig | None
    server: ServerConfig
    storage: StorageConfig

def load_settings(path: Path) -> Settings:
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    with open(path) as f:
        raw = yaml.safe_load(f)
    ww = raw.get("wake_word")
    return Settings(
        models=ModelsConfig(
            llm=LLMConfig(**raw["models"]["llm"]),
            asr=ASRConfig(**raw["models"]["asr"]),
            tts=TTSConfig(**raw["models"]["tts"]),
        ),
        audio=AudioConfig(**raw["audio"]),
        wake_word=WakeWordConfig(**ww) if ww else None,
        server=ServerConfig(**raw["server"]),
        storage=StorageConfig(**raw["storage"]),
    )
```

- [ ] **1.6: Run test to verify it passes**

Run: `uv run pytest tests/test_config.py -v`
Expected: PASS

- [ ] **1.7: Commit**

```bash
git add pyproject.toml config/ src/babel_buddy/__init__.py src/babel_buddy/config.py tests/test_config.py
git commit -m "feat: project scaffolding with config loader"
```

---

## Task 2: Data Models & Protocol Interfaces

**Files:**
- Create: `src/babel_buddy/models.py`
- Test: `tests/test_models.py`

### Steps

- [ ] **2.1: Write failing test for data models**

```python
# tests/test_models.py
from babel_buddy.models import (
    ASRResult, LLMResponse, Message, Session,
    ASRProvider, LLMProvider, TTSProvider, VADProvider, WakeWordProvider,
)
from datetime import datetime

def test_asr_result_creation():
    result = ASRResult(text="你好", language="zh", confidence=0.95)
    assert result.text == "你好"
    assert result.language == "zh"
    assert result.confidence == 0.95

def test_message_creation():
    msg = Message(
        id="test-id",
        session_id="session-1",
        role="user",
        content="Hello",
        translation=None,
        language="en",
        confidence=0.9,
        audio_path=None,
        created_at=datetime.now(),
    )
    assert msg.role == "user"
    assert msg.language == "en"

def test_llm_response():
    resp = LLMResponse(reply="你好！", translation="Hello!", language="zh")
    assert resp.reply == "你好！"
    assert resp.translation == "Hello!"
```

- [ ] **2.2: Run test to verify it fails**

Run: `uv run pytest tests/test_models.py -v`
Expected: FAIL

- [ ] **2.3: Implement models**

```python
# src/babel_buddy/models.py
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
```

- [ ] **2.4: Run test to verify it passes**

Run: `uv run pytest tests/test_models.py -v`
Expected: PASS

- [ ] **2.5: Commit**

```bash
git add src/babel_buddy/models.py tests/test_models.py
git commit -m "feat: data models and provider protocol interfaces"
```

---

## Task 3: SQLite Session Store

**Files:**
- Create: `src/babel_buddy/data/__init__.py`
- Create: `src/babel_buddy/data/session_store.py`
- Test: `tests/data/test_session_store.py`

### Steps

- [ ] **3.1: Write failing tests for session store**

```python
# tests/data/test_session_store.py
import pytest
from babel_buddy.data.session_store import SessionStore

@pytest.fixture
async def store(tmp_path):
    db_path = str(tmp_path / "test.db")
    s = SessionStore(db_path)
    await s.initialize()
    yield s
    await s.close()

async def test_create_and_get_session(store):
    session = await store.create_session()
    assert session.id is not None
    assert session.ended_at is None
    fetched = await store.get_session(session.id)
    assert fetched.id == session.id

async def test_end_session(store):
    session = await store.create_session()
    await store.end_session(session.id)
    fetched = await store.get_session(session.id)
    assert fetched.ended_at is not None

async def test_add_and_list_messages(store):
    session = await store.create_session()
    await store.add_message(
        session_id=session.id,
        role="user",
        content="你好",
        translation=None,
        language="zh",
        confidence=0.95,
        audio_path=None,
    )
    await store.add_message(
        session_id=session.id,
        role="assistant",
        content="你好！我是Babel",
        translation="Hello! I'm Babel",
        language="zh",
        confidence=None,
        audio_path=None,
    )
    messages = await store.get_messages(session.id)
    assert len(messages) == 2
    assert messages[0].role == "user"
    assert messages[1].role == "assistant"

async def test_list_sessions(store):
    await store.create_session()
    await store.create_session()
    sessions = await store.list_sessions()
    assert len(sessions) == 2

async def test_get_nonexistent_session(store):
    result = await store.get_session("nonexistent")
    assert result is None
```

- [ ] **3.2: Run test to verify it fails**

Run: `uv run pytest tests/data/test_session_store.py -v`
Expected: FAIL

- [ ] **3.3: Implement session store**

```python
# src/babel_buddy/data/session_store.py
import aiosqlite
from datetime import datetime
from uuid import uuid4
from babel_buddy.models import Session, Message

SCHEMA = """
CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,
    started_at TIMESTAMP NOT NULL,
    ended_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS messages (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    translation TEXT,
    language TEXT NOT NULL,
    confidence REAL,
    audio_path TEXT,
    created_at TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_messages_session_id ON messages(session_id);
CREATE INDEX IF NOT EXISTS idx_messages_language ON messages(language);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at);

CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TIMESTAMP NOT NULL
);

INSERT OR IGNORE INTO schema_version (version, applied_at) VALUES (1, CURRENT_TIMESTAMP);
"""

class SessionStore:
    def __init__(self, db_path: str):
        self._db_path = db_path
        self._db: aiosqlite.Connection | None = None

    async def initialize(self) -> None:
        self._db = await aiosqlite.connect(self._db_path)
        self._db.row_factory = aiosqlite.Row
        await self._db.executescript(SCHEMA)

    async def close(self) -> None:
        if self._db:
            await self._db.close()

    async def create_session(self) -> Session:
        session = Session(id=str(uuid4()), started_at=datetime.now())
        await self._db.execute(
            "INSERT INTO sessions (id, started_at) VALUES (?, ?)",
            (session.id, session.started_at.isoformat()),
        )
        await self._db.commit()
        return session

    async def end_session(self, session_id: str) -> None:
        now = datetime.now()
        await self._db.execute(
            "UPDATE sessions SET ended_at = ? WHERE id = ?",
            (now.isoformat(), session_id),
        )
        await self._db.commit()

    async def get_session(self, session_id: str) -> Session | None:
        cursor = await self._db.execute(
            "SELECT id, started_at, ended_at FROM sessions WHERE id = ?",
            (session_id,),
        )
        row = await cursor.fetchone()
        if row is None:
            return None
        return Session(
            id=row["id"],
            started_at=datetime.fromisoformat(row["started_at"]),
            ended_at=datetime.fromisoformat(row["ended_at"]) if row["ended_at"] else None,
        )

    async def list_sessions(self, limit: int = 50) -> list[Session]:
        cursor = await self._db.execute(
            "SELECT id, started_at, ended_at FROM sessions ORDER BY started_at DESC LIMIT ?",
            (limit,),
        )
        rows = await cursor.fetchall()
        return [
            Session(
                id=r["id"],
                started_at=datetime.fromisoformat(r["started_at"]),
                ended_at=datetime.fromisoformat(r["ended_at"]) if r["ended_at"] else None,
            )
            for r in rows
        ]

    async def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        translation: str | None,
        language: str,
        confidence: float | None,
        audio_path: str | None,
    ) -> Message:
        msg = Message(
            id=str(uuid4()),
            session_id=session_id,
            role=role,
            content=content,
            translation=translation,
            language=language,
            confidence=confidence,
            audio_path=audio_path,
            created_at=datetime.now(),
        )
        await self._db.execute(
            """INSERT INTO messages
               (id, session_id, role, content, translation, language, confidence, audio_path, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (msg.id, msg.session_id, msg.role, msg.content, msg.translation,
             msg.language, msg.confidence, msg.audio_path, msg.created_at.isoformat()),
        )
        await self._db.commit()
        return msg

    async def get_messages(self, session_id: str) -> list[Message]:
        cursor = await self._db.execute(
            "SELECT * FROM messages WHERE session_id = ? ORDER BY created_at",
            (session_id,),
        )
        rows = await cursor.fetchall()
        return [
            Message(
                id=r["id"],
                session_id=r["session_id"],
                role=r["role"],
                content=r["content"],
                translation=r["translation"],
                language=r["language"],
                confidence=r["confidence"],
                audio_path=r["audio_path"],
                created_at=datetime.fromisoformat(r["created_at"]),
            )
            for r in rows
        ]
```

- [ ] **3.4: Run tests to verify they pass**

Run: `uv run pytest tests/data/test_session_store.py -v`
Expected: ALL PASS

- [ ] **3.5: Commit**

```bash
git add src/babel_buddy/data/ tests/data/
git commit -m "feat: SQLite session store with async operations"
```

---

## Task 4: Prompt Template Builder

**Files:**
- Create: `src/babel_buddy/llm/__init__.py`
- Create: `src/babel_buddy/llm/prompt.py`
- Test: `tests/llm/test_prompt.py`

### Steps

- [ ] **4.1: Write failing tests**

```python
# tests/llm/test_prompt.py
from babel_buddy.llm.prompt import build_system_prompt, build_messages
from babel_buddy.models import Message
from datetime import datetime

def test_build_system_prompt_chinese():
    prompt = build_system_prompt("zh")
    assert "Chinese" in prompt or "zh" in prompt
    assert "Translation" in prompt

def test_build_system_prompt_english():
    prompt = build_system_prompt("en")
    assert "English" in prompt or "en" in prompt

def test_build_messages_includes_history():
    history = [
        Message(id="1", session_id="s1", role="user", content="Hello",
                translation=None, language="en", confidence=0.9,
                audio_path=None, created_at=datetime.now()),
        Message(id="2", session_id="s1", role="assistant",
                content="Hi there!", translation="你好！",
                language="en", confidence=None, audio_path=None,
                created_at=datetime.now()),
    ]
    messages = build_messages(history, "你好", "zh")
    assert messages[0]["role"] == "system"
    assert messages[-1]["role"] == "user"
    assert messages[-1]["content"] == "你好"

def test_build_messages_respects_context_window():
    history = [
        Message(id=str(i), session_id="s1", role="user", content=f"msg {i}",
                translation=None, language="en", confidence=0.9,
                audio_path=None, created_at=datetime.now())
        for i in range(30)
    ]
    messages = build_messages(history, "latest", "en", max_turns=20)
    # system + last 20 history + current user = 22
    assert len(messages) == 22
```

- [ ] **4.2: Run test to verify it fails**

Run: `uv run pytest tests/llm/test_prompt.py -v`
Expected: FAIL

- [ ] **4.3: Implement prompt builder**

```python
# src/babel_buddy/llm/prompt.py
from babel_buddy.models import Message

LANGUAGE_NAMES = {"zh": "Chinese", "en": "English"}

def build_system_prompt(detected_language: str) -> str:
    lang_name = LANGUAGE_NAMES.get(detected_language, detected_language)
    other_lang = "English" if detected_language == "zh" else "Chinese"
    return (
        f"You are Babel, a friendly bilingual buddy. "
        f"The user just spoke in {lang_name}. "
        f"Reply in {lang_name} naturally. "
        f"After your reply, provide a translation in {other_lang} "
        f"in the format: [Translation: ...]"
    )

def build_messages(
    history: list[Message],
    current_text: str,
    detected_language: str,
    max_turns: int = 20,
) -> list[dict]:
    system_msg = {"role": "system", "content": build_system_prompt(detected_language)}
    trimmed = history[-max_turns:] if len(history) > max_turns else history
    hist_msgs = [{"role": m.role, "content": m.content} for m in trimmed]
    user_msg = {"role": "user", "content": current_text}
    return [system_msg] + hist_msgs + [user_msg]
```

- [ ] **4.4: Run tests to verify they pass**

Run: `uv run pytest tests/llm/test_prompt.py -v`
Expected: PASS

- [ ] **4.5: Commit**

```bash
git add src/babel_buddy/llm/ tests/llm/
git commit -m "feat: LLM prompt template builder"
```

---

## Task 5: Ollama LLM Client

**Files:**
- Create: `src/babel_buddy/llm/ollama_client.py`
- Test: `tests/llm/test_ollama_client.py`

### Steps

- [ ] **5.1: Write failing tests**

```python
# tests/llm/test_ollama_client.py
import pytest
import json
from babel_buddy.llm.ollama_client import OllamaClient
from babel_buddy.models import LLMResponse

@pytest.fixture
def client():
    return OllamaClient(host="http://localhost:11434", model="qwen2.5:32b")

async def test_parse_response(client):
    raw_text = "你好！我是Babel。\n[Translation: Hello! I'm Babel.]"
    response = client.parse_response(raw_text, "zh")
    assert response.reply == "你好！我是Babel。"
    assert response.translation == "Hello! I'm Babel."
    assert response.language == "zh"

async def test_parse_response_no_translation(client):
    raw_text = "Just a plain reply without translation marker."
    response = client.parse_response(raw_text, "en")
    assert response.reply == "Just a plain reply without translation marker."
    assert response.translation == ""

async def test_chat_sends_correct_request(client, httpx_mock):
    httpx_mock.add_response(
        url="http://localhost:11434/api/chat",
        json={"message": {"content": "Hi!\n[Translation: 你好！]"}, "done": True},
    )
    messages = [
        {"role": "system", "content": "You are Babel."},
        {"role": "user", "content": "Hello"},
    ]
    response = await client.chat(messages)
    assert response.reply == "Hi!"
    assert "你好" in response.translation
```

- [ ] **5.2: Run test to verify it fails**

Run: `uv run pytest tests/llm/test_ollama_client.py -v`
Expected: FAIL

- [ ] **5.3: Implement Ollama client**

```python
# src/babel_buddy/llm/ollama_client.py
import json
import re
import httpx
from babel_buddy.models import LLMResponse
from typing import AsyncIterator

TRANSLATION_PATTERN = re.compile(r"\[Translation:\s*(.*?)\]\s*$", re.DOTALL)

class OllamaClient:
    def __init__(self, host: str, model: str, timeout: float = 30.0):
        self._host = host.rstrip("/")
        self._model = model
        self._timeout = timeout

    def parse_response(self, raw_text: str, language: str) -> LLMResponse:
        match = TRANSLATION_PATTERN.search(raw_text)
        if match:
            translation = match.group(1).strip()
            reply = raw_text[:match.start()].strip()
        else:
            reply = raw_text.strip()
            translation = ""
        return LLMResponse(reply=reply, translation=translation, language=language)

    async def chat(self, messages: list[dict]) -> LLMResponse:
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            resp = await client.post(
                f"{self._host}/api/chat",
                json={"model": self._model, "messages": messages, "stream": False},
            )
            resp.raise_for_status()
            data = resp.json()
            raw = data["message"]["content"]
            # Detect language from system prompt
            lang = "en"
            for m in messages:
                if m["role"] == "system" and "Chinese" in m["content"]:
                    lang = "zh"
                    break
            return self.parse_response(raw, lang)

    async def chat_stream(self, messages: list[dict]) -> AsyncIterator[str]:
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            async with client.stream(
                "POST",
                f"{self._host}/api/chat",
                json={"model": self._model, "messages": messages, "stream": True},
            ) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if line:
                        data = json.loads(line)
                        token = data.get("message", {}).get("content", "")
                        if token:
                            yield token
                        if data.get("done"):
                            break
```

- [ ] **5.4: Run tests to verify they pass**

Run: `uv run pytest tests/llm/test_ollama_client.py -v`
Expected: PASS

- [ ] **5.5: Commit**

```bash
git add src/babel_buddy/llm/ollama_client.py tests/llm/test_ollama_client.py
git commit -m "feat: Ollama LLM client with streaming support"
```

---

## Task 6: ASR Provider (Whisper)

**Files:**
- Create: `src/babel_buddy/speech/__init__.py`
- Create: `src/babel_buddy/speech/asr.py`
- Test: `tests/speech/test_asr.py`

### Steps

- [ ] **6.1: Write failing tests**

```python
# tests/speech/test_asr.py
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from babel_buddy.speech.asr import WhisperASR
from babel_buddy.models import ASRResult

def test_whisper_asr_implements_protocol():
    """WhisperASR should satisfy ASRProvider protocol."""
    asr = WhisperASR.__new__(WhisperASR)
    assert hasattr(asr, "transcribe")

@patch("babel_buddy.speech.asr.whisper")
def test_whisper_asr_init(mock_whisper):
    mock_whisper.load_model.return_value = MagicMock()
    asr = WhisperASR(model_name="base", device="cpu")
    mock_whisper.load_model.assert_called_once_with("base", device="cpu")

@patch("babel_buddy.speech.asr.whisper")
async def test_whisper_transcribe(mock_whisper):
    mock_model = MagicMock()
    mock_model.transcribe.return_value = {
        "text": " 你好世界",
        "language": "zh",
    }
    mock_whisper.load_model.return_value = mock_model
    asr = WhisperASR(model_name="base", device="cpu")
    result = await asr.transcribe(b"\x00" * 16000)
    assert isinstance(result, ASRResult)
    assert result.text == "你好世界"
    assert result.language == "zh"
```

- [ ] **6.2: Run test to verify it fails**

Run: `uv run pytest tests/speech/test_asr.py -v`
Expected: FAIL

- [ ] **6.3: Implement WhisperASR**

```python
# src/babel_buddy/speech/asr.py
import asyncio
import tempfile
import wave
from pathlib import Path
from babel_buddy.models import ASRResult

try:
    import whisper
except ImportError:
    whisper = None

class WhisperASR:
    def __init__(self, model_name: str = "large-v3", device: str = "cpu"):
        if whisper is None:
            raise RuntimeError("openai-whisper is not installed. Install with: pip install openai-whisper")
        self._model = whisper.load_model(model_name, device=device)

    async def transcribe(self, audio: bytes, sample_rate: int = 16000) -> ASRResult:
        # Write PCM bytes to a temporary WAV file for Whisper
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            tmp_path = f.name
            with wave.open(f, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)  # 16-bit
                wf.setframerate(sample_rate)
                wf.writeframes(audio)
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, lambda: self._model.transcribe(tmp_path)
            )
        finally:
            Path(tmp_path).unlink(missing_ok=True)
        text = result.get("text", "").strip()
        language = result.get("language", "en")
        # Whisper doesn't return a single confidence; use segments average
        segments = result.get("segments", [])
        if segments:
            confidence = sum(s.get("no_speech_prob", 0) for s in segments) / len(segments)
            confidence = 1.0 - confidence  # invert: high no_speech_prob = low confidence
        else:
            confidence = 0.0
        return ASRResult(text=text, language=language, confidence=confidence)
```

- [ ] **6.4: Run tests to verify they pass**

Run: `uv run pytest tests/speech/test_asr.py -v`
Expected: PASS

- [ ] **6.5: Commit**

```bash
git add src/babel_buddy/speech/ tests/speech/
git commit -m "feat: Whisper ASR provider with language detection"
```

---

## Task 7: TTS Provider (CosyVoice HTTP Client)

**Files:**
- Create: `src/babel_buddy/speech/tts.py`
- Test: `tests/speech/test_tts.py`

### Steps

- [ ] **7.1: Write failing tests**

```python
# tests/speech/test_tts.py
import pytest
from babel_buddy.speech.tts import CosyVoiceTTS

@pytest.fixture
def tts():
    return CosyVoiceTTS(host="http://localhost:9880", voice_zh="zh_voice", voice_en="en_voice")

async def test_synthesize(tts, httpx_mock):
    httpx_mock.add_response(
        url="http://localhost:9880/api/tts",
        content=b"\x00\x01\x02\x03",
        headers={"content-type": "audio/pcm"},
    )
    audio = await tts.synthesize("你好", "zh")
    assert audio == b"\x00\x01\x02\x03"
    request = httpx_mock.get_request()
    assert "zh_voice" in request.content.decode()

async def test_synthesize_english(tts, httpx_mock):
    httpx_mock.add_response(
        url="http://localhost:9880/api/tts",
        content=b"\x04\x05\x06",
    )
    audio = await tts.synthesize("Hello", "en")
    assert audio == b"\x04\x05\x06"
    request = httpx_mock.get_request()
    assert "en_voice" in request.content.decode()

async def test_synthesize_service_unavailable(tts, httpx_mock):
    import httpx as httpx_lib
    httpx_mock.add_exception(httpx_lib.ConnectError("Connection refused"))
    with pytest.raises(ConnectionError):
        await tts.synthesize("Hello", "en")
```

- [ ] **7.2: Run test, verify fail. 7.3: Implement**

```python
# src/babel_buddy/speech/tts.py
import httpx
import json

class CosyVoiceTTS:
    def __init__(self, host: str, voice_zh: str, voice_en: str, timeout: float = 10.0):
        self._host = host.rstrip("/")
        self._voice_zh = voice_zh
        self._voice_en = voice_en
        self._timeout = timeout

    def _voice_for(self, language: str) -> str:
        return self._voice_zh if language == "zh" else self._voice_en

    async def synthesize(self, text: str, language: str) -> bytes:
        voice = self._voice_for(language)
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                resp = await client.post(
                    f"{self._host}/api/tts",
                    json={"text": text, "voice": voice, "language": language},
                )
                resp.raise_for_status()
                return resp.content
        except httpx.ConnectError as e:
            raise ConnectionError(f"CosyVoice service unavailable at {self._host}: {e}")
```

- [ ] **7.4: Run tests, verify pass. 7.5: Commit**

```bash
git add src/babel_buddy/speech/tts.py tests/speech/test_tts.py
git commit -m "feat: CosyVoice TTS HTTP client"
```

---

## Task 8: VAD Provider (Silero)

**Files:**
- Create: `src/babel_buddy/speech/vad.py`
- Test: `tests/speech/test_vad.py`

### Steps

- [ ] **8.1: Write failing tests**

```python
# tests/speech/test_vad.py
import pytest
from unittest.mock import MagicMock, patch
from babel_buddy.speech.vad import SileroVAD

@patch("babel_buddy.speech.vad.torch")
def test_silero_vad_is_speech_true(mock_torch):
    mock_model = MagicMock()
    mock_model.return_value = MagicMock(item=MagicMock(return_value=0.8))
    with patch("babel_buddy.speech.vad.SileroVAD._load_model", return_value=mock_model):
        vad = SileroVAD()
        vad._model = mock_model
        vad._threshold = 0.5
        # Mock tensor creation
        mock_torch.frombuffer.return_value = MagicMock()
        mock_torch.frombuffer.return_value.float.return_value = MagicMock(__truediv__=lambda s, o: s)
        assert vad.is_speech(b"\x00" * 1024) is True

def test_silero_vad_implements_protocol():
    vad = SileroVAD.__new__(SileroVAD)
    assert hasattr(vad, "is_speech")
```

- [ ] **8.2: Implement SileroVAD**

```python
# src/babel_buddy/speech/vad.py
try:
    import torch
except ImportError:
    torch = None

class SileroVAD:
    def __init__(self, threshold: float = 0.5, sample_rate: int = 16000):
        self._threshold = threshold
        self._sample_rate = sample_rate
        self._model = self._load_model()

    @staticmethod
    def _load_model():
        if torch is None:
            raise RuntimeError("torch is not installed")
        model, _ = torch.hub.load("snakers4/silero-vad", "silero_vad")
        model.eval()
        return model

    def is_speech(self, audio_chunk: bytes) -> bool:
        if torch is None:
            return True  # fallback: assume speech
        tensor = torch.frombuffer(audio_chunk, dtype=torch.int16).float() / 32768.0
        confidence = self._model(tensor, self._sample_rate).item()
        return confidence >= self._threshold
```

- [ ] **8.3: Run tests, verify pass. 8.4: Commit**

```bash
git add src/babel_buddy/speech/vad.py tests/speech/test_vad.py
git commit -m "feat: Silero VAD provider"
```

---

## Task 9: Wake Word Provider

**Files:**
- Create: `src/babel_buddy/speech/wake_word.py`
- Test: `tests/speech/test_wake_word.py`

### Steps

- [ ] **9.1: Write failing tests**

```python
# tests/speech/test_wake_word.py
from babel_buddy.speech.wake_word import KeyboardWakeWord

def test_keyboard_wake_word_detect():
    """Keyboard fallback always returns False (user presses Enter separately)."""
    ww = KeyboardWakeWord()
    assert ww.detect(b"\x00" * 1024) is False

def test_keyboard_wake_word_trigger():
    ww = KeyboardWakeWord()
    ww.trigger()
    assert ww.detect(b"") is True
    # Second call resets
    assert ww.detect(b"") is False
```

- [ ] **9.2: Implement wake word (keyboard fallback for Phase 1 dev)**

```python
# src/babel_buddy/speech/wake_word.py

class KeyboardWakeWord:
    """Fallback wake word: triggered by keyboard input (Enter key).
    Porcupine/openWakeWord integration is a future enhancement.
    """
    def __init__(self):
        self._triggered = False

    def trigger(self) -> None:
        self._triggered = True

    def detect(self, audio_chunk: bytes) -> bool:
        if self._triggered:
            self._triggered = False
            return True
        return False
```

- [ ] **9.3: Run tests, verify pass. 9.4: Commit**

```bash
git add src/babel_buddy/speech/wake_word.py tests/speech/test_wake_word.py
git commit -m "feat: keyboard-based wake word fallback"
```

---

## Task 10: Conversation Manager (State Machine)

**Files:**
- Create: `src/babel_buddy/core/__init__.py`
- Create: `src/babel_buddy/core/conversation.py`
- Test: `tests/core/test_conversation.py`

### Steps

- [ ] **10.1: Write failing tests**

```python
# tests/core/test_conversation.py
import pytest
from babel_buddy.core.conversation import ConversationManager, ConversationState

def test_initial_state_is_idle():
    cm = ConversationManager()
    assert cm.state == ConversationState.IDLE

def test_activate_transitions_to_listening():
    cm = ConversationManager()
    cm.activate()
    assert cm.state == ConversationState.LISTENING

def test_speech_received_transitions_to_processing():
    cm = ConversationManager()
    cm.activate()
    cm.speech_received()
    assert cm.state == ConversationState.PROCESSING

def test_response_ready_transitions_to_speaking():
    cm = ConversationManager()
    cm.activate()
    cm.speech_received()
    cm.response_ready()
    assert cm.state == ConversationState.SPEAKING

def test_done_speaking_transitions_to_listening():
    cm = ConversationManager()
    cm.activate()
    cm.speech_received()
    cm.response_ready()
    cm.done_speaking()
    assert cm.state == ConversationState.LISTENING

def test_deactivate_returns_to_idle():
    cm = ConversationManager()
    cm.activate()
    cm.deactivate()
    assert cm.state == ConversationState.IDLE

def test_context_window_management():
    cm = ConversationManager(max_turns=3)
    for i in range(5):
        cm.add_turn(role="user", content=f"msg {i}", language="en")
    assert len(cm.history) == 3
    assert cm.history[0].content == "msg 2"

def test_is_exit_phrase():
    cm = ConversationManager()
    assert cm.is_exit_phrase("bye babel") is True
    assert cm.is_exit_phrase("Bye Babel!") is True
    assert cm.is_exit_phrase("hello") is False

def test_invalid_transition_raises():
    cm = ConversationManager()
    with pytest.raises(ValueError):
        cm.speech_received()  # Can't go from IDLE to PROCESSING
```

- [ ] **10.2: Implement conversation manager**

```python
# src/babel_buddy/core/conversation.py
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
            role=role,
            content=content,
            translation=translation,
            language=language,
            confidence=confidence,
            audio_path=None,
            created_at=datetime.now(),
        )
        self._history.append(msg)
        self._last_language = language
        # Trim to max_turns
        if len(self._history) > self._max_turns:
            self._history = self._history[-self._max_turns:]

    @staticmethod
    def is_exit_phrase(text: str) -> bool:
        normalized = text.strip().lower().rstrip("!.,?")
        return normalized in EXIT_PHRASES
```

- [ ] **10.3: Run tests, verify pass. 10.4: Commit**

```bash
git add src/babel_buddy/core/ tests/core/
git commit -m "feat: conversation manager with state machine"
```

---

## Task 11: BabelEngine Orchestrator

**Files:**
- Create: `src/babel_buddy/core/engine.py`
- Test: `tests/core/test_engine.py`

### Steps

- [ ] **11.1: Write failing tests**

```python
# tests/core/test_engine.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from babel_buddy.core.engine import BabelEngine
from babel_buddy.core.conversation import ConversationState
from babel_buddy.models import ASRResult, LLMResponse

@pytest.fixture
def mock_providers():
    asr = AsyncMock()
    asr.transcribe.return_value = ASRResult(text="你好", language="zh", confidence=0.95)
    llm = AsyncMock()
    llm.chat.return_value = LLMResponse(reply="你好！", translation="Hello!", language="zh")
    tts = AsyncMock()
    tts.synthesize.return_value = b"\x00\x01\x02"
    vad = MagicMock()
    vad.is_speech.return_value = True
    store = AsyncMock()
    store.create_session.return_value = MagicMock(id="session-1")
    return {"asr": asr, "llm": llm, "tts": tts, "vad": vad, "store": store}

@pytest.fixture
def engine(mock_providers):
    return BabelEngine(
        asr=mock_providers["asr"],
        llm=mock_providers["llm"],
        tts=mock_providers["tts"],
        vad=mock_providers["vad"],
        session_store=mock_providers["store"],
    )

async def test_process_audio_turn(engine, mock_providers):
    await engine.start_session()
    result = await engine.process_audio(b"\x00" * 4096)
    assert result.reply == "你好！"
    assert result.audio is not None
    mock_providers["asr"].transcribe.assert_called_once()
    mock_providers["tts"].synthesize.assert_called_once()

async def test_process_detects_exit_phrase(engine, mock_providers):
    mock_providers["asr"].transcribe.return_value = ASRResult(
        text="bye babel", language="en", confidence=0.9
    )
    await engine.start_session()
    result = await engine.process_audio(b"\x00" * 4096)
    assert result.is_exit is True

async def test_start_session(engine):
    await engine.start_session()
    assert engine.conversation.state == ConversationState.LISTENING

async def test_process_text(engine, mock_providers):
    await engine.start_session()
    result = await engine.process_text("你好", "zh")
    assert result.reply == "你好！"
    assert result.language == "zh"
    mock_providers["llm"].chat.assert_called_once()

async def test_process_text_auto_detect_chinese(engine, mock_providers):
    await engine.start_session()
    result = await engine.process_text("你好世界", "auto")
    assert result.language == "zh"

async def test_process_text_auto_detect_english(engine, mock_providers):
    await engine.start_session()
    result = await engine.process_text("hello world", "auto")
    assert result.language == "en"

async def test_process_text_exit_phrase(engine, mock_providers):
    await engine.start_session()
    result = await engine.process_text("bye babel")
    assert result.is_exit is True
```

- [ ] **11.2: Implement BabelEngine**

```python
# src/babel_buddy/core/engine.py
from dataclasses import dataclass
from babel_buddy.core.conversation import ConversationManager
from babel_buddy.models import ASRResult, LLMResponse
from babel_buddy.llm.prompt import build_messages

@dataclass
class TurnResult:
    transcript: str
    language: str
    reply: str
    translation: str
    audio: bytes | None
    is_exit: bool = False

class BabelEngine:
    def __init__(self, asr, llm, tts, vad, session_store, max_turns: int = 20):
        self._asr = asr
        self._llm = llm
        self._tts = tts
        self._vad = vad
        self._store = session_store
        self.conversation = ConversationManager(max_turns=max_turns)

    async def start_session(self) -> str:
        session = await self._store.create_session()
        self.conversation.activate()
        self.conversation.session_id = session.id
        return session.id

    async def end_session(self) -> None:
        if self.conversation.session_id:
            await self._store.end_session(self.conversation.session_id)
        self.conversation.deactivate()

    async def process_audio(self, audio: bytes) -> TurnResult:
        self.conversation.speech_received()

        # ASR
        asr_result = await self._asr.transcribe(audio)

        # Check for exit phrase
        if self.conversation.is_exit_phrase(asr_result.text):
            await self.end_session()
            return TurnResult(
                transcript=asr_result.text,
                language=asr_result.language,
                reply="See you next time!",
                translation="下次见！" if asr_result.language == "en" else "See you next time!",
                audio=None,
                is_exit=True,
            )

        # Save user message
        self.conversation.add_turn(
            role="user", content=asr_result.text,
            language=asr_result.language, confidence=asr_result.confidence,
        )
        await self._store.add_message(
            session_id=self.conversation.session_id,
            role="user", content=asr_result.text, translation=None,
            language=asr_result.language, confidence=asr_result.confidence,
            audio_path=None,
        )

        # LLM
        messages = build_messages(
            self.conversation.history, asr_result.text, asr_result.language,
        )
        llm_response = await self._llm.chat(messages)
        self.conversation.response_ready()

        # Save assistant message
        self.conversation.add_turn(
            role="assistant", content=llm_response.reply,
            language=llm_response.language, translation=llm_response.translation,
        )
        await self._store.add_message(
            session_id=self.conversation.session_id,
            role="assistant", content=llm_response.reply,
            translation=llm_response.translation,
            language=llm_response.language, confidence=None, audio_path=None,
        )

        # TTS
        audio_out = await self._tts.synthesize(llm_response.reply, llm_response.language)
        self.conversation.done_speaking()

        return TurnResult(
            transcript=asr_result.text,
            language=asr_result.language,
            reply=llm_response.reply,
            translation=llm_response.translation,
            audio=audio_out,
        )

    async def process_text(self, text: str, language: str = "auto") -> TurnResult:
        """Process a text message directly (no ASR needed)."""
        if language == "auto":
            cjk = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
            language = "zh" if cjk / max(len(text), 1) > 0.3 else "en"

        if self.conversation.is_exit_phrase(text):
            await self.end_session()
            return TurnResult(
                transcript=text, language=language,
                reply="See you next time!",
                translation="下次见！" if language == "en" else "See you next time!",
                audio=None, is_exit=True,
            )

        self.conversation.speech_received()
        self.conversation.add_turn(role="user", content=text, language=language)

        messages = build_messages(self.conversation.history, text, language)
        llm_response = await self._llm.chat(messages)
        self.conversation.response_ready()

        self.conversation.add_turn(
            role="assistant", content=llm_response.reply,
            language=llm_response.language, translation=llm_response.translation,
        )
        self.conversation.done_speaking()

        return TurnResult(
            transcript=text, language=language,
            reply=llm_response.reply,
            translation=llm_response.translation, audio=None,
        )
```

- [ ] **11.3: Run tests, verify pass. 11.4: Commit**

```bash
git add src/babel_buddy/core/engine.py tests/core/test_engine.py
git commit -m "feat: BabelEngine orchestrator"
```

---

## Task 12: FastAPI App + REST Routes

**Files:**
- Create: `src/babel_buddy/api/__init__.py`
- Create: `src/babel_buddy/api/schemas.py`
- Create: `src/babel_buddy/api/routes.py`
- Create: `src/babel_buddy/api/main.py`
- Test: `tests/api/test_routes.py`

### Steps

- [ ] **12.1: Write failing tests**

```python
# tests/api/test_routes.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from httpx import AsyncClient, ASGITransport
from babel_buddy.api.main import create_app
from babel_buddy.models import LLMResponse

@pytest.fixture
def mock_engine():
    engine = AsyncMock()
    engine.conversation = MagicMock()
    engine.conversation.history = []
    engine.conversation.state = MagicMock(value="idle")
    return engine

@pytest.fixture
def mock_store():
    store = AsyncMock()
    store.list_sessions.return_value = []
    store.get_session.return_value = None
    store.get_messages.return_value = []
    return store

@pytest.fixture
async def client(mock_engine, mock_store):
    app = create_app(engine=mock_engine, session_store=mock_store)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c

async def test_health_check(client):
    resp = await client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert "status" in data

async def test_list_sessions(client):
    resp = await client.get("/api/sessions")
    assert resp.status_code == 200
    assert resp.json() == []

async def test_chat_endpoint(client, mock_engine):
    from babel_buddy.core.engine import TurnResult
    mock_engine.process_text.return_value = TurnResult(
        transcript="Hello", language="en",
        reply="Hi there!", translation="你好！",
        audio=None,
    )
    resp = await client.post("/api/chat", json={"text": "Hello", "language": "en"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["reply"] == "Hi there!"
```

- [ ] **12.2: Implement schemas**

```python
# src/babel_buddy/api/schemas.py
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
```

- [ ] **12.3: Implement routes**

```python
# src/babel_buddy/api/routes.py
from fastapi import APIRouter, HTTPException
from babel_buddy.api.schemas import (
    ChatRequest, ChatResponse, SessionResponse, MessageResponse, HealthResponse,
)

def create_router(engine, session_store) -> APIRouter:
    router = APIRouter(prefix="/api")

    @router.get("/health", response_model=HealthResponse)
    async def health():
        return HealthResponse(
            status="ok",
            state=engine.conversation.state.value,
        )

    @router.get("/sessions", response_model=list[SessionResponse])
    async def list_sessions():
        sessions = await session_store.list_sessions()
        return [
            SessionResponse(
                id=s.id,
                started_at=s.started_at.isoformat(),
                ended_at=s.ended_at.isoformat() if s.ended_at else None,
            )
            for s in sessions
        ]

    @router.get("/sessions/{session_id}")
    async def get_session(session_id: str):
        session = await session_store.get_session(session_id)
        if session is None:
            raise HTTPException(status_code=404, detail="Session not found")
        messages = await session_store.get_messages(session_id)
        return {
            "session": SessionResponse(
                id=session.id,
                started_at=session.started_at.isoformat(),
                ended_at=session.ended_at.isoformat() if session.ended_at else None,
            ),
            "messages": [
                MessageResponse(
                    id=m.id, role=m.role, content=m.content,
                    translation=m.translation, language=m.language,
                    created_at=m.created_at.isoformat(),
                )
                for m in messages
            ],
        }

    @router.post("/chat", response_model=ChatResponse)
    async def chat(req: ChatRequest):
        result = await engine.process_text(req.text, req.language)
        return ChatResponse(
            reply=result.reply,
            translation=result.translation,
            language=result.language,
        )

    return router
```

- [ ] **12.4: Implement app factory**

```python
# src/babel_buddy/api/main.py
from fastapi import FastAPI
from babel_buddy.api.routes import create_router

def create_app(engine=None, session_store=None) -> FastAPI:
    app = FastAPI(title="BabelBuddy", version="0.1.0")
    router = create_router(engine, session_store)
    app.include_router(router)
    return app
```

- [ ] **12.5: Run tests, verify pass. 12.6: Commit**

```bash
git add src/babel_buddy/api/ tests/api/
git commit -m "feat: FastAPI REST routes for chat, sessions, health"
```

---

## Task 13: WebSocket Handler

**Files:**
- Create: `src/babel_buddy/api/websocket.py`
- Modify: `src/babel_buddy/api/main.py` (add WS route)
- Test: `tests/api/test_websocket.py`

### Steps

- [ ] **13.1: Write failing tests**

```python
# tests/api/test_websocket.py
import pytest
import json
import base64
from unittest.mock import AsyncMock, MagicMock
from httpx import ASGITransport, AsyncClient
from starlette.testclient import TestClient
from babel_buddy.api.main import create_app
from babel_buddy.core.engine import TurnResult

@pytest.fixture
def mock_engine():
    engine = AsyncMock()
    engine.conversation = MagicMock()
    engine.conversation.state = MagicMock(value="idle")
    engine.start_session.return_value = "session-1"
    engine.process_audio.return_value = TurnResult(
        transcript="你好", language="zh",
        reply="你好！", translation="Hello!",
        audio=b"\x00\x01",
    )
    return engine

def test_websocket_chat_flow(mock_engine):
    app = create_app(engine=mock_engine, session_store=AsyncMock())
    client = TestClient(app)
    with client.websocket_connect("/api/ws/chat") as ws:
        # Start session
        ws.send_json({"type": "control", "action": "start_session"})
        resp = ws.receive_json()
        assert resp["type"] == "state"

        # Send audio
        audio_b64 = base64.b64encode(b"\x00" * 4096).decode()
        ws.send_json({"type": "audio", "data": audio_b64})
        # Should get transcript, reply, audio, and state messages
        messages = []
        for _ in range(4):
            messages.append(ws.receive_json())
        types = {m["type"] for m in messages}
        assert "transcript" in types
        assert "reply" in types
```

- [ ] **13.2: Implement WebSocket handler**

```python
# src/babel_buddy/api/websocket.py
import base64
import json
from fastapi import WebSocket, WebSocketDisconnect

async def websocket_chat(ws: WebSocket, engine):
    await ws.accept()
    try:
        while True:
            raw = await ws.receive_text()
            msg = json.loads(raw)

            if msg["type"] == "control":
                if msg["action"] == "start_session":
                    session_id = await engine.start_session()
                    await ws.send_json({"type": "state", "state": "listening", "session_id": session_id})
                elif msg["action"] == "end_session":
                    await engine.end_session()
                    await ws.send_json({"type": "state", "state": "idle"})
                    break

            elif msg["type"] == "audio":
                audio_bytes = base64.b64decode(msg["data"])
                await ws.send_json({"type": "state", "state": "processing"})

                result = await engine.process_audio(audio_bytes)

                await ws.send_json({
                    "type": "transcript",
                    "text": result.transcript,
                    "language": result.language,
                })

                if result.is_exit:
                    await ws.send_json({"type": "state", "state": "idle"})
                    break

                await ws.send_json({
                    "type": "reply",
                    "text": result.reply,
                    "translation": result.translation,
                    "language": result.language,
                })

                if result.audio:
                    audio_b64 = base64.b64encode(result.audio).decode()
                    await ws.send_json({"type": "audio", "data": audio_b64})

                await ws.send_json({"type": "state", "state": "listening"})

    except WebSocketDisconnect:
        await engine.end_session()
```

- [ ] **13.3: Wire WebSocket into app factory**

```python
# Update src/babel_buddy/api/main.py - add:
from fastapi import WebSocket
from babel_buddy.api.websocket import websocket_chat

# Inside create_app, after include_router:
@app.websocket("/api/ws/chat")
async def ws_chat(ws: WebSocket):
    await websocket_chat(ws, engine)
```

- [ ] **13.4: Run tests, verify pass. 13.5: Commit**

```bash
git add src/babel_buddy/api/websocket.py src/babel_buddy/api/main.py tests/api/test_websocket.py
git commit -m "feat: WebSocket handler for real-time voice chat"
```

---

## Task 14: CLI Voice Terminal

**Files:**
- Create: `src/babel_buddy/terminal/__init__.py`
- Create: `src/babel_buddy/terminal/voice_terminal.py`
- No unit test (interactive I/O) — manual integration test

### Steps

- [ ] **14.1: Implement CLI voice terminal**

```python
# src/babel_buddy/terminal/voice_terminal.py
import asyncio
import sys
from pathlib import Path
from babel_buddy.config import load_settings
from babel_buddy.data.session_store import SessionStore
from babel_buddy.llm.ollama_client import OllamaClient
from babel_buddy.speech.wake_word import KeyboardWakeWord
from babel_buddy.core.engine import BabelEngine

class TextTerminal:
    """Text-only terminal for development/testing without audio hardware."""

    def __init__(self, engine: BabelEngine):
        self._engine = engine

    async def run(self) -> None:
        print("🗣️  BabelBuddy Text Terminal")
        print("Press Enter to start a session. Type 'quit' to exit.\n")

        while True:
            cmd = await asyncio.get_event_loop().run_in_executor(None, input, "> ")
            if cmd.strip().lower() == "quit":
                break

            if self._engine.conversation.state.value == "idle":
                await self._engine.start_session()
                print("🔔 Session started! Type your message.\n")
                continue

            result = await self._engine.process_text(cmd.strip(), "auto")
            print(f"\n📝 [{result.language}] {result.reply}")
            if result.translation:
                print(f"🔄 [Translation] {result.translation}")
            print()

            if result.is_exit:
                print("👋 Session ended.\n")

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
```

Note: `process_text` is already implemented in Task 11 as part of BabelEngine.

- [ ] **14.2: Commit**

```bash
git add src/babel_buddy/terminal/ src/babel_buddy/core/engine.py
git commit -m "feat: text-only CLI terminal for development"
```

---

## Task 15: Integration Wiring & Entry Point

**Files:**
- Modify: `pyproject.toml` (add script entry points)
- Create: `src/babel_buddy/__main__.py`
- Create: `tests/conftest.py`

### Steps

- [ ] **15.1: Add entry points to pyproject.toml**

```toml
# Add to [project] section:
[project.scripts]
babel-buddy = "babel_buddy.__main__:main"
```

- [ ] **15.2: Create __main__.py**

```python
# src/babel_buddy/__main__.py
import asyncio
import sys
from pathlib import Path

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "serve":
        # Run FastAPI server
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
        # Run text terminal
        from babel_buddy.terminal.voice_terminal import main as terminal_main
        asyncio.run(terminal_main())

if __name__ == "__main__":
    main()
```

- [ ] **15.3: Create shared test fixtures**

```python
# tests/conftest.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from babel_buddy.models import ASRResult, LLMResponse

@pytest.fixture
def mock_asr():
    asr = AsyncMock()
    asr.transcribe.return_value = ASRResult(text="hello", language="en", confidence=0.95)
    return asr

@pytest.fixture
def mock_llm():
    llm = AsyncMock()
    llm.chat.return_value = LLMResponse(reply="Hi!", translation="你好！", language="en")
    return llm

@pytest.fixture
def mock_tts():
    tts = AsyncMock()
    tts.synthesize.return_value = b"\x00\x01\x02"
    return tts

@pytest.fixture
def mock_vad():
    vad = MagicMock()
    vad.is_speech.return_value = True
    return vad
```

- [ ] **15.4: Run full test suite**

Run: `uv run pytest tests/ -v`
Expected: ALL PASS

- [ ] **15.5: Commit**

```bash
git add pyproject.toml src/babel_buddy/__main__.py tests/conftest.py
git commit -m "feat: entry points and shared test fixtures"
```

---

## Verification

After all tasks are complete:

1. **Run full test suite**: `uv run pytest tests/ -v --tb=short`
2. **Text terminal smoke test**: `uv run babel-buddy` (requires Ollama running)
3. **API server smoke test**: `uv run babel-buddy serve` → `curl http://localhost:8000/api/health`
4. **Check all `__init__.py` files exist**: `find src -name "*.py" | head -30`

## Summary

| Task | Component | Files | Dependencies |
|------|-----------|-------|--------------|
| 1 | Project scaffolding + config | 4 | None |
| 2 | Data models + protocols | 1 | Task 1 |
| 3 | SQLite session store | 1 | Task 2 |
| 4 | Prompt template builder | 1 | Task 2 |
| 5 | Ollama LLM client | 1 | Task 2, 4 |
| 6 | Whisper ASR | 1 | Task 2 |
| 7 | CosyVoice TTS | 1 | Task 2 |
| 8 | Silero VAD | 1 | Task 2 |
| 9 | Wake Word | 1 | Task 2 |
| 10 | Conversation Manager | 1 | Task 2 |
| 11 | BabelEngine | 1 | Task 3-10 |
| 12 | FastAPI REST routes | 4 | Task 11 |
| 13 | WebSocket handler | 1 | Task 11, 12 |
| 14 | CLI Terminal | 1 | Task 11 |
| 15 | Entry point + wiring | 2 | All |
