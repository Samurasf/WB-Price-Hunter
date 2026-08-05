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
from logger import logger


create_database()

logger.info("Программа запустилась")


async def check_prices():
    users = get_users()

    for chat_id in users:

        SEARCH_QUERIES = get_queries(chat_id)

        for query in SEARCH_QUERIES:

            logger.info(f"Проверяем запрос: {query}")

            products = await get_products(query)

            if not products:
                logger.warning("⚠️ Нет данных")
                continue

            logger.info(f"Найдено товаров: {len(products)}")

            for product in products:

                if check_product(product):

                    old_price = get_last_price(product["id"])

                    if check_price_drop(old_price, product["price"]):

                        logger.info(f'ОБНАРУЖЕНО ПАДЕНИЕ ЦЕНЫ!')
                        logger.info(f'Товар: {product["name"]}')
                        logger.info(f'Старая цена: {old_price}')
                        logger.info(f'Новая цена: {product["price"]}')
                        logger.info(f'Chat ID: {chat_id} |')

                        already_sent = was_notification_sent(product["id"], product["price"])

                        logger.info(f"Уведомление уже отправлялось: {already_sent}")

                        if not already_sent:
                            try:
                                logger.info("Отправляем Telegram-уведомление...")

                                await send_discount_notification(
                                        product,
                                        old_price,
                                        chat_id
                                )
                                logger.info("Telegram-уведомление отправлено!")

                                save_notification(
                                    product["id"],
                                    product["price"]
                                )

                                logger.info("Уведомление сохранено в БД")

                            except Exception:
                                logger.exception("Ошибка Telegram")

                    save_price(product)

                    print(
                        "-------------------------------------------------------------------------------"
                    )

                    logger.info("Найдена скидка")

                    logger.info(
                        f'Товар: {product["name"]}'
                    )

                    logger.info(
                        f'Бренд: {product["brand"]}'
                    )

                    logger.info(
                        f'Цена: {product["price"]} руб. '
                        f'(было {product["old_price"]} руб.)'
                    )

                    logger.info(
                        f'Скидка: {product["discount"]}%'
                    )

                    logger.info(
                        f'Рейтинг: {product["rating"]} ' 
                        f'Отзывы: {product["reviews"]}'
                    )

                    if old_price:
                        logger.info(f"Прошлая цена: {old_price}")

            await asyncio.sleep(random.randint(1, 3))


async def main():
    while True:
        try:
            logger.info("===== НАЧАЛО ПРОВЕРКИ ЦЕН =====")

            await check_prices()

            logger.info("===== ПРОВЕРКА ЗАВЕРШЕНА =====")
            logger.info(
                f"Следующая проверка через {CHECK_INTERVAL} секунд"
            )
            logger.info("==============================")

            await asyncio.sleep(CHECK_INTERVAL)

            logger.info(
                "ИНТЕРВАЛ ЗАКОНЧИЛСЯ — ЗАПУСКАЕМ НОВУЮ ПРОВЕРКУ"
            )

        except KeyboardInterrupt:
            logger.warning("Программа остановлена пользователем")
            break

        except Exception:
            logger.exception(
                "Ошибка в главном цикле программы"
            )

            logger.info(
                "Ждём перед повторной попыткой..."
            )

            await asyncio.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    asyncio.run(main())