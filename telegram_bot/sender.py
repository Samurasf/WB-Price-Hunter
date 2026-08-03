from telegram import Bot
from config import BOT_TOKEN

async def send_message(text, chat_id):
    bot = Bot(token=BOT_TOKEN)

    await bot.send_message(
        chat_id = chat_id,
        text = text
    )