from telethon import events
from datetime import datetime
from config import ADMIN_ID, CMD_PREFIX


def register(client):
    @client.on(events.NewMessage(from_users=ADMIN_ID, pattern=rf"\{CMD_PREFIX}ping$"))
    async def cmd_ping(event):
        start = datetime.now()
        msg = await event.reply("🏓 Pong...")
        end = datetime.now()
        ms = (end - start).microseconds / 1000
        await msg.edit(f"🏓 **Pong!**\n`{ms:.2f} ms`")

    print("✅ پلاگین Ping لود شد")