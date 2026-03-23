from babel_buddy.llm.prompt import build_system_prompt, build_messages
from babel_buddy.models import Message
from datetime import datetime

def test_build_system_prompt_chinese():
    prompt = build_system_prompt("zh")
    assert "Chinese" in prompt or "zh" in prompt
    assert "Translation" in prompt

def test_build_system_prompt_english():
    prompt = build_system_prompt("en")
    assert "English" in prompt or "en" in prompt

def test_build_messages_includes_history():
    history = [
        Message(id="1", session_id="s1", role="user", content="Hello",
                translation=None, language="en", confidence=0.9,
                audio_path=None, created_at=datetime.now()),
        Message(id="2", session_id="s1", role="assistant",
                content="Hi there!", translation="你好！",
                language="en", confidence=None, audio_path=None,
                created_at=datetime.now()),
    ]
    messages = build_messages(history, "你好", "zh")
    assert messages[0]["role"] == "system"
    assert messages[-1]["role"] == "user"
    assert messages[-1]["content"] == "你好"

def test_build_messages_respects_context_window():
    history = [
        Message(id=str(i), session_id="s1", role="user", content=f"msg {i}",
                translation=None, language="en", confidence=0.9,
                audio_path=None, created_at=datetime.now())
        for i in range(30)
    ]
    messages = build_messages(history, "latest", "en", max_turns=20)
    # system + last 20 history + current user = 22
    assert len(messages) == 22
