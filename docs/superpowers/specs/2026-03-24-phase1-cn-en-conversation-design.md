# BabelBuddy Phase 1 Design: Chinese-English Seamless Conversation

## Overview

Phase 1 implements the core experience: a bilingual AI buddy that automatically detects whether you're speaking Chinese or English and responds in the same language, with real-time voice interaction and translation display.

## Core Requirements

| Item | Decision |
|---|---|
| Wake Word | "Hello Babel" |
| Exit Phrase | "Bye Babel" (detected via ASR, not wake word engine) |
| Languages | Phase 1: Chinese + English |
| Language Switching | Auto-detect, respond in the same language the user speaks |
| Persona | Friendly, casual bilingual buddy |
| Output | Voice + original text + translation |
| Clients | CLI terminal + Web page |
| Hardware | Apple Silicon Mac (Phase 1) |
| History | Save and browse past conversations |
| Silence Timeout | 30 seconds of silence exits conversation mode |

## Performance Targets

| Stage | Latency Budget | Notes |
|---|---|---|
| VAD detection | < 100ms | Real-time, streaming |
| ASR (Whisper) | < 1.5s | For typical utterance (3-10s audio) |
| LLM first token | < 1s | Ollama streaming mode |
| LLM full response | < 5s | ~50-100 tokens at 10-20 tok/s on Apple Silicon |
| TTS synthesis | < 1s | Streaming: begin playback before full synthesis |
| **End-to-end** | **< 3s perceived** | Use LLM streaming → TTS streaming pipeline |

**Key optimization**: Stream LLM output to TTS in chunks — begin speaking the first sentence while the LLM is still generating the rest. This reduces perceived latency from ~8s to ~3s.

## Data Flow

### Conversation Flow

```
User speaks → [Silero VAD: detect voice activity] → [Whisper ASR: transcribe + detect language]
    → [Conversation Manager: assemble prompt with language instruction]
    → [Ollama/Qwen2.5: stream reply + translation]
    → [CosyVoice TTS: stream text to speech in chunks]
    → Output: voice playback + screen display (original text + translation)
```

### Wake Word Flow

```
Microphone always listening → [Porcupine: detect "Hello Babel"]
    → Play chime + display "I'm listening..."
    → Enter conversation mode (VAD → ASR → LLM → TTS loop)
    → Exit triggers:
        1. User says "Bye Babel" (detected via ASR after transcription)
        2. 30 seconds of continuous silence (no VAD activity)
    → Play farewell chime + display "See you next time!"
    → Return to wake word listening mode
```

### Conversation State Machine

```
    ┌──────────┐  "Hello Babel"   ┌───────────┐
    │   IDLE   │ ───────────────→ │ LISTENING  │ ←──────────┐
    └──────────┘                  └─────┬─────┘             │
         ↑                              │ VAD detects       │
         │                              │ speech end        │
         │                        ┌─────▼──────┐           │
         │                        │ PROCESSING  │           │
         │                        │ (ASR→LLM)   │           │
         │                        └─────┬──────┘           │
         │                              │                   │
         │                        ┌─────▼──────┐           │
         │                        │  SPEAKING   │ ──────────┘
         │                        │  (TTS out)  │  TTS done
         │                        └─────┬──────┘
         │                              │
         │  "Bye Babel" or timeout      │
         └──────────────────────────────┘
```

States:
- **IDLE**: Only wake word engine is active, minimal resource usage
- **LISTENING**: VAD active, capturing user audio, waiting for speech to end
- **PROCESSING**: ASR transcribing → LLM generating → preparing response
- **SPEAKING**: TTS playing audio output, screen showing text + translation

### LLM Prompt Strategy

```
System: You are Babel, a friendly bilingual buddy.
The user just spoke in {detected_language}.
Reply in {detected_language} naturally.
After your reply, provide a translation in {other_language}
in the format: [Translation: ...]
```

## System Architecture

### Module Structure

