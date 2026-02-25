from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import os 
from dotenv import load_dotenv

load_dotenv()



BOT_TOKEN = os.getenv("BOT_TOKEN")


async def handle_message(update, context):
    user_text = update.message.text
    await update.message.reply_text(f"You said: {user_text}")


app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("Bot is running...")
app.run_polling()