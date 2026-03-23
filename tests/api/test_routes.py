import pytest
from unittest.mock import AsyncMock, MagicMock
from httpx import AsyncClient, ASGITransport
from babel_buddy.api.main import create_app
from babel_buddy.core.engine import TurnResult

@pytest.fixture
def mock_engine():
    engine = AsyncMock()
    engine.conversation = MagicMock()
    engine.conversation.history = []
    engine.conversation.state = MagicMock(value="idle")
    return engine

@pytest.fixture
def mock_store():
    store = AsyncMock()
    store.list_sessions.return_value = []
    store.get_session.return_value = None
    store.get_messages.return_value = []
    return store

@pytest.fixture
async def client(mock_engine, mock_store):
    app = create_app(engine=mock_engine, session_store=mock_store)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c

async def test_health_check(client):
    resp = await client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert "status" in data

async def test_list_sessions(client):
    resp = await client.get("/api/sessions")
    assert resp.status_code == 200
    assert resp.json() == []

async def test_chat_endpoint(client, mock_engine):
    mock_engine.process_text.return_value = TurnResult(
        transcript="Hello", language="en",
        reply="Hi there!", translation="你好！",
        audio=None,
    )
    resp = await client.post("/api/chat", json={"text": "Hello", "language": "en"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["reply"] == "Hi there!"
