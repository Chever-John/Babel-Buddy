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
