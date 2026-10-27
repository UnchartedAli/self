import aiosqlite
from datetime import datetime
from config import DB_NAME, SAVE_MEDIA_MESSAGES


class Database:
    def __init__(self):
        self.db_name = DB_NAME

    async def init(self):
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message_id INTEGER,
                    user_id INTEGER,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    chat_id INTEGER,
                    chat_title TEXT,
                    message_text TEXT,
                    message_date TEXT,
                    deleted_date TEXT,
                    UNIQUE(message_id, chat_id)
                )
            """)
            await db.commit()

    async def save_message(self, message):
        try:
            user = message.sender
            chat = message.chat

            text = message.text
            if not text and SAVE_MEDIA_MESSAGES:
                text = "[Media / Non-text message]"

            async with aiosqlite.connect(self.db_name) as db:
                await db.execute("""
                    INSERT OR REPLACE INTO messages
                    (message_id, user_id, username, first_name, last_name,
                     chat_id, chat_title, message_text, message_date, deleted_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, NULL)
                """, (
                    message.id,
                    user.id if user else None,
                    getattr(user, "username", None),
                    getattr(user, "first_name", None),
                    getattr(user, "last_name", None),
                    message.chat_id,
                    getattr(chat, "title", None) or getattr(chat, "first_name", None),
                    text,
                    message.date.isoformat() if message.date else None,
                ))
                await db.commit()
        except Exception as e:
            print(f"[DB] Error saving message: {e}")

    async def mark_as_deleted(self, message_ids: list, chat_id: int):
        try:
            now = datetime.utcnow().isoformat()
            async with aiosqlite.connect(self.db_name) as db:
                for mid in message_ids:
                    await db.execute("""
                        UPDATE messages
                        SET deleted_date = ?
                        WHERE message_id = ? AND chat_id = ? AND deleted_date IS NULL
                    """, (now, mid, chat_id))
                await db.commit()
        except Exception as e:
            print(f"[DB] Error marking deleted: {e}")

    async def get_deleted_by_user(self, user_id: int, limit: int = 15):
        async with aiosqlite.connect(self.db_name) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("""
                SELECT * FROM messages
                WHERE user_id = ? AND deleted_date IS NOT NULL
                ORDER BY deleted_date DESC
                LIMIT ?
            """, (user_id, limit))
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def get_stats(self):
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute("SELECT COUNT(*) FROM messages")
            total = (await cursor.fetchone())[0]

            cursor = await db.execute("SELECT COUNT(*) FROM messages WHERE deleted_date IS NOT NULL")
            deleted = (await cursor.fetchone())[0]

            cursor = await db.execute("SELECT COUNT(DISTINCT chat_id) FROM messages")
            chats = (await cursor.fetchone())[0]

            cursor = await db.execute("SELECT COUNT(DISTINCT user_id) FROM messages WHERE deleted_date IS NOT NULL")
            users = (await cursor.fetchone())[0]

            return {
                "total_messages": total,
                "deleted_messages": deleted,
                "tracked_chats": chats,
                "users_with_deletes": users
            }

    async def get_recent(self, limit: int = 10):
        async with aiosqlite.connect(self.db_name) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("""
                SELECT * FROM messages
                ORDER BY id DESC
                LIMIT ?
            """, (limit,))
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]