```
BabelBuddy/
├── src/
│   ├── core/                    # Core engine
│   │   ├── engine.py            # BabelEngine - main orchestrator
│   │   ├── conversation.py      # Conversation management (context, history)
│   │   └── language.py          # Language detection result wrapper
│   │
│   ├── speech/                  # Speech processing
│   │   ├── asr.py               # Whisper ASR + language detection
│   │   ├── tts.py               # CosyVoice TTS
│   │   ├── vad.py               # Silero VAD voice activity detection
│   │   └── wake_word.py         # Porcupine wake word
│   │
│   ├── llm/                     # LLM interaction
│   │   ├── ollama_client.py     # Ollama API client
│   │   └── prompt.py            # Prompt template management
│   │
│   ├── data/                    # Data storage
│   │   ├── session_store.py     # SQLite conversation history
│   │   └── models.py            # Data model definitions
│   │
│   ├── api/                     # Web service
│   │   ├── main.py              # FastAPI entry point
│   │   ├── routes.py            # REST + WebSocket routes
│   │   └── schemas.py           # Request/response models
│   │
│   └── terminal/                # CLI terminal
│       └── voice_terminal.py    # CLI voice interaction entry
│
├── web/                         # Web frontend (React SPA)
│
├── config/
│   └── settings.yaml            # Model paths, audio params, etc.
│
├── data/                        # Runtime data
│   └── sessions.db
│
└── models/                      # Local model files
```

### Module Responsibilities

| Module | Responsibility |
|---|---|
| **BabelEngine** | Main orchestrator, chains wake_word → VAD → ASR → LLM → TTS pipeline |
| **ASR** | Calls Whisper, returns `{text, language, confidence}` |
| **TTS** | Calls CosyVoice, selects voice based on language |
| **Prompt Manager** | Dynamically assembles system/user prompt based on detected language |
| **Conversation Manager** | Maintains conversation context window (last 20 messages), manages session lifecycle |
| **Session Store** | SQLite storage for conversation history, supports time/language queries |

### Client Architecture

Both clients share the same BabelEngine via an `AudioSource` abstraction:

```python
class AudioSource(Protocol):
    async def read_audio(self) -> bytes:
        """Read audio chunk from source"""
        ...
    async def play_audio(self, audio: bytes) -> None:
        """Play audio to output device"""
        ...
    async def display(self, text: str, translation: str) -> None:
        """Display text and translation to user"""
        ...
```

- **CLI Terminal**: Implements `AudioSource` with local microphone (PyAudio) and terminal text output
- **Web Page**: Implements `AudioSource` over WebSocket, browser captures audio via Web Audio API

## Error Handling and Resilience

| Stage | Failure Scenario | Fallback Strategy |
|---|---|---|
| **VAD** | Silero fails to load | Bypass VAD, use fixed-duration recording |
| **ASR** | Whisper returns low confidence (< 0.3) | Ask user to repeat: "Sorry, I didn't catch that. Could you say it again?" |
| **ASR** | Whisper language detection uncertain | Default to the language used in the previous turn |
| **LLM** | Ollama timeout (> 10s) | Return "I'm thinking... give me a moment" + retry once |
| **LLM** | Ollama service unavailable | Display error: "Ollama is not running. Please start it with `ollama serve`" |
| **TTS** | CosyVoice synthesis fails | Fall back to text-only output (skip voice) |
| **TTS** | CosyVoice service unavailable | Display error + text-only mode until TTS recovers |
| **Wake Word** | Porcupine init fails | Fall back to keyboard activation (press Enter to start) |

General principles:
- Never crash silently — always inform the user what went wrong
- Degrade gracefully: voice → text-only → error message
- Log all errors with timestamps for debugging

## WebSocket Protocol

### Audio Format

| Parameter | Value |
|---|---|
| Format | PCM 16-bit signed, little-endian |
| Sample Rate | 16000 Hz |
| Channels | 1 (mono) |
| Chunk Size | 4096 bytes (~128ms per chunk) |

### Message Framing

Client → Server (upstream):
```json
{"type": "audio", "data": "<base64-encoded PCM chunk>"}
{"type": "control", "action": "start_session"}
{"type": "control", "action": "end_session"}
```

Server → Client (downstream):
```json
{"type": "transcript", "text": "你好", "language": "zh", "confidence": 0.95}
{"type": "reply", "text": "你好！我是Babel", "translation": "Hi! I'm Babel", "language": "zh"}
{"type": "audio", "data": "<base64-encoded PCM chunk>"}
{"type": "state", "state": "listening|processing|speaking"}
{"type": "error", "message": "ASR failed, please repeat"}
```

