import pytest
import base64
from unittest.mock import AsyncMock, MagicMock
from starlette.testclient import TestClient
from babel_buddy.api.main import create_app
from babel_buddy.core.engine import TurnResult

@pytest.fixture
def mock_engine():
    engine = AsyncMock()
    engine.conversation = MagicMock()
    engine.conversation.state = MagicMock(value="idle")
    engine.start_session.return_value = "session-1"
    engine.process_audio.return_value = TurnResult(
        transcript="你好", language="zh",
        reply="你好！", translation="Hello!",
        audio=b"\x00\x01",
    )
    return engine

def test_websocket_chat_flow(mock_engine):
    app = create_app(engine=mock_engine, session_store=AsyncMock())
    client = TestClient(app)
    with client.websocket_connect("/api/ws/chat") as ws:
        ws.send_json({"type": "control", "action": "start_session"})
        resp = ws.receive_json()
        assert resp["type"] == "state"

        audio_b64 = base64.b64encode(b"\x00" * 4096).decode()
        ws.send_json({"type": "audio", "data": audio_b64})
        messages = []
        for _ in range(4):
            messages.append(ws.receive_json())
        types = {m["type"] for m in messages}
        assert "transcript" in types
        assert "reply" in types
