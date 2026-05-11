import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiohttp_socks import ProxyConnector

from config import TOKEN, CHAT_ID, MIN_DISCOUNT
from handlers.start import router


async def main():
    connector = ProxyConnector.from_url(PROXY)
    session = AiohttpSession(connector=connector)

    bot = Bot(token=TOKEN, session=session)
    dp = Dispatcher()

    dp.include_router(router)

    print("Bot started...")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
