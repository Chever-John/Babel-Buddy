# BabelBuddy 第一期设计：中英文无缝对话

## 概述

第一期实现核心体验：一个双语 AI 伙伴，自动检测你说的是中文还是英文，用相同语言回复，支持实时语音交互和翻译显示。

## 核心需求

| 项目 | 决定 |
|---|---|
| 唤醒词 | "Hello Babel" |
| 退出指令 | "Bye Babel"（通过 ASR 检测，非唤醒词引擎）|
| 语言 | 第一期：中文 + 英文 |
| 语言切换 | 自动检测，用用户说话的同一种语言回复 |
| 人设 | 友好随和的双语伙伴 |
| 输出 | 语音 + 原文 + 翻译 |
| 客户端 | 命令行终端 + Web 页面 |
| 硬件 | Apple Silicon Mac（第一期）|
| 历史记录 | 保存并浏览历史对话 |
| 静默超时 | 30 秒无人说话退出对话模式 |

## 性能目标

| 阶段 | 延迟预算 | 说明 |
|---|---|---|
| VAD 检测 | < 100ms | 实时流式处理 |
| ASR (Whisper) | < 1.5s | 典型语句（3-10秒音频）|
| LLM 首个 token | < 1s | Ollama 流式模式 |
| LLM 完整回复 | < 5s | Apple Silicon 上约 10-20 tok/s，50-100 个 token |
| TTS 合成 | < 1s | 流式：在完整合成前即开始播放 |
| **端到端** | **< 3s 感知延迟** | 使用 LLM 流式 → TTS 流式管道 |

**关键优化**：LLM 输出按块流式传给 TTS —— 在说第一句话时 LLM 还在生成后续内容。感知延迟从约 8 秒降至约 3 秒。

## 数据流

### 对话流程

```
用户说话 → [Silero VAD: 检测语音活动] → [Whisper ASR: 转文字 + 识别语种]
    → [对话管理器: 组装含语种指令的 prompt]
    → [Ollama/Qwen2.5: 流式生成回复 + 翻译]
    → [CosyVoice TTS: 流式文字转语音]
    → 输出: 语音播放 + 屏幕显示（原文 + 翻译）
```

### 唤醒流程

```
麦克风常驻监听 → [Porcupine: 检测 "Hello Babel"]
    → 播放提示音 + 显示 "我在听..."
    → 进入对话模式（VAD → ASR → LLM → TTS 循环）
    → 退出触发:
        1. 用户说 "Bye Babel"（通过 ASR 转写后检测）
        2. 连续 30 秒静默（无 VAD 活动）
    → 播放告别提示音 + 显示 "下次见！"
    → 返回唤醒词监听模式
```

### 对话状态机

```
    ┌──────────┐  "Hello Babel"   ┌───────────┐
    │   空闲   │ ───────────────→ │   监听中   │ ←──────────┐
    └──────────┘                  └─────┬─────┘             │
         ↑                              │ VAD 检测到        │
         │                              │ 说话结束          │
         │                        ┌─────▼──────┐           │
         │                        │   处理中    │           │
         │                        │ (ASR→LLM)   │           │
         │                        └─────┬──────┘           │
         │                              │                   │
         │                        ┌─────▼──────┐           │
         │                        │   播放中    │ ──────────┘
         │                        │  (TTS 输出) │  TTS 完成
         │                        └─────┬──────┘
         │                              │
         │  "Bye Babel" 或超时          │
         └──────────────────────────────┘
```

状态说明：
- **空闲 (IDLE)**：仅唤醒词引擎活跃，资源消耗最小
- **监听中 (LISTENING)**：VAD 活跃，采集用户音频，等待说话结束
- **处理中 (PROCESSING)**：ASR 转写 → LLM 生成 → 准备回复
- **播放中 (SPEAKING)**：TTS 播放音频输出，屏幕显示文字 + 翻译

### LLM Prompt 策略

```
System: You are Babel, a friendly bilingual buddy.
The user just spoke in {detected_language}.
Reply in {detected_language} naturally.
After your reply, provide a translation in {other_language}
in the format: [Translation: ...]
```

## 系统架构

### 模块结构

