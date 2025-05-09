import os
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    CommandHandler,
    CallbackQueryHandler,
    filters,
)
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = -1002677193801  # Your channel ID

# To track last message time per user
last_sent = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📎 لینک‌ها", callback_data="links")],
        [InlineKeyboardButton("📝 ارسال پیام (هر یک ساعت)", callback_data="send_message")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("یکی از گزینه‌های زیر را انتخاب کنید:", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == "links":
        keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("در آینده لینک‌ها اینجا نمایش داده خواهند شد.", reply_markup=reply_markup)

    elif query.data == "send_message":
        keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="back")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "لطفاً پیام خود را ارسال کنید.\n(مجاز به ارسال یک پیام در هر یک ساعت هستید)",
            reply_markup=reply_markup
        )
        context.user_data["awaiting_message"] = True

    elif query.data == "back":
        keyboard = [
            [InlineKeyboardButton("📎 لینک‌ها", callback_data="links")],
            [InlineKeyboardButton("📝 ارسال پیام (هر یک ساعت)", callback_data="send_message")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("یکی از گزینه‌های زیر را انتخاب کنید:", reply_markup=reply_markup)

async def forward_to_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not user or not update.message or not update.message.text:
        return

    if not context.user_data.get("awaiting_message"):
        return

    now = time.time()
    user_id = user.id
    last = last_sent.get(user_id, 0)

    if now - last < 3600:
        retry_in = int(3600 - (now - last)) // 60 + 1
        await update.message.reply_text(
            f"شما فقط می‌توانید هر یک ساعت یک پیام ارسال کنید.\nلطفاً {retry_in} دقیقهٔ دیگر تلاش کنید."
        )
        return

    last_sent[user_id] = now
    context.user_data["awaiting_message"] = False

    text = update.message.text
    username = user.username or user.first_name or str(user.id)

    await context.bot.send_message(
        chat_id=GROUP_ID,
        text=f"From @{username}:\n{text}"
    )

    await update.message.reply_text("✅ پیام شما با موفقیت ارسال شد. ممنون از مشارکت‌تان!")

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), forward_to_group))

    print("Bot is running…")
    app.run_polling()
