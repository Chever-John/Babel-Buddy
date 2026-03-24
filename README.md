# BabelBuddy 🗣️🌍

*BabelBuddy - Breaking language barriers, building friendships around the world*

**[中文文档 (Chinese)](README-ZH.md)**

[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-macOS%20(Apple%20Silicon)-purple.svg)]()
[![Architecture](https://img.shields.io/badge/Architecture-4--Layer%20Design-blue.svg)]()

## 📖 Project Introduction

BabelBuddy is a **personal foreign language AI assistant** designed for learners who want to practice speaking multiple languages (English, Spanish, Japanese, etc.) through interactive voice conversations.

The name "BabelBuddy" is inspired by the Tower of Babel - a project where humanity once sought to reach the heavens, but was scattered across the world with different languages. BabelBuddy aims to reverse this: using AI technology to **break down language barriers** and help people connect across linguistic divides.

### 🌟 Core Vision

- **Personal AI Language Coach**: Always available, patient, never judges
- **Privacy-First**: All processing done locally, no cloud API calls
- **Voice-First Interaction**: Natural spoken dialogue, hands-free practice
- **Multi-Language Support**: Designed for multi-language support (Phase 1: Chinese + English)

---

## 🚀 Phase 1: Chinese-English Seamless Conversation

Phase 1 focuses on delivering the core experience: **a bilingual AI buddy that you can talk to naturally in Chinese or English, just like chatting with a real bilingual friend**.

### Core Experience

1. Say **"Hello Babel"** to wake it up
2. Speak in any language — Babel **auto-detects** whether you're speaking Chinese or English
3. Babel **responds in the same language** you used, naturally
4. **Switch languages anytime** mid-conversation, no manual toggle needed
5. Every response includes: **voice playback + original text + translation**

### Example Conversation

```
You:    "Hello Babel"
Babel:  🔔 "I'm listening..."

You:    "你好，请问你是谁"
Babel:  🗣️ "你好！我是 Babel，你的双语伙伴。有什么想聊的吗？"
        📝 [Translation: Hi! I'm Babel, your bilingual buddy. What would you like to chat about?]

You:    "OK, who r u"
Babel:  🗣️ "Hey! I'm Babel, your bilingual buddy. What's on your mind?"
        📝 [Translation: 嘿！我是 Babel，你的双语伙伴。你在想什么？]

You:    "Bye Babel"
Babel:  🔔 "See you next time!"
```

### Phase 1 Scope

| Item | Decision |
|---|---|
| **Wake Word** | "Hello Babel" |
| **Languages** | Chinese + English |
| **Language Switching** | Auto-detect, respond in the same language |
| **Persona** | Friendly, casual bilingual buddy |
| **Output** | Voice + original text + translation |
| **Clients** | CLI terminal + Web page |
| **Hardware** | Apple Silicon Mac |
| **History** | Save and browse past conversations |

---

## 🖥️ System Architecture

BabelBuddy adopts a **4-Layer Architecture** designed for high-performance local deployment:

```
┌─────────────────────────────────────────────────────────────────┐
│                      CLIENT LAYER                                │
│  ┌─────────────────────┐  ┌─────────────────────────────────┐   │
│  │ Web UI (React)      │  │ Voice Terminal (CLI)            │   │
│  │ Browser audio I/O   │  │ Local microphone + speakers     │   │
│  └─────────────────────┘  └─────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   ORCHESTRATION LAYER                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │ FastAPI     │  │ WebSocket   │  │ Conversation Manager    │ │
│  │ Gateway     │  │ Server      │  │ (State Machine)         │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     AI CORE LAYER                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │ Ollama      │  │ Whisper     │  │ CosyVoice               │ │
│  │ (LLM)       │  │ (ASR)       │  │ (TTS)                   │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
│  ┌─────────────┐  ┌─────────────┐                               │
│  │ Porcupine   │  │ Silero VAD  │                               │
│  │ (Wake Word) │  │ (Voice Act.)│                               │
│  └─────────────┘  └─────────────┘                               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DATA LAYER                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │ SQLite      │  │ Local File  │  │ ChromaDB (Future)       │ │
│  │ (Sessions)  │  │ Storage     │  │ (Vector Search)         │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow

```
User speaks → [Silero VAD: detect voice] → [Whisper ASR: transcribe + detect language]
    → [Conversation Manager: assemble prompt with language instruction]
    → [Ollama/Qwen2.5: stream reply + translation]
    → [CosyVoice TTS: stream text to speech in chunks]
    → Output: voice playback + screen display (original text + translation)
```

> **Streaming optimization**: LLM output is streamed to TTS in sentence-level chunks — Babel starts speaking the first sentence while the LLM is still generating the rest, reducing perceived latency to ~3 seconds.

---

## 🔌 Extensible Architecture

Every AI module is isolated behind an abstract interface, making each component **independently replaceable and upgradeable**.

```
┌──────────────────────────────────────────────────────────┐
│                     BabelEngine                           │
│                    (Orchestrator)                          │
│                                                           │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐ │
│   │ASRProvider│ │LangDetect│  │LLMProvider│ │TTSProvider│ │
│   │ Protocol │  │ Protocol │  │ Protocol  │  │ Protocol │ │
│   └─────┬────┘  └─────┬────┘  └─────┬────┘  └────┬─────┘ │
└─────────┼──────────────┼─────────────┼────────────┼───────┘
          │              │             │            │
     ┌────▼────┐   ┌─────▼────┐  ┌────▼────┐  ┌───▼──────┐
     │Whisper  │   │Whisper   │  │Ollama/  │  │CosyVoice │
     │LargeV3  │   │Built-in  │  │Qwen2.5  │  │          │
     └─────────┘   └──────────┘  └─────────┘  └──────────┘
```

### Abstract Interfaces

All AI modules implement Protocol-based interfaces for easy replacement:

```python
class ASRProvider(Protocol):
    async def transcribe(self, audio: bytes) -> ASRResult:
        """Returns {text, language, confidence}"""

class LLMProvider(Protocol):
    async def chat(self, messages: list[Message]) -> LLMResponse:
        """Returns {reply, translation}"""
    async def chat_stream(self, messages: list[Message]) -> AsyncIterator[str]:
        """Streams reply tokens for lower perceived latency"""

class TTSProvider(Protocol):
    async def synthesize(self, text: str, language: str) -> bytes:
        """Returns audio data"""
    async def synthesize_stream(self, text_stream: AsyncIterator[str], language: str) -> AsyncIterator[bytes]:
        """Streams audio chunks from streaming text input"""

class VADProvider(Protocol):
    def is_speech(self, audio_chunk: bytes) -> bool:
        """Returns True if audio chunk contains speech"""

class WakeWordProvider(Protocol):
    def detect(self, audio_chunk: bytes) -> bool:
        """Returns True if wake word detected"""

class LangDetector(Protocol):
    def detect(self, text: str) -> LangResult:
        """Returns {language, confidence} — future post-ASR verification layer"""

class AudioSource(Protocol):
    async def read_audio(self) -> bytes:
        """Read audio chunk from source (mic or WebSocket)"""
    async def play_audio(self, audio: bytes) -> None:
        """Play audio to output"""
    async def display(self, text: str, translation: str) -> None:
        """Display text and translation"""
```

### Upgrade Roadmap

| Dimension | Phase 1 | Future Upgrade Path |
|---|---|---|
| **Language Detection** | Whisper built-in | Pluggable LangDetector (langid / fastText) |
| **ASR Accuracy** | Whisper Large V3 | FunASR / SenseVoice |
| **LLM Capability** | Qwen2.5-32B | Larger models or cloud API |
| **TTS Naturalness** | CosyVoice | ChatTTS / Fish Speech |
| **VAD** | Silero VAD | WebRTC VAD |
| **Wake Word** | Porcupine / openWakeWord | Custom-trained models |
| **Language Count** | Chinese + English | ES / JA / PT (extend prompts + TTS voices) |
| **Conversation Memory** | SQLite history | ChromaDB vector search |

---

## ⚙️ Hardware Requirements

### Recommended Configuration

| Component | Specification | Notes |
|-----------|---------------|-------|
| **CPU** | Apple M3 Ultra (32-core) | Or M2 Ultra equivalent |
| **Memory** | 512GB RAM | Essential for large LLM models |
| **Storage** | 1.8TB SSD | Model weights + audio storage |
| **Audio** | External Microphone + Speakers | Low-latency recommended |

### Memory Allocation Strategy (with Qwen2.5-32B)

| Component | Memory Allocation |
|-----------|------------------|
| Ollama (LLM) | ~64GB (Qwen2.5-32B) |
| Whisper Large V3 | ~4GB |
| CosyVoice | ~4GB |
| System + Others | ~20GB |
| **Total Required** | **~92GB** |

> For Llama-3-70B, allocate ~140GB for Ollama. Full 512GB RAM is only needed when running 70B+ models.

---

## 🤖 Model Selection

### Recommended LLM Models

| Model | Parameters | Context | Memory | Notes |
|-------|------------|---------|--------|-------|
| **Qwen2.5-32B-Instruct** | 32B | 128K | ~64GB | Best cost-performance |
| **Llama-3-70B-Instruct** | 70B | 8K | ~140GB | Higher quality |
| **Qwen2.5-14B-Instruct** | 14B | 128K | ~28GB | Minimal config |

### Speech Processing Models

| Function | Model | Notes |
|----------|-------|-------|
| **ASR (Speech→Text)** | Whisper Large V3 | Multilingual support |
| **TTS (Text→Speech)** | CosyVoice | Chinese + English natural voice |
| **Wake Word** | Porcupine (picovoice) | "Hello Babel" trigger |
| **VAD** | Silero VAD | Voice activity detection |

---

## ✨ Core Features

### 1. 🎙️ Voice Interaction
- **Wake Word Detection**: "Hello Babel" activates the assistant
- **Real-time ASR**: Speech-to-text with automatic language detection
- **Natural TTS**: AI-generated speech in Chinese or English
- **Seamless Language Switching**: Auto-detects and responds in your language

### 2. 🌐 Bilingual Output
- **Original Text**: See exactly what Babel said on screen
- **Translation**: Every response comes with its translation
- **Voice Playback**: Hear the response spoken naturally

### 3. 🧠 Smart Conversations
- **Context Memory**: Remembers conversation history within a session
- **Friendly Persona**: Like chatting with a bilingual friend
- **Natural Flow**: No rigid Q&A, just free-form conversation

### 4. 📊 Session History
- **Local Storage**: All conversations saved in SQLite
- **Browse History**: Review past sessions and messages
- **Search by Language**: Filter conversations by Chinese or English

---

## 📁 Project Structure

```
BabelBuddy/
├── LICENSE                 # MIT License
├── README.md               # This file
├── docs/                   # Documentation
│   └── superpowers/specs/  # Design specifications
├── src/
│   ├── core/               # Core engine (BabelEngine, conversation manager)
│   ├── speech/             # ASR (Whisper), TTS (CosyVoice), VAD, Wake Word
│   ├── llm/                # Ollama client, prompt templates
│   ├── data/               # SQLite session storage, data models
│   ├── api/                # FastAPI gateway, WebSocket, REST routes
│   └── terminal/           # CLI voice terminal
├── web/                    # React Web UI
├── config/                 # Application configuration (settings.yaml)
├── models/                 # Local model storage
└── data/                   # Runtime data (sessions.db, audio files)
```

---

## 🔧 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/chat` | POST | Text message input, returns reply + translation |
| `/api/ws/chat` | WebSocket | Real-time voice stream (audio + text + translation) |
| `/api/sessions` | GET | List conversation history |
| `/api/sessions/{id}` | GET | Get session details |
| `/api/health` | GET | Service health check |

---

## 🛠️ Installation Guide

### Prerequisites

```bash
# 1. Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 2. Pull recommended LLM model
ollama pull qwen2.5:32b

# 3. Install Python dependencies
pip install -r requirements.txt
```

### Model Download (Alternative)

For faster downloads in China, use ModelScope:

```bash
pip install modelscope
modelscope download --model Qwen/Qwen2.5-32B-Instruct --local_dir ./models/Qwen2.5-32B-Instruct
```

### Running the Service

```bash
# Start the API server
python -m src.api.main

# Start the voice terminal (requires audio hardware)
python -m src.terminal.voice_terminal
```

---

## 📜 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- [Ollama](https://ollama.ai/) - Local LLM inference
- [Whisper](https://github.com/openai/whisper) - Speech recognition
- [CosyVoice](https://github.com/FunAudioLLM/CosyVoice) - Text-to-speech
- [Porcupine](https://picovoice.ai/porcupine/) - Wake word detection
- [Silero VAD](https://github.com/snakers4/silero-vad) - Voice activity detection

---

*BabelBuddy - Your personal language learning companion 🗣️🌍*
