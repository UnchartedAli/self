from telethon import TelegramClient
from config import API_ID, API_HASH, SESSION_NAME
from core.database import Database


class RezeClient(TelegramClient):
    def __init__(self):
        super().__init__(SESSION_NAME, API_ID, API_HASH)
        self.db = Database()

    async def start_client(self):
        await self.db.init()
        await self.start()
        print("✅ Reze شروع به کار کرد...")
        me = await self.get_me()
        print(f"👤 لاگین شده به عنوان: {me.first_name} (@{me.username or 'بدون یوزرنیم'})")
        return self