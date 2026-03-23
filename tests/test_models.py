from babel_buddy.models import (
    ASRResult, LLMResponse, Message, Session,
    ASRProvider, LLMProvider, TTSProvider, VADProvider, WakeWordProvider,
)
from datetime import datetime

def test_asr_result_creation():
    result = ASRResult(text="你好", language="zh", confidence=0.95)
    assert result.text == "你好"
    assert result.language == "zh"
    assert result.confidence == 0.95

def test_message_creation():
    msg = Message(
        id="test-id",
        session_id="session-1",
        role="user",
        content="Hello",
        translation=None,
        language="en",
        confidence=0.9,
        audio_path=None,
        created_at=datetime.now(),
    )
    assert msg.role == "user"
    assert msg.language == "en"

def test_llm_response():
    resp = LLMResponse(reply="你好！", translation="Hello!", language="zh")
    assert resp.reply == "你好！"
    assert resp.translation == "Hello!"
