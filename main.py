import asyncio
import os
from config import API_ID, API_HASH, ADMIN_ID
from core.client import RezeClient

# لود کردن پلاگین‌ها
from plugins import deletewatch, ping


async def main():
    if not API_ID or not API_HASH:
        print("❌ خطا: API_ID و API_HASH رو داخل فایل .env بذار")
        print("از https://my.telegram.org بگیرشون")
        return

    if not ADMIN_ID:
        print("❌ خطا: ADMIN_ID رو داخل فایل .env بذار")
        print("آیدی عددیت رو از @userinfobot بگیر")
        return

    client = RezeClient()

    # ثبت پلاگین‌ها
    deletewatch.register(client)
    ping.register(client)

    try:
        await client.start_client()
        print("♻️ در حال اجرا... (برای توقف Ctrl+C)")
        await client.run_until_disconnected()
    except KeyboardInterrupt:
        print("\n🛑 متوقف شد")
    except Exception as e:
        print(f"❌ خطا: {e}")


if __name__ == "__main__":
    asyncio.run(main())