```
BabelBuddy/
├── src/
│   ├── core/                    # 核心引擎
│   │   ├── engine.py            # BabelEngine - 主编排器
│   │   ├── conversation.py      # 对话管理（上下文、历史）
│   │   └── language.py          # 语种检测结果封装
│   │
│   ├── speech/                  # 语音处理
│   │   ├── asr.py               # Whisper ASR + 语种检测
│   │   ├── tts.py               # CosyVoice TTS
│   │   ├── vad.py               # Silero VAD 语音活动检测
│   │   └── wake_word.py         # Porcupine 唤醒词
│   │
│   ├── llm/                     # LLM 交互
│   │   ├── ollama_client.py     # Ollama API 客户端
│   │   └── prompt.py            # Prompt 模板管理
│   │
│   ├── data/                    # 数据存储
│   │   ├── session_store.py     # SQLite 对话历史
│   │   └── models.py            # 数据模型定义
│   │
│   ├── api/                     # Web 服务
│   │   ├── main.py              # FastAPI 入口
│   │   ├── routes.py            # REST + WebSocket 路由
│   │   └── schemas.py           # 请求/响应模型
│   │
│   └── terminal/                # 命令行终端
│       └── voice_terminal.py    # CLI 语音交互入口
│
├── web/                         # Web 前端 (React SPA)
│
├── config/
│   └── settings.yaml            # 模型路径、音频参数等配置
│
├── data/                        # 运行时数据
│   └── sessions.db
│
└── models/                      # 本地模型文件
```

### 模块职责

| 模块 | 职责 |
|---|---|
| **BabelEngine** | 主编排器，串联 wake_word → VAD → ASR → LLM → TTS 流程 |
| **ASR** | 调用 Whisper，返回 `{text, language, confidence}` |
| **TTS** | 调用 CosyVoice，根据语种选择对应声音 |
| **Prompt 管理器** | 根据检测到的语种动态组装 system/user prompt |
| **对话管理器** | 维护对话上下文窗口（最近 20 条消息），管理会话生命周期 |
| **会话存储** | SQLite 存储对话历史，支持按时间/语种查询 |

### 客户端架构

两个客户端通过 `AudioSource` 抽象共享同一个 BabelEngine：

```python
class AudioSource(Protocol):
    async def read_audio(self) -> bytes:
        """从音频源读取数据"""
        ...
    async def play_audio(self, audio: bytes) -> None:
        """播放音频到输出设备"""
        ...
    async def display(self, text: str, translation: str) -> None:
        """显示文字和翻译"""
        ...
```

- **命令行终端**：用本地麦克风 (PyAudio) 实现 `AudioSource`，终端文字输出
- **Web 页面**：通过 WebSocket 实现 `AudioSource`，浏览器通过 Web Audio API 采集音频

## 错误处理与容错

| 阶段 | 故障场景 | 降级策略 |
|---|---|---|
| **VAD** | Silero 加载失败 | 跳过 VAD，使用固定时长录音 |
| **ASR** | Whisper 置信度低 (< 0.3) | 请用户重说："抱歉，没听清，能再说一遍吗？" |
| **ASR** | Whisper 语种检测不确定 | 默认使用上一轮的语种 |
| **LLM** | Ollama 超时 (> 10s) | 回复 "让我想想...稍等" + 重试一次 |
| **LLM** | Ollama 服务不可用 | 显示错误："Ollama 未运行，请执行 `ollama serve` 启动" |
| **TTS** | CosyVoice 合成失败 | 降级为纯文字输出（跳过语音）|
| **TTS** | CosyVoice 服务不可用 | 显示错误 + 纯文字模式直到 TTS 恢复 |
| **唤醒词** | Porcupine 初始化失败 | 降级为键盘激活（按回车开始）|

通用原则：
- 永不静默崩溃 —— 始终告知用户发生了什么
- 优雅降级：语音 → 纯文字 → 错误消息
- 所有错误附带时间戳写入日志用于调试

## WebSocket 协议

### 音频格式

| 参数 | 值 |
|---|---|
| 格式 | PCM 16位有符号，小端序 |
| 采样率 | 16000 Hz |
| 声道 | 1（单声道）|
| 块大小 | 4096 字节（约 128ms 每块）|

### 消息帧格式

客户端 → 服务端（上行）：
```json
{"type": "audio", "data": "<base64编码的PCM块>"}
{"type": "control", "action": "start_session"}
{"type": "control", "action": "end_session"}
```

服务端 → 客户端（下行）：
```json
{"type": "transcript", "text": "你好", "language": "zh", "confidence": 0.95}
{"type": "reply", "text": "你好！我是Babel", "translation": "Hi! I'm Babel", "language": "zh"}
{"type": "audio", "data": "<base64编码的PCM块>"}
{"type": "state", "state": "listening|processing|speaking"}
{"type": "error", "message": "语音识别失败，请重试"}
```

