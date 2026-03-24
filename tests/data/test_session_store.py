import pytest
from babel_buddy.data.session_store import SessionStore

@pytest.fixture
async def store(tmp_path):
    db_path = str(tmp_path / "test.db")
    s = SessionStore(db_path)
    await s.initialize()
    yield s
    await s.close()

async def test_create_and_get_session(store):
    session = await store.create_session()
    assert session.id is not None
    assert session.ended_at is None
    fetched = await store.get_session(session.id)
    assert fetched.id == session.id

async def test_end_session(store):
    session = await store.create_session()
    await store.end_session(session.id)
    fetched = await store.get_session(session.id)
    assert fetched.ended_at is not None

async def test_add_and_list_messages(store):
    session = await store.create_session()
    await store.add_message(
        session_id=session.id, role="user", content="你好",
        translation=None, language="zh", confidence=0.95, audio_path=None,
    )
    await store.add_message(
        session_id=session.id, role="assistant", content="你好！我是Babel",
        translation="Hello! I'm Babel", language="zh", confidence=None, audio_path=None,
    )
    messages = await store.get_messages(session.id)
    assert len(messages) == 2
    assert messages[0].role == "user"
    assert messages[1].role == "assistant"

async def test_list_sessions(store):
    await store.create_session()
    await store.create_session()
    sessions = await store.list_sessions()
    assert len(sessions) == 2

async def test_get_nonexistent_session(store):
    result = await store.get_session("nonexistent")
    assert result is None
