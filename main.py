import asyncio
import os
import logging
import random
from threading import Thread
from http.server import BaseHTTPRequestHandler, HTTPServer

import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")  # @avtoradar_ru например

if not TOKEN:
    raise RuntimeError("❌ BOT_TOKEN не найден")

bot = Bot(token=TOKEN)
dp = Dispatcher()


# ---------------- TELEGRAM ----------------

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer("🚗 Бот работает и мониторит объявления")


# ---------------- WEB SERVER (Render) ----------------

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running")

    def log_message(self, format, *args):
        return


def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()


# ---------------- PARSERS (ЗАГОТОВКА) ----------------

async def fetch(session, url):
    try:
        async with session.get(url, timeout=10) as resp:
            return await resp.text()
    except Exception as e:
        logging.error(f"Fetch error {url}: {e}")
        return None


async def parse_avito():
    """
    ВАЖНО: это упрощённый пример.
    Реальные селекторы нужно подбирать под HTML.
    """
    url = "https://www.avito.ru/moskva/avtomobili"
    async with aiohttp.ClientSession() as session:
        html = await fetch(session, url)
        if not html:
            return []

        # заглушка (реально тут нужен BeautifulSoup / lxml)
        if "авто" in html.lower():
            return [{
                "title": "Возможное объявление с Avito",
                "price": "—",
                "url": url
            }]
    return []


async def parse_drom():
    url = "https://auto.drom.ru/"
    async with aiohttp.ClientSession() as session:
        html = await fetch(session, url)
        if not html:
            return []

        if "drom" in html.lower():
            return [{
                "title": "Возможное объявление с Drom",
                "price": "—",
                "url": url
            }]
    return []


# ---------------- MONITOR LOOP ----------------

sent_cache = set()


async def monitor():
    await asyncio.sleep(10)

    while True:
        try:
            avito = await parse_avito()
            drom = await parse_drom()

            all_items = avito + drom

            for item in all_items:
                key = item["url"] + item["title"]

                if key in sent_cache:
                    continue

                sent_cache.add(key)

                text = (
                    f"🚗 Новое предложение\n\n"
                    f"📌 {item['title']}\n"
                    f"💰 {item['price']}\n"
                    f"🔗 {item['url']}"
                )

                if CHANNEL_ID:
                    await bot.send_message(CHANNEL_ID, text)

                logging.info("Sent deal to channel")

            await asyncio.sleep(random.randint(120, 300))  # анти-бан

        except Exception as e:
            logging.error(f"Monitor error: {e}")
            await asyncio.sleep(10)


# ---------------- MAIN ----------------

async def run_bot():
    asyncio.create_task(monitor())

    while True:
        try:
            await dp.start_polling(bot)
        except Exception as e:
            logging.error(f"Bot crashed: {e}")
            await asyncio.sleep(5)


async def main():
    Thread(target=run_web_server, daemon=True).start()
    await run_bot()


if __name__ == "__main__":
    asyncio.run(main())
