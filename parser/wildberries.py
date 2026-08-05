from playwright.async_api import async_playwright
from urllib.parse import quote_plus
from logger import logger
import json


_playwright = None
_browser = None
_context = None
_page = None


async def start_browser():
    global _playwright, _browser, _context, _page

    if _page is not None:
        return _page

    logger.info("Запускаем браузер Wildberries...")

    _playwright = await async_playwright().start()

    _browser = await _playwright.chromium.launch(
        headless=False
    )

    _context = await _browser.new_context(
        locale="ru-RU",
        timezone_id="Europe/Moscow",
        viewport={
            "width": 1920,
            "height": 1080
        }
    )

    _page = await _context.new_page()

    logger.info("Браузер запущен")

    return _page


async def close_browser():
    global _playwright, _browser, _context, _page

    try:
        if _page and not _page.is_closed():
            await _page.close()

        if _context:
            await _context.close()

        if _browser:
            await _browser.close()

        if _playwright:
            await _playwright.stop()

    except Exception:
        logger.exception(f"Ошибка при закрытии браузера")

    finally:
        _page = None
        _context = None
        _browser = None
        _playwright = None


def parse_products(data):
    products = []

    for item in data.get("products", []):

        try:
            if not item.get("sizes"):
                continue

            price_data = item["sizes"][0].get("price", {})

            product_price = price_data.get("product")
            basic_price = price_data.get("basic")

            if product_price is None or basic_price is None:
                continue

            product_price = product_price / 100
            basic_price = basic_price / 100

            if basic_price > 0:
                discount = round(
                    (1 - product_price / basic_price) * 100
                )
            else:
                discount = 0

            product = {
                "id": item.get("id"),
                "name": item.get("name", ""),
                "brand": item.get("brand", ""),
                "rating": item.get("reviewRating", 0),
                "reviews": item.get("feedbacks", 0),
                "price": product_price,
                "old_price": basic_price,
                "discount": discount
            }

            products.append(product)

        except Exception:
            logger.exception(
                f"⚠️ Ошибка обработки товара "
                f"{item.get('id')}"
            )

    return products


async def get_products(query):
    page = await start_browser()

    search_url = (
        "https://www.wildberries.ru/catalog/0/search.aspx"
        f"?search={quote_plus(query)}"
    )

    logger.info(f"Открываем поиск: {query}")

    try:
        encoded_query = quote_plus(query)

        def is_search_response(response):
            url = response.url

            return (
                response.status == 200
                and "/__internal/u-search/exactmatch/" in url
                and "/search?" in url
                and "resultset=catalog" in url
                and f"query={encoded_query}" in url
            )

        logger.info("Ждём ответ API...")

        async with page.expect_response(
            is_search_response,
            timeout=20000
        ) as response_info:

            await page.goto(
                search_url,
                wait_until="domcontentloaded",
                timeout=30000
            )

        response = await response_info.value

        logger.info("🔥 API пойман!"
        f"Статус: {response.status}"
        f"URL: {response.url}")

        body = await response.body()

        data = json.loads(body)

        logger.info(
            f"JSON получен: "
            f"{len(data.get('products', []))} товаров"
        )

        products = parse_products(data)

        logger.info(
            f"✅ Получено товаров: {len(products)}"
        )

        return products

    except Exception:
        logger.exception(f"Не удалось получить API")
        return []
