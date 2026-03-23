import pytest
from unittest.mock import AsyncMock, MagicMock
from babel_buddy.core.engine import BabelEngine
from babel_buddy.core.conversation import ConversationState
from babel_buddy.models import ASRResult, LLMResponse

@pytest.fixture
def mock_providers():
    asr = AsyncMock()
    asr.transcribe.return_value = ASRResult(text="你好", language="zh", confidence=0.95)
    llm = AsyncMock()
    llm.chat.return_value = LLMResponse(reply="你好！", translation="Hello!", language="zh")
    tts = AsyncMock()
    tts.synthesize.return_value = b"\x00\x01\x02"
    vad = MagicMock()
    vad.is_speech.return_value = True
    store = AsyncMock()
    store.create_session.return_value = MagicMock(id="session-1")
    return {"asr": asr, "llm": llm, "tts": tts, "vad": vad, "store": store}

@pytest.fixture
def engine(mock_providers):
    return BabelEngine(
        asr=mock_providers["asr"],
        llm=mock_providers["llm"],
        tts=mock_providers["tts"],
        vad=mock_providers["vad"],
        session_store=mock_providers["store"],
    )

async def test_process_audio_turn(engine, mock_providers):
    await engine.start_session()
    result = await engine.process_audio(b"\x00" * 4096)
    assert result.reply == "你好！"
    assert result.audio is not None
    mock_providers["asr"].transcribe.assert_called_once()
    mock_providers["tts"].synthesize.assert_called_once()

async def test_process_detects_exit_phrase(engine, mock_providers):
    mock_providers["asr"].transcribe.return_value = ASRResult(
        text="bye babel", language="en", confidence=0.9
    )
    await engine.start_session()
    result = await engine.process_audio(b"\x00" * 4096)
    assert result.is_exit is True

async def test_start_session(engine):
    await engine.start_session()
    assert engine.conversation.state == ConversationState.LISTENING

async def test_process_text(engine, mock_providers):
    await engine.start_session()
    result = await engine.process_text("你好", "zh")
    assert result.reply == "你好！"
    assert result.language == "zh"
    mock_providers["llm"].chat.assert_called_once()

async def test_process_text_auto_detect_chinese(engine, mock_providers):
    await engine.start_session()
    result = await engine.process_text("你好世界", "auto")
    assert result.language == "zh"

async def test_process_text_auto_detect_english(engine, mock_providers):
    await engine.start_session()
    result = await engine.process_text("hello world", "auto")
    assert result.language == "en"

async def test_process_text_exit_phrase(engine, mock_providers):
    await engine.start_session()
    result = await engine.process_text("bye babel")
    assert result.is_exit is True
