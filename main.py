import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiohttp_socks import ProxyConnector

from config import TOKEN

proxy_url = "socks5://SGmGga:EbPsjy@45.91.209.146:10230"

async def main():
    connector = ProxyConnector.from_url(proxy_url)

    session = AiohttpSession(
        connector=connector
    )

    bot = Bot(token=TOKEN, session=session)
    dp = Dispatcher()

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
