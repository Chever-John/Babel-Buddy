# BabelBuddy 🗣️🌍

*BabelBuddy - 打破语言壁垒，结交世界朋友*

**[English Documentation](README.md)**

[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-macOS%20(Apple%20Silicon)-purple.svg)]()
[![Architecture](https://img.shields.io/badge/Architecture-4--Layer%20Design-blue.svg)]()

## 📖 项目简介

BabelBuddy 是一款**个人外语 AI 助手**，专为希望通过语音对话练习多种语言（英语、西班牙语、日语等）的学习者设计。

"BabelBuddy" 的名字灵感源自巴别塔——人类曾试图建造通天高塔，却因语言不通而散落世界各地。BabelBuddy 旨在逆转这一局面：利用 AI 技术**打破语言壁垒**，帮助人们跨越语言鸿沟。

### 🌟 核心愿景

- **私人 AI 语言教练**：随时可用、耐心陪伴、从不评判
- **隐私优先**：所有处理在本地完成，无需云端 API 调用
- **语音优先交互**：自然的语音对话，解放双手
- **多语言支持**：面向多语言设计（第一期：中文 + 英文）

---

## 🚀 第一期：中英文无缝对话

第一期聚焦核心体验：**一个双语 AI 伙伴，你可以用中文或英文自然地和它聊天，就像和一个真正的双语朋友对话一样**。

### 核心体验

1. 说 **"Hello Babel"** 唤醒它
2. 随意说话 —— Babel **自动检测**你说的是中文还是英文
3. Babel 用**你说的同一种语言**自然回复
4. 对话中**随时切换语言**，无需手动操作
5. 每条回复都包含：**语音播放 + 原文文字 + 翻译**

### 对话示例

```
你:     "Hello Babel"
Babel:  🔔 "我在听..."

你:     "你好，请问你是谁"
Babel:  🗣️ "你好！我是 Babel，你的双语伙伴。有什么想聊的吗？"
        📝 [翻译: Hi! I'm Babel, your bilingual buddy. What would you like to chat about?]

你:     "OK, who r u"
Babel:  🗣️ "Hey! I'm Babel, your bilingual buddy. What's on your mind?"
        📝 [翻译: 嘿！我是 Babel，你的双语伙伴。你在想什么？]

你:     "Bye Babel"
Babel:  🔔 "下次见！"
```

### 第一期范围

| 项目 | 决定 |
|---|---|
| **唤醒词** | "Hello Babel" |
| **语言** | 中文 + 英文 |
| **语言切换** | 自动检测，用相同语言回复 |
| **人设** | 友好随和的双语伙伴 |
| **输出** | 语音 + 原文 + 翻译 |
| **客户端** | 命令行终端 + Web 页面 |
| **硬件** | Apple Silicon Mac |
| **历史记录** | 保存并浏览历史对话 |

---

## 🖥️ 系统架构

BabelBuddy 采用**四层架构**，面向高性能本地部署设计：

```
┌─────────────────────────────────────────────────────────────────┐
│                        客户端层                                   │
│  ┌─────────────────────┐  ┌─────────────────────────────────┐   │
│  │ Web UI (React)      │  │ 语音终端 (CLI)                   │   │
│  │ 浏览器音频 I/O       │  │ 本地麦克风 + 扬声器              │   │
│  └─────────────────────┘  └─────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        编排层                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │ FastAPI     │  │ WebSocket   │  │ 对话管理器               │ │
│  │ 网关        │  │ 服务器      │  │ (状态机)                 │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       AI 核心层                                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │ Ollama      │  │ Whisper     │  │ CosyVoice               │ │
│  │ (大语言模型) │  │ (语音识别)  │  │ (语音合成)               │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
│  ┌─────────────┐  ┌─────────────┐                               │
│  │ Porcupine   │  │ Silero VAD  │                               │
│  │ (唤醒词)    │  │ (语音活动)  │                               │
│  └─────────────┘  └─────────────┘                               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        数据层                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │ SQLite      │  │ 本地文件    │  │ ChromaDB (未来)          │ │
│  │ (会话存储)  │  │ 存储        │  │ (向量搜索)               │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### 数据流

```
用户说话 → [Silero VAD: 检测人声] → [Whisper ASR: 转文字 + 识别语种]
    → [对话管理器: 组装含语种指令的 prompt]
    → [Ollama/Qwen2.5: 流式生成回复 + 翻译]
    → [CosyVoice TTS: 流式文字转语音]
    → 输出: 语音播放 + 屏幕显示 (原文 + 翻译)
```

> **流式优化**：LLM 输出按句级分块流式传给 TTS —— Babel 在说第一句话时，LLM 还在生成后续内容，感知延迟降低至约 3 秒。

---

## 🔌 可扩展架构

每个 AI 模块都通过抽象接口隔离，各组件可**独立替换和升级**。

```
┌──────────────────────────────────────────────────────────┐
│                     BabelEngine                           │
│                    (编排器)                                │
│                                                           │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐ │
│   │ASR 接口  │  │语种检测   │  │LLM 接口  │  │TTS 接口 │ │
│   │ Protocol │  │ Protocol │  │ Protocol  │  │ Protocol │ │
│   └─────┬────┘  └─────┬────┘  └─────┬────┘  └────┬─────┘ │
└─────────┼──────────────┼─────────────┼────────────┼───────┘
          │              │             │            │
     ┌────▼────┐   ┌─────▼────┐  ┌────▼────┐  ┌───▼──────┐
     │Whisper  │   │Whisper   │  │Ollama/  │  │CosyVoice │
     │LargeV3  │   │内置检测   │  │Qwen2.5  │  │          │
     └─────────┘   └──────────┘  └─────────┘  └──────────┘
```

### 抽象接口

所有 AI 模块实现基于 Protocol 的接口，方便替换：

```python
class ASRProvider(Protocol):
    async def transcribe(self, audio: bytes) -> ASRResult:
        """返回 {text, language, confidence}"""

class LLMProvider(Protocol):
    async def chat(self, messages: list[Message]) -> LLMResponse:
        """返回 {reply, translation}"""
    async def chat_stream(self, messages: list[Message]) -> AsyncIterator[str]:
        """流式输出回复 token，降低感知延迟"""

class TTSProvider(Protocol):
    async def synthesize(self, text: str, language: str) -> bytes:
        """返回音频数据"""
    async def synthesize_stream(self, text_stream: AsyncIterator[str], language: str) -> AsyncIterator[bytes]:
        """从流式文本输入生成流式音频块"""

class VADProvider(Protocol):
    def is_speech(self, audio_chunk: bytes) -> bool:
        """音频块中是否包含人声"""

class WakeWordProvider(Protocol):
    def detect(self, audio_chunk: bytes) -> bool:
        """是否检测到唤醒词"""

class LangDetector(Protocol):
    def detect(self, text: str) -> LangResult:
        """返回 {language, confidence} —— 未来用于 ASR 后置验证"""

class AudioSource(Protocol):
    async def read_audio(self) -> bytes:
        """从音频源读取数据（麦克风或 WebSocket）"""
    async def play_audio(self, audio: bytes) -> None:
        """播放音频"""
    async def display(self, text: str, translation: str) -> None:
        """显示文字和翻译"""
```

### 升级路线

| 维度 | 第一期 | 未来升级路径 |
|---|---|---|
| **语种检测** | Whisper 内置 | 可插拔 LangDetector (langid / fastText) |
| **语音识别精度** | Whisper Large V3 | FunASR / SenseVoice |
| **LLM 能力** | Qwen2.5-32B | 更大模型或云端 API |
| **语音合成自然度** | CosyVoice | ChatTTS / Fish Speech |
| **VAD** | Silero VAD | WebRTC VAD |
| **唤醒词** | Porcupine / openWakeWord | 自训练模型 |
| **语言数量** | 中文 + 英文 | ES / JA / PT（扩展 prompt 和 TTS 声音）|
| **对话记忆** | SQLite 历史 | ChromaDB 向量搜索 |

---

## ⚙️ 硬件要求

### 推荐配置

| 组件 | 规格 | 说明 |
|------|------|------|
| **CPU** | Apple M3 Ultra (32核) | 或 M2 Ultra 同等 |
| **内存** | 512GB RAM | 大模型运行必需 |
| **存储** | 1.8TB SSD | 模型权重 + 音频存储 |
| **音频** | 外接麦克风 + 扬声器 | 建议低延迟设备 |

### 内存分配策略（使用 Qwen2.5-32B）

| 组件 | 内存占用 |
|------|----------|
| Ollama (LLM) | ~64GB (Qwen2.5-32B) |
| Whisper Large V3 | ~4GB |
| CosyVoice | ~4GB |
| 系统 + 其他 | ~20GB |
| **总计** | **~92GB** |

> 使用 Llama-3-70B 时 Ollama 需约 140GB。512GB 满配仅在运行 70B+ 模型时需要。

---

## 🤖 模型选型

### 推荐大语言模型

| 模型 | 参数量 | 上下文 | 内存 | 说明 |
|------|--------|--------|------|------|
| **Qwen2.5-32B-Instruct** | 32B | 128K | ~64GB | 性价比最优 |
| **Llama-3-70B-Instruct** | 70B | 8K | ~140GB | 质量更高 |
| **Qwen2.5-14B-Instruct** | 14B | 128K | ~28GB | 最低配置 |

### 语音处理模型

| 功能 | 模型 | 说明 |
|------|------|------|
| **ASR（语音→文字）** | Whisper Large V3 | 多语言支持 |
| **TTS（文字→语音）** | CosyVoice | 中英文自然语音 |
| **唤醒词** | Porcupine (picovoice) | "Hello Babel" 触发 |
| **VAD** | Silero VAD | 语音活动检测 |

---

## ✨ 核心功能

### 1. 🎙️ 语音交互
- **唤醒词检测**："Hello Babel" 激活助手
- **实时语音识别**：Whisper 转文字并自动识别语种
- **自然语音合成**：AI 生成的中文或英文语音
- **无缝语言切换**：自动检测并用你的语言回复

### 2. 🌐 双语输出
- **原文显示**：屏幕上看到 Babel 说的原文
- **翻译对照**：每条回复附带对应翻译
- **语音播放**：自然地听到回复语音

### 3. 🧠 智能对话
- **上下文记忆**：记住会话内的对话历史
- **友好人设**：像和一个双语朋友聊天
- **自由交流**：没有死板的问答，随意自然地对话

### 4. 📊 会话历史
- **本地存储**：所有对话保存在 SQLite 中
- **历史浏览**：回看过去的会话和消息
- **语言筛选**：按中文或英文过滤对话

---

## 📁 项目结构

```
BabelBuddy/
├── LICENSE                 # MIT 许可证
├── README.md               # 英文文档
├── README-ZH.md            # 中文文档（本文件）
├── docs/                   # 文档
│   └── superpowers/specs/  # 设计规格文档
├── src/
│   ├── core/               # 核心引擎（BabelEngine、对话管理器）
│   ├── speech/             # ASR (Whisper)、TTS (CosyVoice)、VAD、唤醒词
│   ├── llm/                # Ollama 客户端、Prompt 模板
│   ├── data/               # SQLite 会话存储、数据模型
│   ├── api/                # FastAPI 网关、WebSocket、REST 路由
│   └── terminal/           # CLI 语音终端
├── web/                    # React Web UI
├── config/                 # 应用配置 (settings.yaml)
├── models/                 # 本地模型存储
└── data/                   # 运行时数据 (sessions.db、音频文件)
```

---

## 🔧 API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/chat` | POST | 文字消息输入，返回回复 + 翻译 |
| `/api/ws/chat` | WebSocket | 实时语音流（音频 + 文字 + 翻译）|
| `/api/sessions` | GET | 获取历史会话列表 |
| `/api/sessions/{id}` | GET | 获取会话详情 |
| `/api/health` | GET | 服务健康检查 |

---

## 🛠️ 安装指南

### 前置条件

```bash
# 1. 安装 Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 2. 拉取推荐的大语言模型
ollama pull qwen2.5:32b

# 3. 安装 Python 依赖
pip install -r requirements.txt
```

### 模型下载（国内加速）

使用 ModelScope 加速下载：

```bash
pip install modelscope
modelscope download --model Qwen/Qwen2.5-32B-Instruct --local_dir ./models/Qwen2.5-32B-Instruct
```

### 启动服务

```bash
# 启动 API 服务器
python -m src.api.main

# 启动语音终端（需要音频硬件）
python -m src.terminal.voice_terminal
```

---

## 📜 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE)。

---

## 🙏 致谢

- [Ollama](https://ollama.ai/) - 本地大语言模型推理
- [Whisper](https://github.com/openai/whisper) - 语音识别
- [CosyVoice](https://github.com/FunAudioLLM/CosyVoice) - 语音合成
- [Porcupine](https://picovoice.ai/porcupine/) - 唤醒词检测
- [Silero VAD](https://github.com/snakers4/silero-vad) - 语音活动检测

---

*BabelBuddy - 你的私人语言学习伙伴 🗣️🌍*
