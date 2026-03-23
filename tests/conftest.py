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
