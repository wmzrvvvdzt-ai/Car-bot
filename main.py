import asyncio
import os
import logging
import random
from threading import Thread
from http.server import BaseHTTPRequestHandler, HTTPServer

import aiohttp
from bs4 import BeautifulSoup
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

if not TOKEN:
    raise RuntimeError("❌ BOT_TOKEN не найден")

bot = Bot(token=TOKEN)
dp = Dispatcher()


# ---------------- TELEGRAM ----------------

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer("🚗 Бот мониторит Avito + Drom и ищет объявления")


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


# ---------------- HTTP ----------------

async def fetch(session, url):
    try:
        async with session.get(url, timeout=15) as resp:
            return await resp.text()
    except Exception as e:
        logging.error(f"Fetch error {url}: {e}")
        return None


# ---------------- AVITO ----------------

async def parse_avito():
    url = "https://www.avito.ru/moskva/avtomobili"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    async with aiohttp.ClientSession(headers=headers) as session:
        html = await fetch(session, url)

    if not html:
        return []

    soup = BeautifulSoup(html, "lxml")

    items = soup.select("div[data-marker='item']")

    results = []

    for item in items[:10]:
        try:
            title = item.get_text(" ", strip=True)

            a = item.find("a", href=True)
            if not a:
                continue

            link = "https://www.avito.ru" + a["href"]

            results.append({
                "source": "Avito",
                "title": title[:120],
                "price": "—",
                "url": link
            })

        except:
            continue

    return results


# ---------------- DROM ----------------

async def parse_drom():
    url = "https://auto.drom.ru/moskva/"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    async with aiohttp.ClientSession(headers=headers) as session:
        html = await fetch(session, url)

    if not html:
        return []

    soup = BeautifulSoup(html, "lxml")

    items = soup.select("a[data-ftid='bulls-list_bull']")

    results = []

    for item in items[:10]:
        try:
            title = item.get_text(strip=True)
            link = item.get("href")

            if not link:
                continue

            results.append({
                "source": "Drom",
                "title": title[:120],
                "price": "—",
                "url": link
            })

        except:
            continue

    return results


# ---------------- CACHE ----------------

sent_cache = set()


# ---------------- MONITOR ----------------

async def monitor():
    await asyncio.sleep(5)

    while True:
        try:
            avito = await parse_avito()
            drom = await parse_drom()

            all_items = avito + drom

            logging.info(f"Found items: {len(all_items)}")

            for item in all_items:
                key = item["url"]

                if key in sent_cache:
                    continue

                sent_cache.add(key)

                text = (
                    f"🚗 {item['source']}\n\n"
                    f"📌 {item['title']}\n"
                    f"💰 {item['price']}\n"
                    f"🔗 {item['url']}"
                )

                if CHANNEL_ID:
                    await bot.send_message(CHANNEL_ID, text)

                logging.info("Sent deal to channel")

            await asyncio.sleep(random.randint(120, 300))

        except Exception as e:
            logging.error(f"Monitor error: {e}")
            await asyncio.sleep(10)


# ---------------- BOT LOOP ----------------

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
