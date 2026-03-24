import aiosqlite
from datetime import datetime
from uuid import uuid4
from babel_buddy.models import Session, Message

SCHEMA = """
CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,
    started_at TIMESTAMP NOT NULL,
    ended_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS messages (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    translation TEXT,
    language TEXT NOT NULL,
    confidence REAL,
    audio_path TEXT,
    created_at TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_messages_session_id ON messages(session_id);
CREATE INDEX IF NOT EXISTS idx_messages_language ON messages(language);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at);

CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TIMESTAMP NOT NULL
);

INSERT OR IGNORE INTO schema_version (version, applied_at) VALUES (1, CURRENT_TIMESTAMP);
"""


class SessionStore:
    def __init__(self, db_path: str):
        self._db_path = db_path
        self._db: aiosqlite.Connection | None = None

    async def initialize(self) -> None:
        self._db = await aiosqlite.connect(self._db_path)
        self._db.row_factory = aiosqlite.Row
        await self._db.executescript(SCHEMA)

    async def close(self) -> None:
        if self._db:
            await self._db.close()

    async def create_session(self) -> Session:
        session = Session(id=str(uuid4()), started_at=datetime.now())
        await self._db.execute(
            "INSERT INTO sessions (id, started_at) VALUES (?, ?)",
            (session.id, session.started_at.isoformat()),
        )
        await self._db.commit()
        return session

    async def end_session(self, session_id: str) -> None:
        now = datetime.now()
        await self._db.execute(
            "UPDATE sessions SET ended_at = ? WHERE id = ?",
            (now.isoformat(), session_id),
        )
        await self._db.commit()

    async def get_session(self, session_id: str) -> Session | None:
        cursor = await self._db.execute(
            "SELECT id, started_at, ended_at FROM sessions WHERE id = ?",
            (session_id,),
        )
        row = await cursor.fetchone()
        if row is None:
            return None
        return Session(
            id=row["id"],
            started_at=datetime.fromisoformat(row["started_at"]),
            ended_at=datetime.fromisoformat(row["ended_at"]) if row["ended_at"] else None,
        )

    async def list_sessions(self, limit: int = 50) -> list[Session]:
        cursor = await self._db.execute(
            "SELECT id, started_at, ended_at FROM sessions ORDER BY started_at DESC LIMIT ?",
            (limit,),
        )
        rows = await cursor.fetchall()
        return [
            Session(
                id=r["id"],
                started_at=datetime.fromisoformat(r["started_at"]),
                ended_at=datetime.fromisoformat(r["ended_at"]) if r["ended_at"] else None,
            )
            for r in rows
        ]

    async def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        translation: str | None,
        language: str,
        confidence: float | None,
        audio_path: str | None,
    ) -> Message:
        msg = Message(
            id=str(uuid4()),
            session_id=session_id,
            role=role,
            content=content,
            translation=translation,
            language=language,
            confidence=confidence,
            audio_path=audio_path,
            created_at=datetime.now(),
        )
        await self._db.execute(
            """INSERT INTO messages (id, session_id, role, content, translation, language, confidence, audio_path, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                msg.id,
                msg.session_id,
                msg.role,
                msg.content,
                msg.translation,
                msg.language,
                msg.confidence,
                msg.audio_path,
                msg.created_at.isoformat(),
            ),
        )
        await self._db.commit()
        return msg

    async def get_messages(self, session_id: str) -> list[Message]:
        cursor = await self._db.execute(
            "SELECT * FROM messages WHERE session_id = ? ORDER BY created_at",
            (session_id,),
        )
        rows = await cursor.fetchall()
        return [
            Message(
                id=r["id"],
                session_id=r["session_id"],
                role=r["role"],
                content=r["content"],
                translation=r["translation"],
                language=r["language"],
                confidence=r["confidence"],
                audio_path=r["audio_path"],
                created_at=datetime.fromisoformat(r["created_at"]),
            )
            for r in rows
        ]