## Extensible Architecture (Future Upgrade Paths)

Each AI module is isolated behind an abstract interface, independently replaceable.

```
┌────────────────────────────────────────────────────────────────┐
│                        BabelEngine                              │
│                       (Orchestrator)                            │
│                                                                 │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌─────┐ ┌─────┐ │
│  │  ASR   │ │LangDet │ │  LLM   │ │  TTS   │ │ VAD │ │Wake │ │
│  │Protocol│ │Protocol│ │Protocol│ │Protocol│ │Proto│ │Proto│ │
│  └───┬────┘ └───┬────┘ └───┬────┘ └───┬────┘ └──┬──┘ └──┬──┘ │
└──────┼──────────┼──────────┼──────────┼─────────┼───────┼─────┘
       │          │          │          │         │       │
  ┌────▼───┐ ┌───▼────┐ ┌───▼────┐ ┌───▼─────┐ ┌▼────┐ ┌▼────────┐
  │Whisper │ │Whisper │ │Ollama/ │ │CosyVoice│ │Sile-│ │Porcupine│
  │LargeV3 │ │Built-in│ │Qwen2.5 │ │         │ │ro   │ │         │
  └────────┘ └────────┘ └────────┘ └─────────┘ └─────┘ └─────────┘
```

### Extension Points

| Dimension | Phase 1 | Future Upgrade Path |
|---|---|---|
| **Language Detection** | Whisper built-in | Pluggable LangDetector (langid/fastText) |
| **ASR Accuracy** | Whisper Large V3 | Replaceable with FunASR / SenseVoice |
| **LLM Capability** | Qwen2.5-32B | Larger models or cloud API integration |
| **TTS Naturalness** | CosyVoice | Replaceable with ChatTTS / Fish Speech |
| **VAD** | Silero VAD | Replaceable with WebRTC VAD |
| **Wake Word** | Porcupine ("Hello Babel") | Replaceable with openWakeWord / custom-trained |
| **Language Count** | Chinese + English | Interface is language-agnostic; add ES/JA/PT by extending prompts and TTS voices |
| **Conversation Memory** | SQLite history | Add ChromaDB vector search |

### Abstract Interface Design

```python
class ASRProvider(Protocol):
    async def transcribe(self, audio: bytes) -> ASRResult:
        """Returns {text, language, confidence}"""
        ...

class LLMProvider(Protocol):
    async def chat(self, messages: list[Message]) -> LLMResponse:
        """Returns {reply, translation}"""
        ...

    async def chat_stream(self, messages: list[Message]) -> AsyncIterator[str]:
        """Streams reply tokens for lower perceived latency"""
        ...

class TTSProvider(Protocol):
    async def synthesize(self, text: str, language: str) -> bytes:
        """Returns audio data"""
        ...

    async def synthesize_stream(self, text_stream: AsyncIterator[str], language: str) -> AsyncIterator[bytes]:
        """Streams audio chunks from streaming text input"""
        ...

class VADProvider(Protocol):
    def is_speech(self, audio_chunk: bytes) -> bool:
        """Returns True if audio chunk contains speech"""
        ...

class WakeWordProvider(Protocol):
    def detect(self, audio_chunk: bytes) -> bool:
        """Returns True if wake word detected in audio chunk"""
        ...

class LangDetector(Protocol):
    def detect(self, text: str) -> LangResult:
        """Returns {language, confidence}"""
        ...

class AudioSource(Protocol):
    async def read_audio(self) -> bytes:
        """Read audio chunk from source"""
        ...
    async def play_audio(self, audio: bytes) -> None:
        """Play audio to output device"""
        ...
    async def display(self, text: str, translation: str) -> None:
        """Display text and translation to user"""
        ...
```

### Note on LangDetector

In Phase 1, language detection comes from Whisper's audio-based detection (returned as part of `ASRResult.language`). The `LangDetector` protocol is defined for future use as a post-ASR verification or fallback layer (e.g., using langid/fastText on the transcribed text when Whisper's confidence is low).

## CosyVoice Deployment

CosyVoice runs as a **separate FastAPI sidecar service**:

```bash
# CosyVoice runs on its own port
python -m cosyvoice.server --port 9880
```