## 可扩展架构（未来升级路径）

每个 AI 模块通过抽象接口隔离，可独立替换。

```
┌────────────────────────────────────────────────────────────────┐
│                        BabelEngine                              │
│                        (编排器)                                  │
│                                                                 │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌─────┐ ┌─────┐ │
│  │  ASR   │ │语种检测│ │  LLM   │ │  TTS   │ │ VAD │ │唤醒 │ │
│  │ 接口   │ │ 接口   │ │ 接口   │ │ 接口   │ │接口 │ │接口 │ │
│  └───┬────┘ └───┬────┘ └───┬────┘ └───┬────┘ └──┬──┘ └──┬──┘ │
└──────┼──────────┼──────────┼──────────┼─────────┼───────┼─────┘
       │          │          │          │         │       │
  ┌────▼───┐ ┌───▼────┐ ┌───▼────┐ ┌───▼─────┐ ┌▼────┐ ┌▼────────┐
  │Whisper │ │Whisper │ │Ollama/ │ │CosyVoice│ │Sile-│ │Porcupine│
  │LargeV3 │ │内置检测│ │Qwen2.5 │ │         │ │ro   │ │         │
  └────────┘ └────────┘ └────────┘ └─────────┘ └─────┘ └─────────┘
```

### 扩展点

| 维度 | 第一期 | 未来升级路径 |
|---|---|---|
| **语种检测** | Whisper 内置 | 可插拔 LangDetector (langid/fastText) |
| **语音识别精度** | Whisper Large V3 | 可替换为 FunASR / SenseVoice |
| **LLM 能力** | Qwen2.5-32B | 更大模型或云端 API |
| **语音合成自然度** | CosyVoice | 可替换为 ChatTTS / Fish Speech |
| **VAD** | Silero VAD | 可替换为 WebRTC VAD |
| **唤醒词** | Porcupine ("Hello Babel") | 可替换为 openWakeWord / 自训练模型 |
| **语言数量** | 中文 + 英文 | 接口不限语种，加 ES/JA/PT 只需扩展 prompt 和 TTS 声音 |
| **对话记忆** | SQLite 历史 | 加 ChromaDB 向量搜索 |

### 抽象接口设计

```python
class ASRProvider(Protocol):
    async def transcribe(self, audio: bytes) -> ASRResult:
        """返回 {text, language, confidence}"""
        ...

class LLMProvider(Protocol):
    async def chat(self, messages: list[Message]) -> LLMResponse:
        """返回 {reply, translation}"""
        ...

    async def chat_stream(self, messages: list[Message]) -> AsyncIterator[str]:
        """流式输出回复 token，降低感知延迟"""
        ...

class TTSProvider(Protocol):
    async def synthesize(self, text: str, language: str) -> bytes:
        """返回音频数据"""
        ...

    async def synthesize_stream(self, text_stream: AsyncIterator[str], language: str) -> AsyncIterator[bytes]:
        """从流式文本输入生成流式音频块"""
        ...

class VADProvider(Protocol):
    def is_speech(self, audio_chunk: bytes) -> bool:
        """音频块中是否包含人声"""
        ...

class WakeWordProvider(Protocol):
    def detect(self, audio_chunk: bytes) -> bool:
        """是否检测到唤醒词"""
        ...

class LangDetector(Protocol):
    def detect(self, text: str) -> LangResult:
        """返回 {language, confidence}"""
        ...

class AudioSource(Protocol):
    async def read_audio(self) -> bytes:
        """从音频源读取数据"""
        ...
    async def play_audio(self, audio: bytes) -> None:
        """播放音频到输出设备"""
        ...
    async def display(self, text: str, translation: str) -> None:
        """显示文字和翻译"""
        ...
```

### 关于 LangDetector 的说明

第一期中，语种检测来自 Whisper 的音频级检测（作为 `ASRResult.language` 返回）。`LangDetector` 接口预留给未来作为 ASR 后置验证或降级层使用（例如当 Whisper 置信度低时，用 langid/fastText 对转写文本做二次判断）。

## CosyVoice 部署

CosyVoice 作为**独立的 FastAPI sidecar 服务**运行：

```bash
# CosyVoice 运行在独立端口
python -m cosyvoice.server --port 9880
```

