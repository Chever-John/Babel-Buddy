import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from babel_buddy.speech.asr import WhisperASR
from babel_buddy.models import ASRResult

def test_whisper_asr_implements_protocol():
    asr = WhisperASR.__new__(WhisperASR)
    assert hasattr(asr, "transcribe")

@patch("babel_buddy.speech.asr.whisper")
def test_whisper_asr_init(mock_whisper):
    mock_whisper.load_model.return_value = MagicMock()
    asr = WhisperASR(model_name="base", device="cpu")
    mock_whisper.load_model.assert_called_once_with("base", device="cpu")

@pytest.mark.asyncio
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
