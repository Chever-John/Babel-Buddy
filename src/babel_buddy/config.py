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
