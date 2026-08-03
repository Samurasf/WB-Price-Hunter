import asyncio
from telegram_bot.sender import send_message

async def main():
    await send_message("🔥Тестовое сообщение от WB Price Hunter")

asyncio.run(main())