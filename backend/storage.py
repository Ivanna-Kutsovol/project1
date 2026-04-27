import sqlite3
from pathlib import Path
from typing import Dict, List


BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database" / "chatbot.db"

ANALYTICS_TOPICS = (
    "total_messages",
    "faq",
    "contacts",
    "services",
    "about",
    "delivery",
    "payment",
    "returns",
    "navigation",
    "support",
    "gpt",
    "unknown",
)


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                text TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS analytics (
                topic TEXT PRIMARY KEY,
                count INTEGER NOT NULL DEFAULT 0
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                summary TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.executemany(
            "INSERT OR IGNORE INTO analytics(topic, count) VALUES (?, 0)",
            [(topic,) for topic in ANALYTICS_TOPICS],
        )


def add_message_to_db(session_id: str, role: str, text: str) -> None:
    init_db()
    with get_connection() as connection:
        connection.execute(
            "INSERT INTO messages(session_id, role, text) VALUES (?, ?, ?)",
            (session_id, role, text),
        )


def get_history_from_db(session_id: str) -> List[dict[str, str]]:
    init_db()
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT role, text
            FROM messages
            WHERE session_id = ?
            ORDER BY id ASC
            """,
            (session_id,),
        ).fetchall()
    return [{"role": row["role"], "text": row["text"]} for row in rows]


def increment_analytics(topic: str) -> None:
    init_db()
    normalized_topic = topic if topic in ANALYTICS_TOPICS else "unknown"
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO analytics(topic, count)
            VALUES (?, 1)
            ON CONFLICT(topic) DO UPDATE SET count = count + 1
            """,
            (normalized_topic,),
        )


def get_analytics_from_db() -> Dict[str, int]:
    init_db()
    with get_connection() as connection:
        rows = connection.execute("SELECT topic, count FROM analytics").fetchall()
    data = {topic: 0 for topic in ANALYTICS_TOPICS}
    data.update({row["topic"]: int(row["count"]) for row in rows})
    return data


def save_contact(name: str, email: str, message: str) -> dict:
    init_db()
    with get_connection() as connection:
        cursor = connection.execute(
            "INSERT INTO contacts(name, email, message) VALUES (?, ?, ?)",
            (name, email, message),
        )
        contact_id = cursor.lastrowid
    return {"id": contact_id, "name": name, "email": email, "message": message}


def create_article(title: str, summary: str, content: str) -> dict:
    init_db()
    with get_connection() as connection:
        cursor = connection.execute(
            "INSERT INTO articles(title, summary, content) VALUES (?, ?, ?)",
            (title, summary, content),
        )
        article_id = cursor.lastrowid
        row = connection.execute(
            """
            SELECT id, title, summary, content, created_at
            FROM articles
            WHERE id = ?
            """,
            (article_id,),
        ).fetchone()
    return dict(row)


def list_articles() -> List[dict]:
    init_db()
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, title, summary, content, created_at
            FROM articles
            ORDER BY id DESC
            """
        ).fetchall()
    return [dict(row) for row in rows]
