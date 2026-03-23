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
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            tmp_path = f.name
            with wave.open(f, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
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
        segments = result.get("segments", [])
        if segments:
            confidence = sum(s.get("no_speech_prob", 0) for s in segments) / len(segments)
            confidence = 1.0 - confidence
        else:
            confidence = 0.0
        return ASRResult(text=text, language=language, confidence=confidence)
