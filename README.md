# BabelBuddy 🗣️🌍

*BabelBuddy - Breaking language barriers, building friendships around the world*

[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-macOS%20%7C%20Linux-purple.svg)]()
[![Architecture](https://img.shields.io/badge/Architecture-4--Layer%20Design-blue.svg)]()

## 📖 Project Introduction

BabelBuddy is a **personal foreign language AI assistant** designed for learners who want to practice speaking multiple languages (English, Spanish, Japanese, etc.) through interactive voice conversations.

The name "BabelBuddy" is inspired by the Tower of Babel - a project where humanity once sought to reach the heavens, but was scattered across the world with different languages. BabelBuddy aims to reverse this: using AI technology to **break down language barriers** and help people connect across linguistic divides.

### 🌟 Core Vision

- **Personal AI Language Coach**: Always available, patient, neverjudges
- **Privacy-First**: All processing done locally, no cloud API calls
- **Voice-First Interaction**: Natural spoken dialogue, hands-free practice
- **Multi-Language Support**: English, Spanish, Japanese, and more

---

## 🖥️ System Architecture

BabelBuddy adopts a **4-Layer Architecture** designed for high-performance local deployment:

```
┌─────────────────────────────────────────────────────────────────┐
│                      CLIENT LAYER                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │ Web UI      │  │ Mobile App  │  │ Voice Terminal          │ │
│  │ (React)     │  │ (Flutter)   │  │ (Raspberry Pi + Speaker)│ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   ORCHESTRATION LAYER                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │ FastAPI     │  │ WebSocket   │  │ Conversation Manager   │ │
│  │ Gateway     │  │ Server      │  │ (State Machine)        │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     AI CORE LAYER                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │ Ollama      │  │ Whisper     │  │ XTTS / CosyVoice        │ │
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
│  │ ChromaDB    │  │ SQLite      │  │ Local File Storage      │ │
│  │ (Vectors)   │  │ (Sessions)  │  │ (Audio, Models)         │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

##⚙️ Hardware Requirements

### Recommended Configuration

| Component | Specification | Notes |
|-----------|---------------|-------|
| **CPU** | Apple M3 Ultra (32-core) | Or M2 Ultra equivalent |
| **Memory** | 512GB RAM | Essential for large LLM models |
| **Storage** | 1.8TB SSD | Model weights + audio storage |
| **Audio** | External Microphone + Speakers | Low-latency recommended |

### Memory Allocation Strategy

| Component | Memory Allocation |
|-----------|------------------|
| Ollama (LLM) | 384GB (Qwen2.5-32B or Llama3-70B) |
| Whisper | 4GB |
| System + Others | ~60GB |
| **Reserved** | ~50GB |

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
| **TTS (Text→Speech)** | XTTS v2 / CosyVoice | Natural voice output |
| **Wake Word** | Porcupine (picovoice) | "Hey Babel" trigger |
| **VAD** | Silero VAD | Voice activity detection |

---

## ✨ Core Features

### 1. 🎙️ Voice Interaction
- **Wake Word Detection**: "Hey Babel" activates the assistant
- **Real-time ASR**: Speech-to-text with Whisper
- **Natural TTS**: AI-generated speech response
- **Full Duplex**: Simultaneous listening and speaking

### 2. 📚 Language Practice
- **Grammar Correction**: Instant feedback on mistakes
- **Scenario Simulation**: Travel, business, daily conversations
- **Vocabulary Building**: New words with examples
- **Pronunciation Tips**: Phonetic guidance

### 3. 🧠 Smart Conversations
- **Context Memory**: Remembers conversation history
- **Topic Suggestions**: Suggests practice topics
- **Difficulty Levels**: Beginner to advanced
- **Multiple Languages**: Switch between EN/ES/JA

### 4. 📊 Progress Tracking
- **Session History**: All conversations stored locally
- **Statistics Dashboard**: Practice time, common mistakes
- **Vector Search**: Find similar past conversations

---

## 🛠️ Installation Guide

### Prerequisites

```bash
# 1. Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 2. Pull recommended LLM model
ollama pull qwen2.5:32b
# or
ollama pull llama3:70b

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

## 📁 Project Structure

```
BabelBuddy/
├── LICENSE                 # MIT License
├── README.md               # This file
├── docs/                   # Documentation
│   ├── SYSTEM_ARCHITECTURE.md
│   └── MODEL_DOWNLOAD_GUIDE.md
├── src/
│   ├── api/                # FastAPI gateway
│   ├── core/               # AI model wrappers
│   ├── speech/             # ASR/TTS/Wake Word
│   ├── data/               # ChromaDB/SQLite
│   └── terminal/           # Voice terminal
├── models/                 # Local model storage
└── data/                   # Conversation data
```

---

## 🔧 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/chat` | POST | Send message, get AI response |
| `/ws/chat` | WebSocket | Real-time voice streaming |
| `/session` | GET/POST | Conversation history |
| `/stats` | GET | Practice statistics |

---

## 📜 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- [Ollama](https://ollama.ai/) - Local LLM inference
- [Whisper](https://github.com/openai/whisper) - Speech recognition
- [XTTS](https://coqui.ai/) - Text-to-speech
- [Porcupine](https://picovoice.ai/porcupine/) - Wake word detection

---

* BabelBuddy - Your personal language learning companion 🗣️🌍