`TTSProvider` 实现通过 HTTP API 与 CosyVoice 通信。这样主 BabelBuddy 进程保持轻量，CosyVoice 独立管理自己的 GPU/模型资源。

第一期部署方案：
1. **本地子进程**（推荐）：BabelBuddy 将 CosyVoice 作为托管子进程启动
2. **手动启动**：用户在运行 BabelBuddy 前单独启动 CosyVoice 服务

## Porcupine 唤醒词：许可证说明

Porcupine (Picovoice) 需要 API 密钥。免费版仅支持内置关键词；自定义唤醒词（"Hello Babel"）需要 Porcupine Console 且可能有许可限制。

**第一期应对方案**：使用接近 "Hello Babel" 的内置关键词（如开发阶段用 "hey google" 占位），或使用 openWakeWord（完全离线，Apache 2.0 许可）作为替代方案。

## API 设计

| 端点 | 方法 | 说明 |
|---|---|---|
| `/api/chat` | POST | 文字消息输入，返回回复 + 翻译 |
| `/api/ws/chat` | WebSocket | 实时语音流（见上方 WebSocket 协议）|
| `/api/sessions` | GET | 获取历史会话列表 |
| `/api/sessions/{id}` | GET | 获取会话详情 |
| `/api/health` | GET | 服务健康检查（包含 Ollama、CosyVoice 状态）|

## 数据模型

ID 生成策略：所有 `id` 字段使用 UUID4。

```sql
-- 会话表
CREATE TABLE sessions (
    id TEXT PRIMARY KEY,       -- UUID4
    started_at TIMESTAMP NOT NULL,
    ended_at TIMESTAMP
);

-- 消息表
CREATE TABLE messages (
    id TEXT PRIMARY KEY,       -- UUID4
    session_id TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    role TEXT NOT NULL,        -- 'user' | 'assistant'
    content TEXT NOT NULL,     -- 原文
    translation TEXT,          -- 翻译
    language TEXT NOT NULL,    -- 'zh' | 'en'
    confidence REAL,           -- ASR 置信度（仅用户消息）
    audio_path TEXT,           -- 音频文件路径，仅存储用户消息
    created_at TIMESTAMP NOT NULL
);

-- 索引
CREATE INDEX idx_messages_session_id ON messages(session_id);
CREATE INDEX idx_messages_language ON messages(language);
CREATE INDEX idx_messages_created_at ON messages(created_at);

-- Schema 版本追踪
CREATE TABLE schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TIMESTAMP NOT NULL
);
INSERT INTO schema_version (version, applied_at) VALUES (1, CURRENT_TIMESTAMP);
```

### 音频存储策略

- **用户消息**：仅在 ASR 置信度 < 0.7 时存储音频，用于调试和质量审查
- **助手消息**：不存储音频（可按需重新合成）
- **保留期**：超过 30 天的音频文件自动清理

## 配置 (settings.yaml)

```yaml
# 模型配置
models:
  llm:
    name: "qwen2.5:32b"
    ollama_host: "http://localhost:11434"
    context_window: 20  # 保留的最大对话轮数
  asr:
    model: "large-v3"
    device: "cpu"  # 或 "mps" 用于 Apple Silicon GPU
  tts:
    host: "http://localhost:9880"
    voice_zh: "default_zh"
    voice_en: "default_en"

# 音频配置
audio:
  sample_rate: 16000
  channels: 1
  chunk_size: 4096
  silence_timeout: 30  # 秒

# 唤醒词
wake_word:
  engine: "porcupine"  # 或 "openwakeword"
  keyword: "hello_babel"

# 服务器
server:
  host: "0.0.0.0"
  port: 8000

# 存储
storage:
  database: "data/sessions.db"
  audio_dir: "data/audio"
  audio_retention_days: 30
```

## 技术栈总结

| 组件 | 技术 | 用途 |
|---|---|---|
| ASR | Whisper Large V3 | 语音转文字 + 语种检测 |
| LLM | Ollama + Qwen2.5-32B | 对话生成 |
| TTS | CosyVoice（sidecar 服务）| 文字转语音（中文 + 英文）|
| 唤醒词 | Porcupine / openWakeWord | "Hello Babel" 检测 |
| VAD | Silero VAD | 语音活动检测 |
| 后端 | FastAPI + WebSocket | API 服务器 |
| 前端 | React | Web UI |
| 数据库 | SQLite | 对话历史 |
| 配置 | YAML | 应用配置 |
