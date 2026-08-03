import time
import random
import asyncio

from telegram_bot.notifications import send_discount_notification
from parser.wildberries import get_products, close_browser
from analyzer.discount_checker import check_product
from database.database import (
    create_database,
    save_price,
    get_last_price,
    was_notification_sent,
    save_notification,
    get_queries,
    get_users
)
from analyzer.price_drop_checker import check_price_drop
from settings import CHECK_INTERVAL


create_database()

print("Программа запустилась")


async def check_prices():
    users = get_users()

    for chat_id in users:

        SEARCH_QUERIES = get_queries(chat_id)

        for query in SEARCH_QUERIES:

            print(f"\n🔍 Проверяем запрос: {query}")

            products = await get_products(query)

            if not products:
                print("⚠️ Нет данных")
                continue

            print(f"Найдено товаров: {len(products)}")

            for product in products:

                if check_product(product):

                    old_price = get_last_price(product["id"])

                    if check_price_drop(old_price, product["price"]):

                        print("🔥🔥🔥 ОБНАРУЖЕНО ПАДЕНИЕ ЦЕНЫ!")
                        print("Товар:", product["name"])
                        print("Старая цена:", old_price)
                        print("Новая цена:", product["price"])
                        print("Chat ID:", chat_id)

                        already_sent = was_notification_sent(product["id"], product["price"])

                        print("Уведомление уже отправлялось:", already_sent)

                        if not already_sent:
                            try:
                                print("📨 Отправляем Telegram-уведомление...")

                                await send_discount_notification(
                                        product,
                                        old_price,
                                        chat_id
                                )
                                print("✅ Telegram-уведомление отправлено!")

                                save_notification(
                                    product["id"],
                                    product["price"]
                                )

                                print("✅ Уведомление сохранено в БД")

                            except Exception as e:
                                print("❌ ОШИБКА TELEGRAM:")
                                print(type(e).__name__, e)

                    save_price(product)

                    print(
                        "-------------------------------------------------------------------------------"
                    )

                    print("НАЙДЕНА СКИДКА!")
                    print("Название:", product["name"])
                    print("Бренд:", product["brand"])
                    print("Цена:", product["price"], "руб.")
                    print("Старая цена:", product["old_price"], "руб.")
                    print("Скидка:", product["discount"], "%")
                    print("Рейтинг:", product["rating"])
                    print("Отзывы:", product["reviews"])

                    if old_price:
                        print("Прошлая цена:", old_price)

            await asyncio.sleep(random.randint(1, 3))


async def main():
    while True:
        try:
            print("\n==============================")
            print("🔍 НАЧАЛО ПРОВЕРКИ ЦЕН")
            print("==============================")

            await check_prices()

            print("\n==============================")
            print("✅ ПРОВЕРКА ЗАВЕРШЕНА")
            print(f"⏳ Следующая проверка через {CHECK_INTERVAL} секунд")
            print("==============================")

            await asyncio.sleep(CHECK_INTERVAL)

            print("\n🔄 ИНТЕРВАЛ ЗАКОНЧИЛСЯ — ЗАПУСКАЕМ НОВУЮ ПРОВЕРКУ")

        except KeyboardInterrupt:
            print("\n🛑 Программа остановлена")
            break

        except Exception as e:
            print("\n❌ ОШИБКА В ГЛАВНОМ ЦИКЛЕ:")
            print(type(e).__name__, e)

            print("⏳ Ждём перед повторной попыткой...")
            await asyncio.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    asyncio.run(main())