The `TTSProvider` implementation communicates with CosyVoice via HTTP API. This keeps the main BabelBuddy process lightweight and allows CosyVoice to manage its own GPU/model resources independently.

Deployment options for Phase 1:
1. **Local subprocess** (recommended): BabelBuddy starts CosyVoice as a managed subprocess
2. **Manual start**: User starts CosyVoice server separately before running BabelBuddy

## Porcupine Wake Word: Licensing Note

Porcupine from Picovoice requires an API key. The free tier supports built-in keywords only; custom wake words ("Hello Babel") require the Porcupine Console and may have licensing restrictions.

**Phase 1 mitigation**: Use a built-in keyword close to "Hello Babel" (e.g., "hey google" placeholder during development), or use openWakeWord (fully offline, Apache 2.0 licensed) as an alternative if custom Porcupine licensing is not feasible.

## API Design

| Endpoint | Method | Description |
|---|---|---|
| `/api/chat` | POST | Text message input, returns reply + translation |
| `/api/ws/chat` | WebSocket | Real-time voice stream (see WebSocket Protocol above) |
| `/api/sessions` | GET | List conversation history |
| `/api/sessions/{id}` | GET | Get session details |
| `/api/health` | GET | Service health check (includes status of Ollama, CosyVoice) |

## Data Model

ID generation: UUID4 for all `id` fields.

```sql
-- Sessions table
CREATE TABLE sessions (
    id TEXT PRIMARY KEY,       -- UUID4
    started_at TIMESTAMP NOT NULL,
    ended_at TIMESTAMP
);

-- Messages table
CREATE TABLE messages (
    id TEXT PRIMARY KEY,       -- UUID4
    session_id TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    role TEXT NOT NULL,        -- 'user' | 'assistant'
    content TEXT NOT NULL,     -- original text
    translation TEXT,          -- translation
    language TEXT NOT NULL,    -- 'zh' | 'en'
    confidence REAL,           -- ASR confidence score (user messages only)
    audio_path TEXT,           -- audio file path, stored for user messages only
    created_at TIMESTAMP NOT NULL
);

-- Indexes
CREATE INDEX idx_messages_session_id ON messages(session_id);
CREATE INDEX idx_messages_language ON messages(language);
CREATE INDEX idx_messages_created_at ON messages(created_at);

-- Schema version tracking
CREATE TABLE schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TIMESTAMP NOT NULL
);
INSERT INTO schema_version (version, applied_at) VALUES (1, CURRENT_TIMESTAMP);
```

### Audio Storage Policy

- **User messages**: Audio is stored only when ASR confidence < 0.7, for debugging and quality review
- **Assistant messages**: Audio is not stored (can be re-synthesized on demand)
- **Retention**: Audio files older than 30 days are automatically cleaned up

## Configuration (settings.yaml)

```yaml
# Model configuration
models:
  llm:
    name: "qwen2.5:32b"
    ollama_host: "http://localhost:11434"
    context_window: 20  # max conversation turns to keep
  asr:
    model: "large-v3"
    device: "cpu"  # or "mps" for Apple Silicon GPU
  tts:
    host: "http://localhost:9880"
    voice_zh: "default_zh"
    voice_en: "default_en"

# Audio configuration
audio:
  sample_rate: 16000
  channels: 1
  chunk_size: 4096
  silence_timeout: 30  # seconds

# Wake word
wake_word:
  engine: "porcupine"  # or "openwakeword"
  keyword: "hello_babel"

# Server
server:
  host: "0.0.0.0"
  port: 8000

# Storage
storage:
  database: "data/sessions.db"
  audio_dir: "data/audio"
  audio_retention_days: 30
```

## Tech Stack Summary

| Component | Technology | Purpose |
|---|---|---|
| ASR | Whisper Large V3 | Speech-to-text + language detection |
| LLM | Ollama + Qwen2.5-32B | Conversation generation |
| TTS | CosyVoice (sidecar service) | Text-to-speech (Chinese + English) |
| Wake Word | Porcupine / openWakeWord | "Hello Babel" detection |
| VAD | Silero VAD | Voice activity detection |
| Backend | FastAPI + WebSocket | API server |
| Frontend | React | Web UI |
| Database | SQLite | Conversation history |
| Config | YAML | Application configuration |
