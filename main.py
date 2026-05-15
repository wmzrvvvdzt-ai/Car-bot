import asyncio
import os
import logging
import random

from aiohttp import web
from playwright.async_api import async_playwright

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

bot = Bot(token=TOKEN)
dp = Dispatcher()

sent_cache = set()


# ---------------- TELEGRAM ----------------

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer("🚗 Бот работает и мониторит объявления")


# ---------------- WEB SERVER (Render FIX) ----------------

async def handle(request):
    return web.Response(text="Bot is running")


async def run_web_server():
    app = web.Application()
    app.router.add_get("/", handle)

    port = int(os.environ.get("PORT", 10000))
    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

    logging.info(f"Web server started on port {port}")


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
