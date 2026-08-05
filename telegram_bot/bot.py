from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from config import BOT_TOKEN
from database.database import get_queries, add_query, delete_query, get_queries_with_id, add_user, user_exists
from logger import logger

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    username = update.effective_user.username
    add_user(chat_id, username)
    logger.info(
         f"Новый пользователь запустил бота: "
         f"Username={username}, chat_id={chat_id}"
    )
    await update.message.reply_text("🔥WB Price Hunter запущен!")

async def id_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.message.chat_id

        await update.message.reply_text(f"Твой Telegram ID: {user_id}")

async def list_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    chat_id = update.effective_chat.id

    queries = get_queries_with_id(chat_id)

    if not queries:
        await update.message.reply_text(
            "📋 У тебя пока нет отслеживаемых запросов."
        )
        return

    text = "🧾 Твои запросы:\n\n"

    for index, query in enumerate(queries, start=1):
        text += f"{index}. {query[1]}\n"

    text += "\nУдалить запрос:\n/remove номер"

    await update.message.reply_text(text)

async def add_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        if not user_exists(chat_id):
             await update.message.reply_text(
                "❌ Сначала запусти бота: \n/start"
             )
             return
        if not context.args:
            await update.message.reply_text(
                 "❌ Напиши запрос после команды. \n\nПример: \n/add airpods pro"
            )
            return
        query = " ".join(context.args)
        add_query(chat_id, query)
        logger.info(
             f"Добавлен запрос: "
             f"Query='{query}', chat_id={chat_id}"
        )
        await update.message.reply_text(
             f"✅ Добавил в отслеживание: \n\n{query}"
        )

async def remove_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    chat_id = update.effective_chat.id

    if not context.args:
        await update.message.reply_text(
            "❌ Укажи номер запроса.\n\nПример:\n/remove 2"
        )
        return

    try:
        position = int(context.args[0])

    except ValueError:
        logger.warning(
            f"Пользователь ввёл неправильный номер запроса: "
            f"chat_id={chat_id}, value={context.args[0]}"
        )

        await update.message.reply_text(
            "❌ Нужно указать число.\n\nПример:\n/remove 2"
        )
        return

    queries = get_queries_with_id(chat_id)

    if position < 1 or position > len(queries):
        logger.warning(
            f"Пользователь ввёл неправильный номер запроса: "
            f"chat_id={chat_id}, value={context.args[0]}"
        )
        
        await update.message.reply_text(
            "❌ Нет такого номера запроса."
        )
        return

    query_id = queries[position - 1][0]
    query_name = queries[position - 1][1]

    deleted = delete_query(chat_id, query_id)
    
    if deleted:
        logger.info(
            f"Удалён запрос: "
            f"chat_id={chat_id}, query='{query_name}'"
        )
        await update.message.reply_text(
            f"🗑 Запрос удалён:\n\n{query_name}"
        )

    else:
        await update.message.reply_text(
            "❌ Не удалось удалить запрос."
        )
        

def main():
    try:
        app = Application.builder().token(BOT_TOKEN).build()

        app.add_handler(
            CommandHandler("start", start)
        )
        app.add_handler(
            CommandHandler("id", id_command)
        )
        app.add_handler(
            CommandHandler("list", list_command)
        )
        app.add_handler(
            CommandHandler("add", add_command)
        )
        app.add_handler(
            CommandHandler("remove", remove_command)
        )
        logger.info("Бот запущен")
        app.run_polling()
        
    except Exception:
         logger.exception("Ошибка Telegram бота")

if __name__ == "__main__":
    main()

    