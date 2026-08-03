from telegram_bot.sender import send_message

async def send_discount_notification(product, old_price, chat_id):
    drop_percent = round(
        (1 - product["price"] / old_price) * 100
    )

    text = f"""
🔥РЕЗКОЕ ПАДЕНИЕ ЦЕНЫ
🛍 {product["name"]}
🔖 Бренд: {product["brand"]}

💰 Было: {old_price}
🔥 Сейчас: {product["price"]}

📉 Падение: {drop_percent}%

⭐ Рейтинг: {product["rating"]}
💬 Отзывов: {product["reviews"]}
🔗 https://www.wildberries.ru/catalog/{product["id"]}/detail.aspx
"""
    await send_message(text, chat_id)