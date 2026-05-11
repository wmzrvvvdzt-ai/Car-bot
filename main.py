from aiohttp import TCPConnector
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram import Bot, Dispatcher
import asyncio

TOKEN = "8590083060:AAHzISyE09bEMp-m5HDJs-BoILHCL456cCA"

async def main():
    session = AiohttpSession(
        connector=TCPConnector(
            force_close=True,
            ssl=False
        )
    )

    bot = Bot(token=TOKEN, session=session)
    dp = Dispatcher()

    print("Bot started...")

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
