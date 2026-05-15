import os
import asyncio
import threading
import logging

from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# =====================
# CONFIG
# =====================
TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()


# =====================
# TELEGRAM HANDLERS
# =====================
@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Бот работает 🚀")


@dp.message()
async def echo(message: types.Message):
    await message.answer(message.text)


# =====================
# WEB SERVER (Render ping)
# =====================
async def handle(request):
    return web.Response(text="OK")


def run_web_server():
    app = web.Application()
    app.router.add_get("/", handle)

    port = int(os.environ.get("PORT", 10000))
    web.run_app(app, host="0.0.0.0", port=port)


# =====================
# BOT RUNNER
# =====================
async def run_bot():
    # ВАЖНО: только ОДИН polling процесс
    await dp.start_polling(bot)


# =====================
# MAIN
# =====================
if __name__ == "__main__":

    # Web server в отдельном потоке
    web_thread = threading.Thread(target=run_web_server, daemon=True)
    web_thread.start()

    # Bot polling в основном потоке
    asyncio.run(run_bot())

# ---------------- PLAYWRIGHT ----------------

async def get_browser(p):
    return await p.chromium.launch(
        headless=True,
        args=[
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu"
        ]
    )


# ---------------- PARSERS ----------------

async def parse_avito():
    url = "https://www.avito.ru/moskva/avtomobili"
    results = []

    try:
        async with async_playwright() as p:
            browser = await get_browser(p)
            page = await browser.new_page()

            await page.goto(url, timeout=60000)
            await page.wait_for_timeout(4000)

            cards = await page.query_selector_all("div[data-marker='item']")

            for card in cards[:10]:
                try:
                    title = await card.inner_text()
                    link = await card.query_selector("a")

                    if not link:
                        continue

                    href = await link.get_attribute("href")
                    if not href:
                        continue

                    if href.startswith("/"):
                        href = "https://www.avito.ru" + href

                    results.append({
                        "source": "Avito",
                        "title": title[:120],
                        "price": "—",
                        "url": href
                    })
                except:
                    continue

            await browser.close()

    except Exception as e:
        logging.error(f"Avito error: {e}")

    return results


async def parse_drom():
    url = "https://auto.drom.ru/moskva/"
    results = []

    try:
        async with async_playwright() as p:
            browser = await get_browser(p)
            page = await browser.new_page()

            await page.goto(url, timeout=60000)
            await page.wait_for_timeout(4000)

            cards = await page.query_selector_all("a[data-ftid='bulls-list_bull']")

            for card in cards[:10]:
                try:
                    title = await card.inner_text()
                    href = await card.get_attribute("href")

                    if not href:
                        continue

                    if href.startswith("/"):
                        href = "https://auto.drom.ru" + href

                    results.append({
                        "source": "Drom",
                        "title": title[:120],
                        "price": "—",
                        "url": href
                    })
                except:
                    continue

            await browser.close()

    except Exception as e:
        logging.error(f"Drom error: {e}")

    return results


# ---------------- MONITOR ----------------

async def monitor():
    await asyncio.sleep(5)

    while True:
        try:
            items = await parse_avito() + await parse_drom()
            logging.info(f"Found items: {len(items)}")

            for item in items:
                if item["url"] in sent_cache:
                    continue

                sent_cache.add(item["url"])

                text = (
                    f"🚗 {item['source']}\n\n"
                    f"📌 {item['title']}\n"
                    f"💰 {item['price']}\n"
                    f"🔗 {item['url']}"
                )

                if CHANNEL_ID:
                    await bot.send_message(CHANNEL_ID, text)

            await asyncio.sleep(random.randint(120, 300))

        except Exception as e:
            logging.error(f"Monitor error: {e}")
            await asyncio.sleep(10)


# ---------------- MAIN ----------------

async def main():
    await bot.delete_webhook(drop_pending_updates=True)

    await asyncio.gather(
        run_web_server(),
        monitor(),
        dp.start_polling(bot)
    )


if __name__ == "__main__":
    asyncio.run(main())
