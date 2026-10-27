from telethon import events
from config import ADMIN_ID, NOTIFY_DELETIONS, MAX_SEARCH_RESULTS, MAX_MESSAGE_DISPLAY_LENGTH, CMD_PREFIX


def register(client):
    """ثبت رویدادها و دستورات DeleteWatch"""

    # ---------- ذخیره همه پیام‌های جدید ----------
    @client.on(events.NewMessage)
    async def save_incoming(event):
        # پیام‌های خودمان رو هم ذخیره می‌کنیم (اختیاری)
        await client.db.save_message(event.message)

    # ---------- تشخیص پیام پاک‌شده ----------
    @client.on(events.MessageDeleted)
    async def on_deleted(event):
        if not event.deleted_ids:
            return

        chat_id = event.chat_id
        await client.db.mark_as_deleted(event.deleted_ids, chat_id)

        if NOTIFY_DELETIONS and ADMIN_ID:
            try:
                # سعی می‌کنیم اطلاعات بیشتری پیدا کنیم
                text = f"🗑️ **پیام پاک شد**\n\n"
                text += f"• تعداد: `{len(event.deleted_ids)}`\n"
                text += f"• چت ID: `{chat_id}`\n"
                text += f"• شناسه‌ها: `{event.deleted_ids[:5]}{'...' if len(event.deleted_ids) > 5 else ''}`"

                await client.send_message(ADMIN_ID, text)
            except Exception:
                pass

    # ---------- دستورات ادمین ----------
    @client.on(events.NewMessage(from_users=ADMIN_ID, pattern=rf"\{CMD_PREFIX}search(?: |$)(.*)"))
    async def cmd_search(event):
        args = event.pattern_match.group(1).strip()
        if not args or not args.isdigit():
            await event.reply(f"❗ استفاده صحیح:\n`{CMD_PREFIX}search <user_id>`\n\nمثال:\n`{CMD_PREFIX}search 123456789`")
            return

        user_id = int(args)
        results = await client.db.get_deleted_by_user(user_id, MAX_SEARCH_RESULTS)

        if not results:
            await event.reply(f"❌ هیچ پیام پاک‌شده‌ای از کاربر `{user_id}` پیدا نشد.")
            return

        text = f"🔍 **نتایج جستجو برای** `{user_id}`\n"
        text += f"تعداد نمایش: {len(results)}\n\n"

        for i, msg in enumerate(results, 1):
            preview = (msg["message_text"] or "بدون متن")[:MAX_MESSAGE_DISPLAY_LENGTH]
            text += (
                f"**{i}.**\n"
                f"• چت: `{msg['chat_title'] or msg['chat_id']}`\n"
                f"• تاریخ ارسال: `{msg['message_date']}`\n"
                f"• تاریخ پاک شدن: `{msg['deleted_date']}`\n"
                f"• متن: `{preview}`\n\n"
            )

        await event.reply(text)

    @client.on(events.NewMessage(from_users=ADMIN_ID, pattern=rf"\{CMD_PREFIX}stats$"))
    async def cmd_stats(event):
        stats = await client.db.get_stats()
        text = (
            "📊 **آمار Reze - DeleteWatch**\n\n"
            f"• کل پیام‌های ذخیره‌شده: `{stats['total_messages']}`\n"
            f"• پیام‌های پاک‌شده: `{stats['deleted_messages']}`\n"
            f"• چت‌های مانیتور شده: `{stats['tracked_chats']}`\n"
            f"• کاربران دارای پیام پاک‌شده: `{stats['users_with_deletes']}`"
        )
        await event.reply(text)

    @client.on(events.NewMessage(from_users=ADMIN_ID, pattern=rf"\{CMD_PREFIX}debug$"))
    async def cmd_debug(event):
        rows = await client.db.get_recent(10)
        if not rows:
            await event.reply("دیتابیس خالی است.")
            return

        text = "🛠 **۱۰ پیام اخیر دیتابیس:**\n\n"
        for i, msg in enumerate(rows, 1):
            status = "🗑️ پاک شده" if msg["deleted_date"] else "✅ فعال"
            preview = (msg["message_text"] or "-")[:40]
            text += (
                f"**{i}.** `{msg['message_id']}` | {status}\n"
                f"کاربر: `{msg['user_id']}` | چت: `{msg['chat_id']}`\n"
                f"`{preview}`\n\n"
            )
        await event.reply(text)

    @client.on(events.NewMessage(from_users=ADMIN_ID, pattern=rf"\{CMD_PREFIX}help$"))
    async def cmd_help(event):
        text = (
            "🤖 **Reze Userbot - راهنما**\n\n"
            f"**دستورات DeleteWatch:**\n"
            f"`{CMD_PREFIX}search <user_id>` - جستجوی پیام‌های پاک‌شده یک کاربر\n"
            f"`{CMD_PREFIX}stats` - آمار کلی\n"
            f"`{CMD_PREFIX}debug` - نمایش ۱۰ پیام اخیر دیتابیس\n"
            f"`{CMD_PREFIX}help` - همین پیام\n"
            f"`{CMD_PREFIX}ping` - تست سرعت\n\n"
            "📌 پیشوند دستورات: `.`\n"
            "توسعه‌دهنده: بر اساس درخواست شما"
        )
        await event.reply(text)

    print("✅ پلاگین DeleteWatch لود شد")